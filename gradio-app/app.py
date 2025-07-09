import gradio as gr
from apps.chat_interface import create_chat_interface
from apps.prompt_playground import create_prompt_playground
from apps.context_demo import create_context_demo
from apps.max_length_demo import create_max_length_demo
from fastapi import FastAPI

# Create FastAPI app
app = FastAPI()

# Create Gradio apps
chat_app = create_chat_interface()
prompt_app = create_prompt_playground()
context_app = create_context_demo()
max_length_app = create_max_length_demo()

# Mount the Gradio apps at different paths
app = gr.mount_gradio_app(app, chat_app, path="/chat-interface")
app = gr.mount_gradio_app(app, prompt_app, path="/prompt-playground")
app = gr.mount_gradio_app(app, context_app, path="/context-demo")
app = gr.mount_gradio_app(app, max_length_app, path="/max-length-demo")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)