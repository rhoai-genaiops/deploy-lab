# Gradio App

A collection of Gradio-based demo interfaces for exploring LLM capabilities.

## Interfaces

| Path | Description |
|------|-------------|
| `/chat-interface` | Simple chat interface for LLM interaction |
| `/prompt-playground` | Advanced prompt testing with system/user prompts and history |
| `/context-demo` | Demonstrates context window and token limits |
| `/max-length-demo` | Shows how max tokens affects response length |
| `/optimization` | Side-by-side model comparison with response timing |

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

The app runs on port 7860.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_URL` | Base URL for the LLM API | `http://localhost:8080` |
| `MODEL_NAME` | Model name for API requests | `llama32` |
| `COMPRESSED_MODEL_URL` | URL for second model (optimization) | `http://localhost:8081` |
| `COMPRESSED_MODEL_NAME` | Name for second model | `llama32-fp8` |

## Building Container

```bash
podman build -t gradio-app -f Containerfile .
podman run -p 7860:7860 gradio-app
```
