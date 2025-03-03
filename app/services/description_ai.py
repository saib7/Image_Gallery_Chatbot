import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import base64

from app.config.secrets import gemini_api_key
from app.config.config import (
    DEFAULT_MODEL_NAME,
    DEFAULT_DELAY,
    IMAGE_DESCRIPTION_PROMPT,
    ERROR_LOADING_IMAGE,
    FAILED_IMAGE_LOAD,
)


class GeminiImageDescription:
    def __init__(self, api_key: str, model_name=DEFAULT_MODEL_NAME, delay=DEFAULT_DELAY):
        self.api_key = api_key
        self.model_name = model_name
        self.model = ChatGoogleGenerativeAI(model=self.model_name, api_key=gemini_api_key)
        self.delay = delay

    def load_image(self, image_path: str):
        """Reads and encodes the image from the local path."""
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            return image_data
        except Exception as e:
            print(ERROR_LOADING_IMAGE.format(e=e))
            return None

    def create_message(self, image_data):
        """Creates a HumanMessage with the encoded image."""
        return HumanMessage(
            content=[
                {"type": "text", "text": IMAGE_DESCRIPTION_PROMPT},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
            ],
        )

    def invoke_model(self, message):
        """Invoke the model with the message and return the response."""
        time.sleep(self.delay)
        return self.model.invoke([message])

    def get_description(self, image_path: str):
        """Invokes the model and retrieves the description of the image."""
        image_data = self.load_image(image_path)
        if image_data:
            message = self.create_message(image_data)
            response = self.invoke_model(message)
            return response.content
        else:
            return FAILED_IMAGE_LOAD

