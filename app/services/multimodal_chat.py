from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage
from langchain_core.messages import HumanMessage
from app.services.embeddings import EmbeddingProcessor
from app.services.description_ai import GeminiImageDescription
from app.config import config, secrets
from app.utils.utility import ChatUtils
from app.vectrodb_models.retriever import GalleryDatabase




class ChatSession:
    """Manages conversation history and interactions with the AI model.

    Attributes:
        model (ChatGoogleGenerativeAI): The generative AI model instance.
        history (list): List of messages in the conversation history.
        max_history (int): Maximum number of messages to retain in history.
        system_message (SystemMessage): The initial system instruction message.
    """

    def __init__(self, api_key, model_name=config.DEFAULT_MODEL_NAME, max_history=config.MAX_HISTORY_SIZE):
        """Initializes the chat session with a model and system message.

        Args:
            api_key (str): API key for the generative AI model.
            model_name (str, optional): Name of the model. Defaults to config.DEFAULT_MODEL_NAME.
            max_history (int, optional): Max history size. Defaults to config.MAX_HISTORY_SIZE.
        """
        self.model = ChatGoogleGenerativeAI(model=model_name, api_key=api_key)
        self.history = []
        self.max_history = max_history
        self.system_message = SystemMessage(content=config.SYSTEM_MESSAGE)

    def add_message(self, message):
        """Adds a message to the conversation history and trims if necessary.

        Args:
            message (HumanMessage or AIMessage): The message to add to history.
        """
        self.history.append(message)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def generate_response(self, human_message):
        """Generates an AI response based on the current conversation history.

        Args:
            human_message (HumanMessage): The user's input message.

        Returns:
            str: The AI-generated response content.
        """
        self.add_message(human_message)
        messages = [self.system_message] + self.history
        response = self.model.invoke(messages)
        self.add_message(AIMessage(content=response.content))
        return response.content


class ResponseFormatter:
    """Formats responses and summarizes image descriptions for the chat system.

    Attributes:
        gemini_desc (GeminiImageDescription): Instance for generating image descriptions.
    """

    def __init__(self, api_key, model_name=config.DEFAULT_MODEL_NAME):
        """Initializes the formatter with a Gemini description generator.

        Args:
            api_key (str): API key for the Gemini model.
            model_name (str, optional): Name of the model. Defaults to config.DEFAULT_MODEL_NAME.
        """
        self.gemini_desc = GeminiImageDescription(api_key=api_key, model_name=model_name, delay=0)

    def describe_image(self, image_path):
        """Generates a description for a single image.

        Args:
            image_path (str): Path to the image file.

        Returns:
            str: The description of the image or an error message if failed.
        """
        return self.gemini_desc.get_description(image_path)

    def summarize_images(self, image_paths):
        """Summarizes descriptions of multiple images into a single paragraph.

        Args:
            image_paths (list): List of image file paths to summarize.

        Returns:
            str: A summarized paragraph or a fallback message if no descriptions are available.
        """
        image_paths = [path.replace("../", "app/") for path in image_paths] ## added later
        ## Because in db path is saved as /app/static/image_data
        ## Not as /static/image_data
        descriptions = [
            desc for path in image_paths
            if (desc := self.describe_image(path)) and desc != config.FAILED_IMAGE_LOAD
        ]
        if not descriptions:
            return config.NO_DESCRIPTION_AVAILABLE
        prompt = config.SUMMARY_PROMPT.format(descriptions="".join([f"- {desc}" for desc in descriptions]))
        response = self.gemini_desc.invoke_model(HumanMessage(content=prompt))
        return response.content


class GalleryChat:
    """Orchestrates the gallery chat system, integrating database, embeddings, and AI responses.

    Attributes:
        api_key (str): API key for the generative AI model.
        db (GalleryDatabase): Database instance for image retrieval.
        embedding_processor (EmbeddingProcessor): Processor for generating embeddings.
        session (ChatSession): Session manager for conversation history and AI responses.
        formatter (ResponseFormatter): Formatter for response generation and summarization.
        utils (ChatUtils): Utility instance for formatting and query analysis.
    """

    def __init__(self):
        """Initializes the gallery chat system with all necessary components."""
        self.api_key = secrets.gemini_api_key
        self.db = GalleryDatabase()
        self.embedding_processor = EmbeddingProcessor()
        self.session = ChatSession(self.api_key)
        self.formatter = ResponseFormatter(self.api_key)
        self.utils = ChatUtils()

    def handle_description_request(self, user_image):
        """Handles requests to describe an uploaded image.

        Args:
            user_image (str): Path to the user-uploaded image.

        Returns:
            tuple: (response, data) where:
                - response (str): Description of the image.
                - data (dict): Metadata with empty paths and description.
        """
        description = self.formatter.describe_image(user_image)
        return description, {"paths": [], "combined_description": ""}

    def handle_general_query(self, user_input):
        """Handles non-image-related general queries with a brief response.

        Args:
            user_input (str): The user's general question.

        Returns:
            tuple: (response, data) where:
                - response (str): Brief answer to the query.
                - data (dict): Metadata with empty paths and description.
        """
        prompt = config.GENERAL_QUERY_PROMPT.format(query=user_input)
        response = self.formatter.gemini_desc.invoke_model(HumanMessage(content=prompt))
        return response.content.strip(), {"paths": [], "combined_description": ""}

    def handle_gallery_query(self, user_input, user_image):
        """Handles image-related queries using the gallery database.

        Args:
            user_input (str, optional): The user's text input. Defaults to None.
            user_image (str, optional): Path to the user's uploaded image. Defaults to None.

        Returns:
            tuple: (response, data) where:
                - response (str): Cleaned AI response text (without paths).
                - data (dict): Metadata with relevant paths and combined description.
        """
        query_embedding = self.embedding_processor.generate_query_embedding(user_input, user_image)
        documents, metadatas, image_paths = self.db.retrieve_relevant_documents(query_embedding)

        formatted_data = self.utils.format_retrieved_data(documents, metadatas)
        human_content = config.HUMAN_MESSAGE_TEMPLATE.format(
            input=user_input or "No text provided",
            data=formatted_data,
            paths=", ".join(image_paths) if image_paths else "None"
        )
        human_message = HumanMessage(content=human_content)

        response_content = self.session.generate_response(human_message)
        clean_response = self.utils.clean_response_text(response_content)
        relevant_paths = self.utils.extract_relevant_paths(response_content, image_paths)

        # Ensure clean_response doesn’t include "Relevant images:" by splitting if necessary
        if config.RELEVANT_IMAGES_PREFIX in clean_response:
            clean_response = clean_response.split(config.RELEVANT_IMAGES_PREFIX)[0].strip()

        combined_description = self.formatter.summarize_images(relevant_paths) if relevant_paths else config.NO_IMAGES_FOUND
        return clean_response, {"paths": relevant_paths, "combined_description": combined_description}

    def chat(self, user_input=None, user_image=None):
        """Processes a user query and returns a response with relevant image data.

        Args:
            user_input (str, optional): The user's text input. Defaults to None.
            user_image (str, optional): Path to the user's uploaded image. Defaults to None.

        Returns:
            tuple: (response, data) where:
                - response (str): The AI-generated response.
                - data (dict): Dictionary with 'paths' (list) and 'combined_description' (str).
        """
        if user_image and user_input and self.utils.is_description_request(user_input):
            return self.handle_description_request(user_image)
        if not user_image and user_input and not self.utils.is_image_related_query(user_input):
            return self.handle_general_query(user_input)
        return self.handle_gallery_query(user_input, user_image)

