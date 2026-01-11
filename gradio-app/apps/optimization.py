import gradio as gr
import requests
import json
import os
import threading
import time
from queue import Queue

# Default model URLs from environment
DEFAULT_MODEL_URL_1 = os.getenv('MODEL_URL', os.getenv('MODEL_URL', 'http://localhost:8080'))
DEFAULT_MODEL_URL_2 = os.getenv('COMPRESSED_MODEL_URL', 'http://localhost:8081')
DEFAULT_MODEL_NAME_1 = os.getenv('MODEL_NAME', os.getenv('MODEL_NAME', 'llama32'))
DEFAULT_MODEL_NAME_2 = os.getenv('COMPRESSED_MODEL_NAME', 'llama32-fp8')


def stream_from_model(model_name, model_url, prompt, temperature, max_tokens, queue, model_id, start_time):
    """Stream response from a model and put chunks in the queue."""
    try:
        url = f"{model_url.rstrip('/')}/v1/chat/completions"
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": True
        }
        headers = {"Content-Type": "application/json"}

        with requests.post(url, json=payload, headers=headers, stream=True, timeout=60) as response:
            if response.status_code != 200:
                elapsed = time.time() - start_time
                queue.put((model_id, f"Error {response.status_code}: {response.text}", True, elapsed))
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
                    elapsed = time.time() - start_time
                    queue.put((model_id, partial, False, elapsed))
                except json.JSONDecodeError:
                    continue

            elapsed = time.time() - start_time
            queue.put((model_id, partial, True, elapsed))

    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        queue.put((model_id, "Request timed out.", True, elapsed))
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start_time
        queue.put((model_id, f"Request failed: {str(e)}", True, elapsed))
    except Exception as e:
        elapsed = time.time() - start_time
        queue.put((model_id, f"Error: {str(e)}", True, elapsed))


def compare_models(prompt, model_name_1, model_url_1, model_name_2, model_url_2, temperature, max_tokens):
    """Send prompt to both models and yield results side by side."""
    if not prompt:
        yield "Please provide a prompt.", "Please provide a prompt.", "—", "—"
        return

    queue = Queue()
    response_1 = ""
    response_2 = ""
    done_1 = False
    done_2 = False
    time_1 = 0.0
    time_2 = 0.0

    # Headers to identify which model generated which response
    header_1 = f"[{model_name_1}]\n\n"
    header_2 = f"[{model_name_2}]\n\n"

    # Start time for both models
    start_time = time.time()

    # Start threads for both models
    thread_1 = threading.Thread(
        target=stream_from_model,
        args=(model_name_1, model_url_1, prompt, temperature, max_tokens, queue, 1, start_time)
    )
    thread_2 = threading.Thread(
        target=stream_from_model,
        args=(model_name_2, model_url_2, prompt, temperature, max_tokens, queue, 2, start_time)
    )

    thread_1.start()
    thread_2.start()

    # Collect results from both streams
    while not (done_1 and done_2):
        try:
            model_id, content, is_done, elapsed = queue.get(timeout=0.1)
            if model_id == 1:
                response_1 = content
                time_1 = elapsed
                done_1 = is_done
            else:
                response_2 = content
                time_2 = elapsed
                done_2 = is_done

            time_str_1 = f"{time_1:.2f}s" if time_1 > 0 else "..."
            time_str_2 = f"{time_2:.2f}s" if time_2 > 0 else "..."
            yield header_1 + response_1, header_2 + response_2, time_str_1, time_str_2
        except:
            # Check if threads are still alive
            if not thread_1.is_alive() and not done_1:
                done_1 = True
            if not thread_2.is_alive() and not done_2:
                done_2 = True
            time_str_1 = f"{time_1:.2f}s" if time_1 > 0 else "..."
            time_str_2 = f"{time_2:.2f}s" if time_2 > 0 else "..."
            yield header_1 + response_1, header_2 + response_2, time_str_1, time_str_2

    thread_1.join()
    thread_2.join()


def create_optimization_interface():
    with gr.Blocks(css="""
        @media (max-width: 768px) {
            .mobile-stack {
                flex-direction: column !important;
            }
            .mobile-stack > div {
                width: 100% !important;
                max-width: 100% !important;
            }
        }
    """) as interface:
        gr.Markdown("# Model Comparison")
        gr.Markdown("Send the same prompt to two different models and compare their responses side by side.")

        with gr.Row(elem_classes=["mobile-stack"]):
            with gr.Column(scale=1):
                gr.Markdown("### Model 1")
                model_name_1 = gr.Textbox(
                    label="Model Name",
                    value=DEFAULT_MODEL_NAME_1,
                    placeholder="e.g., llama32"
                )
                model_url_1 = gr.Textbox(
                    label="Model URL",
                    value=DEFAULT_MODEL_URL_1,
                    placeholder="e.g., http://model-server:8080"
                )

            with gr.Column(scale=1):
                gr.Markdown("### Model 2")
                model_name_2 = gr.Textbox(
                    label="Model Name",
                    value=DEFAULT_MODEL_NAME_2,
                    placeholder="e.g., mistral"
                )
                model_url_2 = gr.Textbox(
                    label="Model URL",
                    value=DEFAULT_MODEL_URL_2,
                    placeholder="e.g., http://model-server:8081"
                )

        with gr.Row():
            prompt = gr.Textbox(
                label="Prompt",
                placeholder="Enter your prompt here...",
                lines=3,
                scale=3
            )

        with gr.Row():
            temperature = gr.Slider(
                label="Temperature",
                minimum=0.0,
                maximum=1.0,
                value=0.7,
                step=0.1
            )
            max_tokens = gr.Slider(
                label="Max Tokens",
                minimum=50,
                maximum=2048,
                value=512,
                step=50
            )

        submit_btn = gr.Button("Compare Models", variant="primary")

        with gr.Row(elem_classes=["mobile-stack"]):
            with gr.Column(scale=1):
                time_1 = gr.Textbox(
                    label="Response Time",
                    value="—",
                    interactive=False,
                    max_lines=1
                )
                output_1 = gr.Textbox(
                    label="Model 1 Response",
                    lines=15,
                    max_lines=30,
                    interactive=False
                )

            with gr.Column(scale=1):
                time_2 = gr.Textbox(
                    label="Response Time",
                    value="—",
                    interactive=False,
                    max_lines=1
                )
                output_2 = gr.Textbox(
                    label="Model 2 Response",
                    lines=15,
                    max_lines=30,
                    interactive=False
                )

        submit_btn.click(
            fn=compare_models,
            inputs=[prompt, model_name_1, model_url_1, model_name_2, model_url_2, temperature, max_tokens],
            outputs=[output_1, output_2, time_1, time_2]
        )

        prompt.submit(
            fn=compare_models,
            inputs=[prompt, model_name_1, model_url_1, model_name_2, model_url_2, temperature, max_tokens],
            outputs=[output_1, output_2, time_1, time_2]
        )

    return interface
