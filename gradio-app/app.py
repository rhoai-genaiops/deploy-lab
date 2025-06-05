import gradio as gr
import requests
import json

def chat_with_model_stream(model_name, model_url, system_prompt, user_prompt, max_tokens, temperature):
    if not model_url or not user_prompt:
        yield "Please provide both model URL and user prompt."
        return
    
    try:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
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

with gr.Blocks(title="Play with Prompts") as demo:
    gr.Markdown("# 🤖 Play with Prompts")
    gr.Markdown("Enter your model URL, system prompt, and user prompt to get AI responses.")

    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            model_name = gr.Textbox(label="Model Name", placeholder="tinyllama")
            model_url = gr.Textbox(label="Model API URL", placeholder="https://api.example.com/v1/chat/completions")
            system_prompt = gr.Textbox(label="System Prompt", value="You are a helpful assistant.", lines=3)
            user_prompt = gr.Textbox(label="User Prompt", placeholder="Enter your question...", lines=3)
            max_tokens = gr.Slider(label="Max Tokens", minimum=10, maximum=2048, value=100, step=10)
            temperature = gr.Slider(label="Temperature", minimum=0.0, maximum=1.0, value=0.7, step=0.1)
            submit_btn = gr.Button("Send", variant="primary")

        with gr.Column(scale=1.5):
            output = gr.Textbox(
                label="AI Response",
                lines=18,
                max_lines=30,
                interactive=False,
                placeholder="AI response will appear here...",
                show_copy_button=True
            )

    submit_btn.click(
        fn=chat_with_model_stream,
        inputs=[model_name, model_url, system_prompt, user_prompt, max_tokens, temperature],
        outputs=output
    )

    user_prompt.submit(
        fn=chat_with_model_stream,
        inputs=[model_name, model_url, system_prompt, user_prompt, max_tokens, temperature],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
