"""Chatbot application for Ehsan Masnavi's resume and profile.

This module creates a Gradio-based chat interface that allows users to interact
with an AI assistant representing Ehsan Masnavi, answering questions about his
career, background, skills, and experience based on his profile summary and
LinkedIn profile.
"""
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr



load_dotenv(override=True)

script_dir = Path(__file__).parent
pdf_path = script_dir / "me" / "Profile.pdf"
summary_path = script_dir / "me" / "ProfileSummary.txt"


reader = PdfReader(pdf_path)

linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text
        
with open(summary_path, "r", encoding="utf-8") as f:
    summary = f.read()
        
name = "Ehsan Masnavi"
system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If the question is unrelated to {name}'s professional backgroud, say no. Alos if you don't know the answer, say so."

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

ollama_client = OpenAI(api_key='ollama', base_url="http://99.251.9.3:11434/v1")
ollama_model = "llama3.2"


def chat(message, history):
    """Process a chat message and return the AI response.
    
    Args:
        message: The user's message string.
        history: List of previous message dictionaries with 'role' and 'content' keys.
    
    Returns:
        The AI's response content as a string.
    """
    print(history)
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = ollama_client.chat.completions.create(model=ollama_model, messages=messages)
    return response.choices[0].message.content


demo = gr.ChatInterface(
    fn=chat, 
    type="messages",
    title="Ehsan Masnavi's resume chat bot",
    description="Running locally on localhost:1234"
)

if __name__ == "__main__":
    # server_name="127.0.0.1" ensures it is only accessible on YOUR computer
    demo.launch(server_name="127.0.0.1", server_port=1234, share=False)