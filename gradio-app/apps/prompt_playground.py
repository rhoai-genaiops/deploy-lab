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

def create_prompt_playground():
    with gr.Blocks() as interface:
        gr.Markdown("Enter your model URL, system prompt, and user prompt to get AI responses.")

        # State to hold conversation history
        history_state = gr.State([])

        with gr.Row():
            # Model Configuration Column
            with gr.Column(scale=1):
                model_name = gr.Textbox(label="Model Name", placeholder="tinyllama")
                model_url = gr.Textbox(label="Model API URL", placeholder="https://api.example.com/v1/chat/completions")
                system_prompt = gr.Textbox(label="System Prompt", value="Write me an exquisitely long poem about the following topic: ", lines=3)
                user_prompt = gr.Textbox(label="User Prompt", value="Making a cup of tea is easy. First, boil some water. Then, place a tea bag in a cup. Pour the hot water over the tea bag. Let it steep for a few minutes. After that, take out the tea bag. You can add sugar or milk if you like. Now the tea is ready to drink.", lines=3)

                max_tokens = gr.Slider(label="Max Tokens", minimum=10, maximum=2048, value=100, step=10)
                temperature = gr.Slider(label="Temperature", minimum=0.0, maximum=1.0, value=0.7, step=0.1)
                    
                with gr.Row():
                    submit_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear History", variant="secondary")

            # AI Response Column
            with gr.Column(scale=1):
                output = gr.Textbox(
                    label="AI Response",
                    lines=20,
                    max_lines=30,
                    interactive=False,
                    placeholder="AI response will appear here...",
                    show_copy_button=True
                )

            # History Column
            with gr.Column(scale=1):
                history_display = gr.Markdown(
                    label="Prompts History",
                    value="No prompts history yet.",
                    elem_classes=["history-panel"]
                )

            def add_to_history_and_chat(history, model_name, model_url, system_prompt, user_prompt, max_tokens, temperature):
                # Add to history first
                new_entry = {
                    "system_prompt": system_prompt or "Write me an exquisitely long poem about the following topic: ",
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
                outputs=output
            )

            clear_btn.click(
                fn=clear_history,
                outputs=[history_state, history_display]
            )

            # Add custom CSS for better history panel styling
            gr.Markdown("""
            <style>
            .history-panel {
                max-height: 800px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid var(--border-color-primary);
                border-radius: 5px;
                font-size: 12px;
            }
            /* Make columns have equal height */
            .gradio-container .row > div {
                min-height: 800px;
                display: flex;
                flex-direction: column;
            }
            /* Make the AI Response textbox expand to fill available space */
            .gradio-container .row > div:nth-child(2) textarea {
                height: 100% !important;
                min-height: 600px;
            }
            </style>
            """)

    return interface