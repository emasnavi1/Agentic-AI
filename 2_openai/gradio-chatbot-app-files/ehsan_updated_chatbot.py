"""Chatbot application for Ethan Masnavi's resume and profile.

This module creates a Gradio-based chat interface that allows users to interact
with an AI assistant representing Ethan Masnavi, answering questions about his
career, background, skills, and experience based on his profile summary and
LinkedIn profile.
"""
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import json
import os
import requests
import gradio as gr
from pathlib import Path
import asyncio


load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
openai_vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

script_dir = Path(__file__).parent
pdf_path = script_dir / "me" / "Profile.pdf"
summary_path = script_dir / "me" / "ProfileSummary.txt"

        
name = "Ethan Masnavi"

system_prompt = f"""
You are acting as {name}, representing {name} on their personal website.

Your role:
- Answer questions about {name}'s career, background, skills, experience, and professional interests.
- Communicate professionally and confidently, as if speaking with a potential client, recruiter, or employer.

Knowledge sourcing rules (STRICT):
1. For every factual question, FIRST attempt to answer using the `vector_store_tool`.
2. If the `vector_store_tool`:
   - does not return relevant information, OR
   - explicitly indicates that specific information cannot be found,
   THEN you MUST call `record_unknown_question` before providing any response.
3. If the information cannot be found via `vector_store_tool`, DO NOT guess or improvise an answer.

Tool transparency rules:
- Do NOT mention files, documents, embeddings, or tools in your responses.
- Do NOT ask the user whether you should look up information.
- The user should never be aware of internal data retrieval.
- Do not make any suggestion such as "If you have any specific questions about the uploaded files let me know".

Conversation and lead-generation behavior:
- If the user engages in discussion, shows interest, or asks open-ended questions,
  gently encourage them to get in touch.
- Ask for their name and email in a natural, professional manner.
- When provided, store these details using the `record_user_details` tool.

Fallback behavior:
- If a question cannot be answered using available knowledge,
  record it with `record_unknown_question` and respond with a brief,
  professional message indicating that the information is not currently available.
  
Unknown-question logging (MANDATORY):
- A question is considered UNKNOWN if the `vector_store_tool` does not return
  explicit, relevant information that directly answers the question.
- For EVERY UNKNOWN question, without exception you MUST:
  1. Call `record_unknown_question` with the full user question.
  2. Do NOT answer the question in any form.
  3. Do NOT speculate, summarize, or provide partial information.
- There are NO exceptions to this rule, even for:
  - trivial questions
  - casual conversation
  - quetions unrelated to the professional background
  - personal questions
  - hypothetical or exploratory questions
  - questions unrelated to {name}'s career or background
  - Questions that are repeated several time
  
  ABSOLUTE PROHIBITION (NON-NEGOTIABLE):
- You are FORBIDDEN from mentioning or implying the existence of:
  files, uploads, documents, data sources, vector stores, embeddings,
  internal context, prior inputs, or system-provided information.
- This includes generic phrases such as:
  “files you uploaded”, “information you provided”, “documents”,
  “based on what I have”, or similar wording.
- If you generate a response that contains any such reference,
  you MUST immediately rephrase it to remove the reference
  before finalizing the answer.
"""

openAI_client = AsyncOpenAI(api_key=openai_api_key)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

# We wrap the blocking requests call so it doesn't hang the event loop
async def push(message):
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    # This runs the blocking request in a separate thread
    await asyncio.to_thread(requests.post, pushover_url, data=payload)

def record_user_details(email, name="Name not provided", notes="not provided"):
    """ Record a user detail """
    asyncio.create_task(push(f"Recording interest from {name} with email {email} and notes {notes}"))
    return {"recorded": "ok"}

def record_unknown_question(question):
    """ Record an unknown request """
    asyncio.create_task(push(f"Recording {question} asked that I couldn't answer"))
    return {"recorded": "ok"}


def handle_tool_calls(tool_calls):
    results = []
    for item in tool_calls:
        if item.type == "function_call":
            arguments = json.loads(item.arguments)
            if item.name == "record_unknown_question":
                result = record_unknown_question(**arguments)
            
            elif item.name == "record_user_details":
                result = record_user_details(**arguments) 
            
            else:
                result = {"error": "function not found"}
            
            results.append({"type": "function_call_output", "call_id": item.call_id ,"output": json.dumps(result)})
            
    return results


# Define tool JSON schemas for OpenAI API
record_user_details_tool = {
    "type": "function",
    "name": "record_user_details",
    "description": "records a user's name and email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "[The email address of the user]"
            },
            "name": {
                "type": "string",
                "description": "The user's name",
                "default": "[Name of the user]"
            },
            "notes": {
                "type": "string",
                "description": "Any additional notes",
                "default": "not provided"
            }
        },
        "required": ["email", "name"],
        "additionalProperties": False
    }
}

record_unknown_question_tool = {
    "type": "function",
    "name": "record_unknown_question", 
    "description": "records a question to which the LLM could not find an answer to",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            }
        },
        "required": ["question"],
        "additionalProperties": False
    } 
}

vector_store_tool = {
    "type": "file_search", 
    "vector_store_ids": [f"{openai_vector_store_id}"]
}

tools = [
    record_user_details_tool,
    record_unknown_question_tool,
    vector_store_tool
]


async def chat(message, history):
    
    messages = [
        {"role": h["role"], "content": h["content"]} 
        for h in history
    ]
    
    messages.append({"role": "user", "content": message})
        
    done = False
    answer = ""
    
    while not done:
        
        response = await openAI_client.responses.create(
            model="gpt-4o-mini",
            input = messages,
            tools = tools,
            instructions= system_prompt
        )
        
        # 1. Add the assistant's response (calls and messages) to history exactly ONCE
        messages.extend(response.output)
        
        # Check exactly what type of items we got back
        has_function = any(item.type == "function_call" for item in response.output)
        # has_message = any(item.type == "message" for item in response.output)

        # 1. If there is a message, we treat it as the final answer
        # UNLESS there is also a function we must execute first.
        # if has_message:
        for item in response.output:
            if item.type == "message":
                if not has_function:
                    answer = item.content[0].text
                    done = True
                    break
                else:
                    # print(f"Intermediate message before function: {item.content[0].text}")
                    pass

        # 2. If we aren't done, process functions and loop again.
        # Note: If it was ONLY a file_search (no message yet), we naturally loop 
        # again because done is still False.
        if not done and has_function:
            results = handle_tool_calls(response.output)
            if results:
                messages.extend(results)
    
    return answer


demo = gr.ChatInterface(
    fn=chat, 
    type="messages",
    title="Ethan Masnavi's chat bot",
    description="Ask me about Ethan's background and experience.",
    concurrency_limit=20
)

if __name__ == "__main__":
    demo.queue().launch(
        max_threads=40, # Standard thread pool size
        show_api=False
    )