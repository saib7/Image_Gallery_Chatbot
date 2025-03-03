import uuid
import tempfile
import shutil
import os
from fastapi import APIRouter, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from app.services.multimodal_chat import GalleryChat

router = APIRouter()

# Load chat.html content
with open("app/templates/chat.html", "r") as f:
    chat_html = f.read()

# Store GalleryChat instances for each session
sessions = {}

@router.get("/chat", response_class=HTMLResponse)
async def read_root():
    """Serve the chat interface HTML page.

        This endpoint returns the preloaded HTML content for the chat interface.

        Returns:
            HTMLResponse: The contents of 'chat.html' as an HTML response.

        Notes:
            - The HTML file is loaded from '../templates/chat.html' at startup.
        """
    return chat_html

@router.post("/start_session")
async def start_session():
    """Initialize a new chat session and provide a unique session ID.

    This endpoint creates a new GalleryChat instance, associates it with a unique session ID,
    and stores it in the sessions dictionary.

    Returns:
        dict: A JSON response containing the generated `session_id` (str).

    Notes:
        - Session IDs are generated using UUID4 for uniqueness.
        - The session persists in memory until the server restarts or it is explicitly cleared.
    """
    session_id = str(uuid.uuid4())
    gallery = GalleryChat()
    sessions[session_id] = gallery
    return {"session_id": session_id}

@router.post("/chat/{session_id}")
async def chat(session_id: str, text: str = Form(None), image: UploadFile = None):
    """Process user input (text and/or image) and return the chatbot's response.

    This endpoint handles multimodal chat input for a given session, passing text and/or an
    uploaded image to the GalleryChat instance, and returns the chatbot's response along with
    relevant image paths and descriptions.

    Args:
        session_id (str): The unique identifier for the chat session.
        text (str, optional): The user's text input. Defaults to None.
        image (UploadFile, optional): An uploaded image file. Defaults to None.

    Returns:
        dict: A JSON response containing:
            - response (str): The chatbot's text response.
            - images (list[str]): URLs of relevant images, adjusted for frontend access.
            - combined_description (str): A combined description of the relevant images.

    Raises:
        HTTPException: If the `session_id` is not found (404 status).

    Notes:
        - Temporary image files are created and deleted after processing.
        - Image paths in the response are rewritten to replace '../frontend/' with '../'.
        - Either `text`, `image`, or both must be provided for meaningful interaction.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    gallery = sessions[session_id]
    user_image_path = None

    if image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            shutil.copyfileobj(image.file, temp_file)
            user_image_path = temp_file.name

    try:
        response, image_data = gallery.chat(user_input=text, user_image=user_image_path)
        relevant_paths = image_data["paths"]
        combined_description = image_data["combined_description"]
    finally:
        if user_image_path:
            os.remove(user_image_path)

    # urls = [path.replace("../frontend/", "../") for path in relevant_paths]
    urls = relevant_paths
    return {"response": response, "images": urls, "combined_description": combined_description}

