# Backend
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Custom modules
from routes import home
from routes import api


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(api.router)
