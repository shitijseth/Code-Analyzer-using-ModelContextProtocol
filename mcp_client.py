# mcp_client.py

from mcp.client import McpClient

def main():
    # Initialize the MCP client with the server URL.
    client = McpClient(server_url="http://localhost:5000")
    
    # Example: Analyze a GitHub repository.
    owner = "shitijseth"           # Replace with actual repository owner.
    repo = "3D-Solar-System-Simulator"        # Replace with actual repository name.
    analysis_response = client.call('analyze_repo', {'owner': owner, 'repo': repo})
    print("Repository Analysis:")
    print(analysis_response)
    
    # Example: Ask a specific question about the repository.
    question = "What improvements can be made to the overall code structure?"
    question_response = client.call('ask_repo_question', {
        'owner': owner,
        'repo': repo,
        'question': question
    })
    print("\nAnswer to your question:")
    print(question_response)

if __name__ == "__main__":
    main()
