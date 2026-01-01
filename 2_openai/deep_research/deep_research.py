import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)


async def run(query: str):
    async for chunk in ResearchManager().run(query):
        yield chunk


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    query_textbox = gr.Textbox(label="What topic would you like to research?")
    run_button = gr.Button("Run", variant="primary")
    gr.Markdown("# Output:")
    report = gr.HTML(label="Report")
    
    run_button.click(fn=run, inputs=query_textbox, outputs=report, concurrency_limit=5)
    query_textbox.submit(fn=run, inputs=query_textbox, outputs=report, concurrency_limit=5)

# 2. Enable queuing and set max_threads in launch
if __name__ == "__main__":
    ui.queue().launch(
        inbrowser=True,
        max_threads=40  # Allows the underlying server to handle more simultaneous connections
    )

