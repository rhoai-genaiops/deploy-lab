import gradio as gr
import requests
import json
import os

# Get base model URL from environment variable
BASE_URL = os.getenv('MODEL_URL', 'http://localhost:8080')
# Get model name from environment variable
MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')

def chat_with_model_stream(message, max_tokens=30):
    if not message:
        yield "Please provide a message."
        return
    
    try:
        # Append /chat/completions to the base URL
        model_url = f"{BASE_URL.rstrip('/')}/v1/chat/completions"
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": message}
            ],
            "stream": True,
            "max_tokens": max_tokens
        }

        headers = {
            "Content-Type": "application/json",
        }

        with requests.post(model_url, json=payload, headers=headers, stream=True, timeout=30) as response:
            if response.status_code != 200:
                yield f"Error {response.status_code}: {response.text}"
                return

            partial = ""
            for line in response.iter_lines(decode_unicode=True):
                if line.strip() == "" or not line.startswith("data: "):
                    continue
                data = line[len("data: "):]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    partial += delta
                    yield partial
                except json.JSONDecodeError:
                    continue
                    
    except requests.exceptions.Timeout:
        yield "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        yield f"Request failed: {str(e)}"
    except Exception as e:
        yield f"An error occurred: {str(e)}"

def create_context_demo():
    with gr.Blocks() as interface:
        with gr.Column():
            gr.Markdown(
                """# Limited Context Demo""",
                elem_classes="contain"
            )
            
            chatbot = gr.Chatbot(
                label="Chat History",
                elem_id="chatbot",
                height=400
            )

            msg = gr.Textbox(
                label="Message",
                placeholder="Try asking: 'Write a detailed explanation of how neural networks work'",
                container=False,
                lines=2,
                elem_classes="contain",
                autofocus=True
            )

            max_tokens_slider = gr.Slider(
                minimum=1,
                maximum=500,
                value=30,
                step=1,
                label="Max Tokens",
                elem_classes="contain"
            )

            submit_btn = gr.Button("Send", variant="primary", elem_classes="contain")

            def user(message, history):
                return "", history + [[message, None]]

            def bot(history, max_tokens):
                if not history:
                    return history

                last_message = history[-1][0]
                history[-1][1] = ""

                for chunk in chat_with_model_stream(last_message, max_tokens):
                    history[-1][1] = chunk
                    yield history

            submit_event = msg.submit(user, [msg, chatbot], [msg, chatbot]).then(
                bot, [chatbot, max_tokens_slider], chatbot
            )
            submit_btn.click(fn=user, inputs=[msg, chatbot], outputs=[msg, chatbot]).then(
                bot, [chatbot, max_tokens_slider], chatbot
            )

    return interface