# Exercise App

A FastAPI web portal serving as a landing page for AI orientation exercises.

## Overview

This app provides a unified entry point linking to various LLM demos and tools:

- Tokenizer Playground (external)
- Chat Interface
- Prompt Playground
- Context Demo
- Max Length Demo
- Optimization
- Guardrails (external)

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

The app runs on port 8080.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GRADIO_APP_URL` | Base URL for Gradio app interfaces | `http://localhost:7860` |

## Endpoints

| Path | Description |
|------|-------------|
| `/` | Main landing page with exercise cards |
| `/health` | Health check endpoint |

## Building Container

```bash
podman build -t exercise-app -f Containerfile .
podman run -p 8080:8080 exercise-app
```
