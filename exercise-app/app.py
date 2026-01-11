import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="AI Orientation Exercises")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Get gradio app URL from environment variable
GRADIO_APP_URL = os.getenv("GRADIO_APP_URL", "http://localhost:7860")
TOKENIZER_URL = "https://agents-course-the-tokenizer-playground.static.hf.space"

# Define exercises
EXERCISES = [
    {
        "id": "tokenizer",
        "title": "Tokenizer Playground",
        "description": "Explore how LLMs break text into tokens",
        "icon": "puzzle-piece",
        "url": TOKENIZER_URL,
        "external": True,
    },
    {
        "id": "chat",
        "title": "Chat Interface",
        "description": "Test LLM conversations and responses",
        "icon": "comments",
        "path": "/chat-interface",
        "external": False,
    },
    {
        "id": "prompt",
        "title": "Prompt Playground",
        "description": "Experiment with different prompting techniques",
        "icon": "terminal",
        "path": "/prompt-playground",
        "external": False,
    },
    {
        "id": "context",
        "title": "Context Demo",
        "description": "Understand context windows and token limits",
        "icon": "window-maximize",
        "path": "/context-demo",
        "external": False,
    },
    {
        "id": "maxlength",
        "title": "Max Length Demo",
        "description": "See how token limits affect model responses",
        "icon": "ruler-horizontal",
        "path": "/max-length-demo",
        "external": False,
    },
    {
        "id": "optimization",
        "title": "Optimization",
        "description": "Explore model optimization techniques",
        "icon": "bolt",
        "path": "/optimization",
        "external": False,
    },
    {
        "id": "guardrails",
        "title": "Guardrails",
        "description": "Learn about LLM safety and content moderation",
        "icon": "shield-halved",
        "url": "https://red.ht/lemon",
        "external": True,
    },
]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Build URLs for internal exercises
    exercises = []
    for ex in EXERCISES:
        exercise = ex.copy()
        if not exercise.get("external"):
            exercise["url"] = f"{GRADIO_APP_URL}{exercise['path']}"
        exercises.append(exercise)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "exercises": exercises,
            "title": "AI Orientation Exercises",
        },
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
