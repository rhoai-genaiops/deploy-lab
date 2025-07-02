import gradio as gr
import requests
import json
import os

# Get base model URL from environment variable
BASE_URL = os.getenv('MODEL_URL', 'http://localhost:8080')

def chat_with_model_stream(message):
    if not message:
        yield "Please provide a message."
        return
    
    try:
        # Append /chat/completions to the base URL
        model_url = f"{BASE_URL.rstrip('/')}/chat/completions"
        
        payload = {
            "messages": [
                {"role": "user", "content": message}
            ],
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
    with gr.Blocks(css="""
        .gradio-container {width: 800px !important; margin: 0 !important;}
        .contain {max-width: 800px !important;}
        #chatbot {height: 400px !important;}
        .main {padding: 0 !important; margin: 0 !important;}
        .app {padding-left: 1rem !important;}
        /* Override default Enter key behavior */
        textarea {
            resize: none !important;
        }
    """) as interface:
        with gr.Column():
            gr.Markdown(
                f"Using Model URL: {BASE_URL}/chat/completions",
                elem_classes="contain"
            )
            
            chatbot = gr.Chatbot(
                label="Chat History",
                elem_id="chatbot",
                container=False,
                height=400,
                type="messages"  # Use new message format
            )
            
            msg = gr.Textbox(
                label="Message",
                placeholder="Type your message here...",
                container=False,
                lines=2,
                elem_classes="contain",
                autofocus=True
            )
            submit_btn = gr.Button("Send", variant="primary", elem_classes="contain")

            def user(message, history):
                return "", history + [{"role": "user", "content": message}]

            def bot(history):
                if not history:
                    return history
                
                last_message = history[-1]["content"]
                history.append({"role": "assistant", "content": ""})
                
                for chunk in chat_with_model_stream(last_message):
                    history[-1]["content"] = chunk
                    yield history

            submit_event = msg.submit(user, [msg, chatbot], [msg, chatbot]).then(
                bot, [chatbot], chatbot
            )
            submit_btn.click(fn=user, inputs=[msg, chatbot], outputs=[msg, chatbot]).then(
                bot, [chatbot], chatbot
            )

    return interface