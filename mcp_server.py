# mcp_server.py

from mcp.server import McpServer, McpHandler
import os
import requests
import openai
import anthropic
from transformers import pipeline
from typing import List, Dict, Optional, Callable


def fetch_repo_files(
    owner: str, repo: str, path: str = "", session: Optional[requests.Session] = None
) -> List[Dict[str, str]]:
    """Recursively fetch all items in a GitHub repository path."""
    session = session or requests.Session()
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = session.get(url)
    if response.status_code != 200:
        return []

    items = response.json()
    files: List[Dict[str, str]] = []
    for item in items:
        if item.get("type") == "file":
            files.append(item)
        elif item.get("type") == "dir":
            files.extend(fetch_repo_files(owner, repo, item.get("path", ""), session))
    return files


def fetch_python_files(owner: str, repo: str, session: Optional[requests.Session] = None) -> List[Dict[str, str]]:
    """Return all Python files in the given repository."""
    return [
        item
        for item in fetch_repo_files(owner, repo, session=session)
        if item.get("name", "").endswith(".py")
    ]


def aggregate_python_code(
    files: List[Dict[str, str]], session: Optional[requests.Session] = None
) -> str:
    """Download and concatenate the contents of all provided Python files."""
    session = session or requests.Session()
    code_parts: List[str] = []
    for item in files:
        download_url = item.get("download_url")
        if not download_url:
            continue
        resp = session.get(download_url)
        if resp.status_code == 200:
            code_parts.append(f"\n\n# File: {item['path']}\n{resp.text}")
        else:
            code_parts.append(
                f"\n\n# File: {item['path']} - Unable to fetch file content.\n"
            )
    return "".join(code_parts)


def load_llm(choice: str) -> Callable:
    """Return a text-generation callable based on the selected LLM."""
    choice = choice.lower()
    if choice == "chatgpt":
        openai.api_key = os.getenv("OPENAI_API_KEY", "")

        def chatgpt(prompt: str, max_length: int = 500, temperature: float = 0.7):
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length,
                temperature=temperature,
            )
            return [{"generated_text": resp["choices"][0]["message"]["content"]}]

        return chatgpt
    if choice == "claude":
        client = anthropic.Client(os.getenv("ANTHROPIC_API_KEY", ""))

        def claude(prompt: str, max_length: int = 500, temperature: float = 0.7):
            resp = client.completions.create(
                model="claude-3-opus-20240229",
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                max_tokens=max_length,
                temperature=temperature,
            )
            return [{"generated_text": resp.completion}]

        return claude

    # Default to a coding-focused open-source model.
    model_id = "codellama/CodeLlama-7b-hf"
    try:
        return pipeline("text-generation", model=model_id, device=0)
    except Exception:
        return pipeline("text-generation", model=model_id, device=-1)


llm_choice = os.getenv("LLM_CHOICE", "codellama")
llm = load_llm(llm_choice)

class MyMcpHandler(McpHandler):
    def get_methods(self):
        """
        Return a dictionary mapping MCP method names to handler functions.
        """
        return {
            'analyze_repo': self.analyze_repo,
            'ask_repo_question': self.ask_repo_question,
        }

    def analyze_repo(self, params):
        """
        Analyze a GitHub repository for code improvements.
        Expected parameters:
            - 'owner': Repository owner (string)
            - 'repo': Repository name (string)
        Returns:
            A list of suggestions based on the repository's Python files.
        """
        owner = params.get('owner')
        repo = params.get('repo')
        if not owner or not repo:
            return "Error: Missing 'owner' or 'repo' parameters."

        session = requests.Session()
        py_files = fetch_python_files(owner, repo, session=session)
        if not py_files:
            return ["No Python files found for analysis."]
        return [
            f"File '{item['path']}' might benefit from improved error handling and better comments."
            for item in py_files
        ]

    def ask_repo_question(self, params):
        """
        Answer a specific question about the repository's code.
        Expected parameters:
            - 'owner': Repository owner (string)
            - 'repo': Repository name (string)
            - 'question': The user's question (string)
        Returns:
            An answer generated by the LLM after reading all the code.
        """
        owner = params.get('owner')
        repo = params.get('repo')
        question = params.get('question')
        if not owner or not repo or not question:
            return "Error: Missing one or more parameters: 'owner', 'repo', 'question'."

        session = requests.Session()
        py_files = fetch_python_files(owner, repo, session=session)
        code_aggregate = aggregate_python_code(py_files, session=session)
        if not code_aggregate:
            code_aggregate = "No Python files found in the repository."

        # Construct a prompt that includes the full code and the user's question.
        prompt = (
            f"Repository {owner}/{repo} code:\n"
            f"{code_aggregate}\n\n"
            f"Based on the code above, answer the following question: {question}\n"
            "Provide clear, detailed analysis and suggestions."
        )
        # Generate an answer using the LLM.
        try:
            output = llm(prompt, max_length=500, temperature=0.7)
            answer = output[0]['generated_text']
        except Exception as e:
            answer = f"LLM error: {str(e)}"
        return answer

if __name__ == "__main__":
    # Initialize and start the MCP server with our custom handler.
    server = McpServer(handler=MyMcpHandler())
    print("Starting MCP server on port 5000...")
    server.start(port=5000)
