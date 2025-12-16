import gradio as gr
import requests
import json
import os

# Get base model URL from environment variable
BASE_URL = os.getenv('MODEL_URL', 'http://localhost:8080')
# Get model name from environment variable
MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')

def chat_with_model_stream(message, temperature=0.7):
    if not message:
        yield "Please provide a message."
        return
    
    try:
        # Append /v1/chat/completions to the base URL
        model_url = f"{BASE_URL.rstrip('/')}/v1/chat/completions"
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": message}
            ],
            "temperature": float(temperature),
            "max_tokens": 2048,  # Default max tokens, can be adjusted
            "stream": True
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
                    # For chat endpoint, the response format uses delta.content
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

def create_chat_interface():
    with gr.Blocks() as interface:
        with gr.Column():
            gr.Markdown(
                f"Using Model URL: {BASE_URL}/v1/chat/completions",
                elem_classes="contain"
            )
            
            output = gr.Textbox(
                label="Response",
                lines=15,
                max_lines=25,
                interactive=False,
                placeholder="AI response will appear here...",
                elem_classes="contain"
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Prompt",
                    placeholder="Type your prompt here...",
                    container=False,
                    lines=3,
                    elem_classes="contain",
                    autofocus=True,
                    scale=4
                )
                temperature = gr.Slider(
                    label="Temperature",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    elem_classes="contain",
                    scale=1
                )
            
            submit_btn = gr.Button("Send", variant="primary", elem_classes="contain")

            def generate_response(prompt, temp):
                if not prompt:
                    return "Please enter a prompt."
                
                response = ""
                for chunk in chat_with_model_stream(prompt, temp):
                    response = chunk
                    yield response

            msg.submit(generate_response, [msg, temperature], output)
            submit_btn.click(generate_response, [msg, temperature], output)

    return interface