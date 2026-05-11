import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import characters, chat, story


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HP Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(story.router, prefix="/api/story")
app.include_router(characters.router, prefix="/api/characters")
app.include_router(chat.router, prefix="/api/chat")


@app.get("/health")
def health() -> dict[str, str]:
    """Quick liveness check."""
    return {"status": "ok"}
