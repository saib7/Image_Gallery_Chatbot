from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.vectrodb_models.data_loader import ChromaDBClient, ChromaDBDataRetriever
from app.utils.utility import PathRetriever, MapThroughPath
from app.config import config

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/gallery", response_class=HTMLResponse)
async def gallery(request: Request):
    get_path = PathRetriever(db_path=config.DEFAULT_DB_PATH, collection_name=config.DEFAULT_COLLECTION_NAME)
    image_paths = get_path.fetch_image_paths()
    image_paths = list(reversed(image_paths))  # Reverse order
    return templates.TemplateResponse("gallery.html", {"request": request, "image_paths": image_paths})

@router.get("/image-viewer", response_class=HTMLResponse)
async def image_viewer(request: Request, image: str = None):

    """Render the gallery page displaying a list of image paths.

        This endpoint retrieves image paths from a ChromaDB collection, reverses their order,
        and renders them in an HTML template.

        Args:
            request (Request): The incoming HTTP request object provided by FastAPI.
            image: Path to the image to be displayed.

        Returns:
            TemplateResponse: A rendered HTML response using the 'gallery.html' template,
                              containing the request object and a list of image paths.

        Notes:
            - Image paths are fetched from the 'image_embeddings2' collection in the './db' directory.
            - The paths are reversed to display the most recent images first.
            - Templates are loaded from '../frontend/templates'.
        """

    db_client = ChromaDBClient(persist_directory=config.DEFAULT_DB_PATH)
    data_retriever = ChromaDBDataRetriever(
        client=db_client,
        collection_name=config.DEFAULT_COLLECTION_NAME,
        include_embeddings=True,
        include_metadatas=True,
        include_documents=True
    )
    data = data_retriever.get_all_data()
    map_through_path = MapThroughPath(data)
    formatted_data = map_through_path.transform()
    descriptions = formatted_data[image]["document"]
    tags = formatted_data[image]["tags"]
    color_palette = formatted_data[image]["color_palette"]
    detected_objects = formatted_data[image]["detected_objects"]
    return templates.TemplateResponse(
        "image-viewer.html",
        {
            "request": request,
            "image_path": image,
            "description": descriptions,
            "tags": tags,
            "color_palette": color_palette,
            "detected_objects": detected_objects
        }
    )

