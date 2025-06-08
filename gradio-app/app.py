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

def format_history(history):
    if not history:
        return "No prompts history yet."
    
    formatted = []
    for i, entry in enumerate(history, 1):
        formatted.append(f"**{i}. System prompt:**")
        formatted.append(f"{entry['system_prompt']}")
        formatted.append(f"**User prompt:**")
        formatted.append(f"{entry['user_prompt']}")
        formatted.append("")  # Empty line for spacing
    
    return "\n".join(formatted)

def clear_history():
    return [], "No prompts history yet."

def load_from_history(history_text, evt: gr.SelectData):
    # This function would be called when clicking on history
    # For now, we'll just return the current values
    return gr.update(), gr.update(), gr.update(), gr.update()

with gr.Blocks(title="Play with Prompts", theme=gr.themes.Default()) as demo:
    gr.Markdown("# 🤖 Play with Prompts")
    gr.Markdown("Enter your model URL, system prompt, and user prompt to get AI responses. Your conversation history is shown on the right.")

    # State to hold conversation history
    history_state = gr.State([])

    with gr.Row(equal_height=False):
        with gr.Column(scale=2):
            with gr.Row():
                with gr.Column(scale=2):
                    model_name = gr.Textbox(label="Model Name", placeholder="tinyllama")
                    model_url = gr.Textbox(label="Model API URL", placeholder="https://api.example.com/v1/chat/completions")
                    system_prompt = gr.Textbox(label="System Prompt", value="You are a helpful assistant.", lines=3)
                    user_prompt = gr.Textbox(label="User Prompt", placeholder="Enter your question...", lines=3)
                    
                    with gr.Row():
                        max_tokens = gr.Slider(label="Max Tokens", minimum=10, maximum=2048, value=100, step=10)
                        temperature = gr.Slider(label="Temperature", minimum=0.0, maximum=1.0, value=0.7, step=0.1)
                    
                    with gr.Row():
                        submit_btn = gr.Button("Send", variant="primary", scale=2)
                        clear_btn = gr.Button("Clear History", variant="secondary", scale=1)

                with gr.Column(scale=2):
                    output = gr.Textbox(
                        label="AI Response",
                        lines=20,
                        max_lines=30,
                        interactive=False,
                        placeholder="AI response will appear here...",
                        show_copy_button=True
                    )

        with gr.Column(scale=1):
            history_display = gr.Markdown(
                label="Prompts History",
                value="No prompts history yet.",
                elem_classes=["history-panel"]
            )

    # Event handlers
    def add_to_history_and_chat(history, model_name, model_url, system_prompt, user_prompt, max_tokens, temperature):
        # Add to history first
        new_entry = {
            "system_prompt": system_prompt or "You are a helpful assistant.",
            "user_prompt": user_prompt
        }
        updated_history = history + [new_entry]
        
        # Return updated history display
        history_display_text = format_history(updated_history)
        
        return updated_history, history_display_text

    submit_btn.click(
        fn=add_to_history_and_chat,
        inputs=[history_state, model_name, model_url, system_prompt, user_prompt, max_tokens, temperature],
        outputs=[history_state, history_display]
    ).then(
        fn=chat_with_model_stream,
        inputs=[model_name, model_url, system_prompt, user_prompt, max_tokens, temperature],
        outputs=[output]
    )

    user_prompt.submit(
        fn=add_to_history_and_chat,
        inputs=[history_state, model_name, model_url, system_prompt, user_prompt, max_tokens, temperature],
        outputs=[history_state, history_display]
    ).then(
        fn=chat_with_model_stream,
        inputs=[model_name, model_url, system_prompt, user_prompt, max_tokens, temperature],
        outputs=[output]
    )

    clear_btn.click(
        fn=clear_history,
        outputs=[history_state, history_display]
    )

    # Add custom CSS for better history panel styling
    demo.css = """
    .history-panel {
        max-height: 600px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid var(--border-color-primary);
        border-radius: 5px;
        font-size: 12px;
    }
    """

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)