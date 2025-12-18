import gradio as gr
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

# 1. Configuration
# Use the RAW urls (click "Raw" on a GitHub file to get this link)
DOC_URLS = [
    "https://raw.githubusercontent.com/username/repo/main/docs/intro.md",
    "https://raw.githubusercontent.com/username/repo/main/docs/api.md"
]

ollama_client = OpenAI(api_key='ollama', base_url="http://localhost:11434/v1")
ollama_model = "llama3.2"

# 2. The Fetch Function
def fetch_docs_on_start():
    """
    This runs ONLY when a new user opens the page (or refreshes).
    """
    print("--- NEW SESSION: Fetching fresh docs from GitHub... ---")
    combined_text = ""
    try:
        for url in DOC_URLS:
            resp = requests.get(url)
            if resp.status_code == 200:
                combined_text += f"\n\n=== FILE: {url.split('/')[-1]} ===\n"
                combined_text += resp.text
            else:
                combined_text += f"\n\n[Error fetching {url}]\n"
    except Exception as e:
        combined_text += f"\n[System Error: {e}]\n"
    
    return combined_text

# 3. The Chat Function
# Notice the extra argument: 'doc_context'
def chat(message, history, doc_context):
    
    # We use the 'doc_context' that was passed in from the State
    system_prompt = f"""
    You are a technical support assistant.
    Answer questions using the documentation provided below.
    
    ## LIVE DOCUMENTATION CONTEXT:
    {doc_context}
    """
    
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    
    response = ollama_client.chat.completions.create(
        model=ollama_model, 
        messages=messages
    )
    return response.choices[0].message.content

# 4. Building the App
with gr.Blocks() as demo:
    # A. Define the State
    # Setting value=fetch_docs_on_start means "Run this function when app loads"
    # The result is stored in 'repo_state'
    repo_state = gr.State(value=fetch_docs_on_start)

    # B. The Chat Interface
    # We pass 'repo_state' into 'additional_inputs'.
    # This automatically feeds the stored docs into the chat function as the 3rd argument.
    gr.ChatInterface(
        fn=chat,
        type="messages",
        additional_inputs=[repo_state], 
        title="GitHub Docs Bot",
        description="I fetched the docs when you opened this page."
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=1234)