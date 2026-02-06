import os
import json
import time
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"

# Configuration from environment
DEFAULT_MODEL_URL = os.getenv("MODEL_URL", "http://localhost:8080")
DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
TINY_MODEL_URL = os.getenv("TINY_URL", "https://tinyllama-1b-cpu")
TINY_MODEL_NAME = os.getenv("TINY_MODEL_NAME", "tinyllama")
COMPRESSED_MODEL_URL = os.getenv("COMPRESSED_MODEL_URL", "http://localhost:8081")
COMPRESSED_MODEL_NAME = os.getenv("COMPRESSED_MODEL_NAME", "llama32-fp8")


# Pydantic models for request validation
class ChatRequest(BaseModel):
    message: str
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048, ge=1, le=4096)
    stream: bool = True


class PlaygroundRequest(BaseModel):
    user_prompt: str
    system_prompt: Optional[str] = "You are a helpful assistant."
    model_name: Optional[str] = None
    model_url: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=100, ge=1, le=4096)
    stream: bool = True


class CompareRequest(BaseModel):
    prompt: str
    model_name_1: Optional[str] = None
    model_url_1: Optional[str] = None
    model_name_2: Optional[str] = None
    model_url_2: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=512, ge=1, le=4096)


# HTTP client for making requests to LLM APIs
http_client: httpx.AsyncClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(timeout=60.0)
    yield
    await http_client.aclose()


app = FastAPI(
    title="LLM Chat API",
    description="Lightweight API for LLM chat interactions",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


async def stream_chat_response(
    model_url: str,
    model_name: str,
    messages: list,
    temperature: float,
    max_tokens: int,
):
    """Stream response from an LLM API."""
    url = f"{model_url.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    try:
        async with http_client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                yield f"data: {json.dumps({'error': f'Error {response.status_code}: {error_text.decode()}'})}\n\n"
                return

            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                try:
                    chunk = json.loads(data)
                    content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        yield f"data: {json.dumps({'content': content})}\n\n"
                except json.JSONDecodeError:
                    continue

    except httpx.TimeoutException:
        yield f"data: {json.dumps({'error': 'Request timed out'})}\n\n"
    except httpx.RequestError as e:
        yield f"data: {json.dumps({'error': f'Request failed: {str(e)}'})}\n\n"


async def get_chat_response(
    model_url: str,
    model_name: str,
    messages: list,
    temperature: float,
    max_tokens: int,
) -> dict:
    """Get non-streaming response from an LLM API."""
    url = f"{model_url.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    try:
        response = await http_client.post(url, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Request failed: {str(e)}")


@app.get("/")
async def root():
    """Serve the main UI."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/chat")
async def chat_page():
    """Serve the chat UI."""
    return FileResponse(STATIC_DIR / "chat.html")


@app.get("/playground")
async def playground_page():
    """Serve the playground UI."""
    return FileResponse(STATIC_DIR / "playground.html")


@app.get("/compare")
async def compare_page():
    """Serve the compare UI."""
    return FileResponse(STATIC_DIR / "compare.html")


@app.get("/context")
async def context_page():
    """Serve the context demo UI."""
    return FileResponse(STATIC_DIR / "context.html")


@app.get("/max-length")
async def max_length_page():
    """Serve the max length demo UI."""
    return FileResponse(STATIC_DIR / "max-length.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/config")
async def get_config():
    """Return current configuration."""
    return {
        "default_model_url": DEFAULT_MODEL_URL,
        "default_model_name": DEFAULT_MODEL_NAME,
        "tiny_model_url": TINY_MODEL_URL,
        "tiny_model_name": TINY_MODEL_NAME,
        "compressed_model_url": COMPRESSED_MODEL_URL,
        "compressed_model_name": COMPRESSED_MODEL_NAME,
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Basic chat endpoint.
    Sends a message to the default model and returns the response.
    Supports streaming (SSE) when stream=true.
    """
    messages = [{"role": "user", "content": request.message}]

    if request.stream:
        return StreamingResponse(
            stream_chat_response(
                DEFAULT_MODEL_URL,
                DEFAULT_MODEL_NAME,
                messages,
                request.temperature,
                request.max_tokens,
            ),
            media_type="text/event-stream",
        )
    else:
        result = await get_chat_response(
            DEFAULT_MODEL_URL,
            DEFAULT_MODEL_NAME,
            messages,
            request.temperature,
            request.max_tokens,
        )
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"content": content}


@app.post("/api/chat/playground")
async def chat_playground(request: PlaygroundRequest):
    """
    Playground endpoint with customizable system prompt and model.
    Allows specifying custom model URL and name.
    """
    model_url = request.model_url or DEFAULT_MODEL_URL
    model_name = request.model_name or DEFAULT_MODEL_NAME

    messages = [
        {"role": "system", "content": request.system_prompt},
        {"role": "user", "content": request.user_prompt},
    ]

    if request.stream:
        return StreamingResponse(
            stream_chat_response(
                model_url,
                model_name,
                messages,
                request.temperature,
                request.max_tokens,
            ),
            media_type="text/event-stream",
        )
    else:
        result = await get_chat_response(
            model_url,
            model_name,
            messages,
            request.temperature,
            request.max_tokens,
        )
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"content": content}


@app.post("/api/chat/context")
async def chat_context(request: ChatRequest):
    """
    Context demo endpoint - same as chat but uses default model.
    Useful for testing token limits.
    """
    return await chat(request)


@app.post("/api/chat/max-length")
async def chat_max_length(request: ChatRequest):
    """
    Max length demo endpoint - uses the tiny model for testing output length.
    """
    messages = [{"role": "user", "content": request.message}]

    if request.stream:
        return StreamingResponse(
            stream_chat_response(
                TINY_MODEL_URL,
                TINY_MODEL_NAME,
                messages,
                request.temperature,
                request.max_tokens,
            ),
            media_type="text/event-stream",
        )
    else:
        result = await get_chat_response(
            TINY_MODEL_URL,
            TINY_MODEL_NAME,
            messages,
            request.temperature,
            request.max_tokens,
        )
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"content": content}


@app.post("/api/chat/compare")
async def compare_models(request: CompareRequest):
    """
    Compare two models side by side.
    Streams responses from both models concurrently with timing information.
    """
    model_url_1 = request.model_url_1 or DEFAULT_MODEL_URL
    model_name_1 = request.model_name_1 or DEFAULT_MODEL_NAME
    model_url_2 = request.model_url_2 or COMPRESSED_MODEL_URL
    model_name_2 = request.model_name_2 or COMPRESSED_MODEL_NAME

    messages = [{"role": "user", "content": request.prompt}]

    async def compare_stream():
        start_time = time.time()
        queue = asyncio.Queue()

        async def stream_model(model_url, model_name, model_id):
            """Stream from a single model and put chunks in the queue."""
            url = f"{model_url.rstrip('/')}/v1/chat/completions"
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": True,
            }

            content = ""
            model_start = time.time()

            try:
                async with http_client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        elapsed = time.time() - model_start
                        await queue.put({
                            "model_id": model_id,
                            "model_name": model_name,
                            "content": f"Error {response.status_code}: {error_text.decode()}",
                            "time": elapsed,
                            "done": True,
                            "error": True,
                        })
                        return

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                content += delta
                                elapsed = time.time() - model_start
                                await queue.put({
                                    "model_id": model_id,
                                    "model_name": model_name,
                                    "content": content,
                                    "time": elapsed,
                                    "done": False,
                                    "error": False,
                                })
                        except json.JSONDecodeError:
                            continue

                elapsed = time.time() - model_start
                await queue.put({
                    "model_id": model_id,
                    "model_name": model_name,
                    "content": content,
                    "time": elapsed,
                    "done": True,
                    "error": False,
                })

            except httpx.TimeoutException:
                elapsed = time.time() - model_start
                await queue.put({
                    "model_id": model_id,
                    "model_name": model_name,
                    "content": "Request timed out",
                    "time": elapsed,
                    "done": True,
                    "error": True,
                })
            except Exception as e:
                elapsed = time.time() - model_start
                await queue.put({
                    "model_id": model_id,
                    "model_name": model_name,
                    "content": str(e),
                    "time": elapsed,
                    "done": True,
                    "error": True,
                })

        # Start both streaming tasks
        task1 = asyncio.create_task(stream_model(model_url_1, model_name_1, 1))
        task2 = asyncio.create_task(stream_model(model_url_2, model_name_2, 2))

        done_count = 0
        while done_count < 2:
            try:
                update = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield f"data: {json.dumps(update)}\n\n"
                if update.get("done"):
                    done_count += 1
            except asyncio.TimeoutError:
                # Check if tasks are still running
                if task1.done() and task2.done():
                    break
                continue

        await task1
        await task2
        yield "data: [DONE]\n\n"

    return StreamingResponse(compare_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
