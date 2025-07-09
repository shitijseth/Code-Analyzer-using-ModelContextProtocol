
<body>
  <h1>MCP Code Analyzer Setup &amp; Run Instructions</h1>
  <p>
    This project demonstrates an MCP (Model Context Protocol) server that integrates
    an open-source LLM (GPT-J 6B) to analyze a GitHub repository’s code and answer
    questions about it.
  </p>
  
  <h2>Prerequisites</h2>
  <ul>
    <li>Python 3.10 or higher installed on your system.</li>
    <li>Git to clone the repository.</li>
  </ul>
  
  <h2>Step 1: Clone the Repository</h2>
  <pre>
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
  </pre>
  
  <h2>Step 2: Create and Activate a Virtual Environment</h2>
  <p>It’s recommended to use a virtual environment for this project:</p>
  <pre>
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS/Linux:
python3 -m venv venv
source venv/bin/activate
  </pre>
  
  <h2>Step 3: Install Dependencies</h2>
  <p>Install all required packages using the provided <code>requirements.txt</code> file:</p>
  <pre>
pip install -r requirements.txt
  </pre>
  
  <h2>Step 4: Run the MCP Server</h2>
  <p>In one terminal, start the MCP server:</p>
  <pre>
# Example using the default open-source model:
python mcp_server.py

# To use ChatGPT or Claude, set the following environment variables first:
#   LLM_CHOICE=chatgpt  # or "claude"
#   OPENAI_API_KEY=your-openai-key      # required for ChatGPT
#   ANTHROPIC_API_KEY=your-anthropic-key  # required for Claude
python mcp_server.py
  </pre>
  <p>You should see a message indicating that the server has started (e.g., “Starting MCP server on port 5000...”).</p>
  
  <h2>Step 5: Run the MCP Client</h2>
  <p>Open another terminal (or tab) with the same virtual environment activated, then run:</p>
  <pre>
python mcp_client.py
  </pre>
  <p>The client will connect to the server, analyze the GitHub repo, and query the LLM for an answer.</p>
  
  <h2>Troubleshooting</h2>
  <ul>
    <li><strong>Python Version Errors:</strong> Make sure you’re on Python 3.10 or higher.</li>
    <li><strong>Virtual Environment Issues:</strong> Double-check that your environment is activated before installing or running.</li>
    <li><strong>LLM Loading Problems:</strong> The default CodeLlama model may require significant resources. You can switch models by setting <code>LLM_CHOICE</code> to <code>chatgpt</code> or <code>claude</code> if you have the appropriate API keys.</li>
  </ul>
  
  <hr>
  <p>&copy; 2023 Your Name or Organization</p>
</body>
</html>
