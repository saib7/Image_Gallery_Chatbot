from fastapi import APIRouter, Request, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from app.vectrodb_models.vectordb import ChromaDatabase
from app.config import config


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def process_images_background(directory: str):
    """Process and store images in ChromaDB as a background task.

    This function initializes a ChromaDatabase instance and stores images from the specified
    directory into the 'image_embeddings2' collection. Errors are logged to the console.

    Args:
        directory (str): The path to the directory containing images to process.

    Notes:
        - The ChromaDatabase persists data in './db'.
        - Errors during processing are printed to the console but do not raise exceptions
          to the caller, as this runs in the background.
    """
    try:
        db = ChromaDatabase(collection_name=config.DEFAULT_COLLECTION_NAME, persist_directory=config.DEFAULT_DB_PATH)
        db.store_images_in_chroma(directory)
    except Exception as e:
        print(f"Error processing images: {str(e)}")


@router.get("/uploader", response_class=HTMLResponse)
async def uploader(request: Request):
    return templates.TemplateResponse("uploader.html", {"request": request})


@router.post("/upload")
async def upload_files(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """
    Handle multiple image uploads and save them to the static/images directory.
    """
    for file in files:
        upload_path = f"../static/image_data/{file.filename}"
        with open(upload_path, "wb") as buffer:
            buffer.write(await file.read())

    upload_dir = "../static/image_data"
    background_tasks.add_task(process_images_background, upload_dir)
    return {"message": f"{len(files)} files successfully uploaded!"}

