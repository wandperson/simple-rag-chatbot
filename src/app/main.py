# Basic
from pathlib import Path
from contextlib import asynccontextmanager
import sqlite3

# Backend
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Custom modules
from app.routes import root_router, chat_router


MAIN_DIR = Path(__file__).parent.resolve()


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = sqlite3.connect(
        MAIN_DIR / "database" / "datastore.db", check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    app.state.db_conn = conn

    yield

    conn.close()


def create_app():
    app = FastAPI(lifespan=lifespan)

    STATIC_DIR = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    app.include_router(root_router.router)
    app.include_router(chat_router.router, prefix=chat_router.API_PREFIX)

    return app


app = create_app()
