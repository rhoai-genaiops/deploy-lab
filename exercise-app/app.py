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

# Get AI orientation app URL from environment variable
AI_ORIENTATION_APP_URL = os.getenv("AI_ORIENTATION_APP_URL", "http://localhost:8000")
TOKENIZER_URL = "https://agents-course-the-tokenizer-playground.static.hf.space"

# Define exercises
EXERCISES = [
    {
        "id": "chat",
        "title": "Chat with the Model",
        "description": "Test LLM conversations and responses",
        "icon": "comments",
        "path": "/chat",
        "external": False,
    },
    {
        "id": "tokenizer",
        "title": "Tokenizer Playground",
        "description": "Explore how LLMs break text into tokens",
        "icon": "puzzle-piece",
        "url": TOKENIZER_URL,
        "external": True,
    },
    {
        "id": "guardrails",
        "title": "Guardrails",
        "description": "Learn about LLM safety and content moderation",
        "icon": "shield-halved",
        "url": "https://red.ht/lemonade-stand",
        "external": True,
    },
    {
        "id": "context",
        "title": "Max Tokens Demo",
        "description": "Control how many tokens the model generates",
        "icon": "window-maximize",
        "path": "/context",
        "external": False,
    },
    {
        "id": "maxlength",
        "title": "Context Window Demo",
        "description": "See what happens when you hit the model's capacity limit",
        "icon": "ruler-horizontal",
        "path": "/max-length",
        "external": False,
    },
    {
        "id": "compare",
        "title": "Side-by-Side Model Comparison",
        "description": "Compare different models and optimization techniques",
        "icon": "bolt",
        "path": "/compare",
        "external": False,
    },
    {
        "id": "prompt",
        "title": "Prompt Engineering Lab",
        "description": "Experiment with different prompting techniques",
        "icon": "terminal",
        "path": "/playground",
        "external": False,
    },
]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Build URLs for internal exercises
    exercises = []
    for ex in EXERCISES:
        exercise = ex.copy()
        if not exercise.get("external"):
            exercise["url"] = f"{AI_ORIENTATION_APP_URL}{exercise['path']}"
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
