# mcp_server.py

from mcp.server import McpServer, McpHandler
import requests
from transformers import pipeline

# Load an open source LLM for text generation.
# We use GPT-J 6B; if GPU is available, it will use it; otherwise, it falls back to CPU.
try:
    llm = pipeline("text-generation", model="EleutherAI/gpt-j-6B", device=0)
except Exception as e:
    # Fallback to CPU if GPU is not available or model load fails.
    llm = pipeline("text-generation", model="EleutherAI/gpt-j-6B", device=-1)
print("LLM loaded successfully.")

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

        # Use GitHub API to fetch repository contents.
        url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Unable to fetch repository (Status code: {response.status_code})."

        contents = response.json()
        analysis_results = []
        for item in contents:
            # Check for Python files for a simple analysis.
            if item['type'] == 'file' and item['name'].endswith('.py'):
                analysis_results.append(
                    f"File '{item['name']}' might benefit from improved error handling and better comments."
                )
        if not analysis_results:
            analysis_results.append("No Python files found for analysis.")
        return analysis_results

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

        # Fetch repository contents.
        url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Unable to fetch repository contents (Status code: {response.status_code})."
        
        contents = response.json()
        code_aggregate = ""
        # Iterate through each item to fetch code from Python files.
        for item in contents:
            if item['type'] == 'file' and item['name'].endswith('.py'):
                download_url = item.get('download_url')
                if download_url:
                    file_resp = requests.get(download_url)
                    if file_resp.status_code == 200:
                        code_aggregate += f"\n\n# File: {item['name']}\n"
                        code_aggregate += file_resp.text
                    else:
                        code_aggregate += f"\n\n# File: {item['name']} - Unable to fetch file content.\n"
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
            output = llm(prompt, max_length=500, do_sample=True, temperature=0.7)
            answer = output[0]['generated_text']
        except Exception as e:
            answer = f"LLM error: {str(e)}"
        return answer

if __name__ == "__main__":
    # Initialize and start the MCP server with our custom handler.
    server = McpServer(handler=MyMcpHandler())
    print("Starting MCP server on port 5000...")
    server.start(port=5000)
