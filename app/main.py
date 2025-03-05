import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn


# Import routers
from app.api.home import router as home_router
from app.api.gallery import router as gallery_router
from app.api.uploader import router as uploader_router
from app.api.chat import router as chat_router

from app.config import config

# Ensure static/images directory exists
if not os.path.exists(config.IMAGE_DATA_FILE_PATH):
    os.makedirs(config.IMAGE_DATA_FILE_PATH)

# Create the FastAPI app
app = FastAPI()

# Set up templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(home_router)
app.include_router(gallery_router)
app.include_router(uploader_router)
app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
