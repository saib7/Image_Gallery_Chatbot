import time
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from app.config.secrets import gemini_api_key
from app.config.config import (
    DEFAULT_MODEL_NAME,
    DEFAULT_DELAY,
    DEFAULT_LANGUAGE,
    IMAGE_ANALYSIS_SYSTEM_PROMPT,
    IMAGE_ANALYSIS_HUMAN_TEXT,
)


class ImageMetadata(BaseModel):
    detected_objects: list[str] = Field(description="A list of objects detected in the image")
    color_palette: list[str] = Field(description="A list of predominant colors in the image")
    potential_use_cases: list[str] = Field(description="Potential use cases or industries that could benefit from the image")
    tags: list[str] = Field(description="Relevant tags for categorizing the image")


class ImageAnalyzer:
    """
        A class to analyze images using Google Generative AI.

        Attributes:
            api_key (str): The API key for accessing Google Generative AI.
            model (str): The name of the AI model to use.
            delay (int): The delay between API calls in seconds.
            model (ChatGoogleGenerativeAI): The AI model instance.
            parser (PydanticOutputParser): The parser for the AI model's output.
            prompt (ChatPromptTemplate): The prompt template for the AI model.

        Methods:
            analyze_image(image_path: str, language: str = DEFAULT_LANGUAGE) -> dict:
                Analyzes an image and returns the metadata.
        """
    def __init__(self, api_key: str, model_name: str = DEFAULT_MODEL_NAME, delay: int = DEFAULT_DELAY):
        self.delay = delay
        self.model = ChatGoogleGenerativeAI(model=model_name, api_key=gemini_api_key)
        self.parser = PydanticOutputParser(pydantic_object=ImageMetadata)
        self.prompt = self._create_prompt_template()

    def _create_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", IMAGE_ANALYSIS_SYSTEM_PROMPT),
            ("human", [
                {"type": "text", "text": IMAGE_ANALYSIS_HUMAN_TEXT},
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,{image_data}"},
                },
            ])
        ])

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        return image_data

    def analyze_image(self, image_path: str, language: str = DEFAULT_LANGUAGE):
        image_data = self._encode_image(image_path)

        chain = self.prompt | self.model | self.parser

        time.sleep(self.delay)

        result = chain.invoke({
            "language": language,
            "format_instructions": self.parser.get_format_instructions(),
            "image_data": image_data
        })

        return result.model_dump()
