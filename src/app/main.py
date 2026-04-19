# Basic
from pathlib import Path

# Backend
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Custom modules
from app.routes import root_router, chat_router


def create_app():
    app = FastAPI()

    STATIC_DIR = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    app.include_router(root_router.router)
    app.include_router(chat_router.router, prefix=chat_router.API_PREFIX)

    return app


app = create_app()
