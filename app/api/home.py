from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the homepage of the MemoryBot website.

    This endpoint renders and returns the HTML content for the homepage using a Jinja2 template.

    Args:
        request (Request): The incoming HTTP request object provided by FastAPI.

    Returns:
        TemplateResponse: A rendered HTML response using the 'home_page.html' template,
                          with the request object passed to the template context.

    Notes:
        - The template is loaded from the '../frontend/templates' directory.
        - The response is explicitly set to HTMLResponse via the route decorator.
    """
    return templates.TemplateResponse("home_page.html", {"request": request})
