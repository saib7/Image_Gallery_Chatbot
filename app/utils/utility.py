import re
from app.config import config
from app.vectrodb_models.data_loader import ChromaDBClient, ChromaDBDataRetriever
from app.vectrodb_models.vectordb import ChromaDatabase


class PathRetriever:
    def __init__(self, db_path=config.DEFAULT_DB_PATH, collection_name=config.DEFAULT_COLLECTION_NAME):
        # Initialize ChromaDBClient and ChromaDBDataRetriever
        self.db_client = ChromaDBClient(persist_directory=db_path)
        self.data_retriever = ChromaDBDataRetriever(
            client=self.db_client,
            collection_name=collection_name,
            include_embeddings=True,
            include_metadatas=True,
            include_documents=True
        )

    def fetch_image_paths(self):
        # Fetch all data from the collection
        data = self.data_retriever.get_all_data()
        image_paths = []

        for i in range(len(data["metadatas"])):
            image_paths.append(data["metadatas"][i]["image_path"])

        # Replace paths
        image_paths = [path.replace("app/", "../") for path in image_paths]

        return image_paths


class MapThroughPath:
    """
    A class to transform and structure data by mapping image paths to their
    corresponding documents, tags, color palettes, and detected objects.

    The class processes metadata, splits comma-separated values into lists,
    and creates a new structured dictionary for easy access and further use.

    Attributes:
        data (dict): The input data containing 'metadatas' and 'documents' to be processed.
    """

    def __init__(self, data):
        """
        Initialize with the data to be transformed.

        Args:
            data (dict): The input data containing metadata and documents.
        """
        self.data = data

    def _split_metadata_field(self, metadata_field):
        """
        Helper method to split comma-separated metadata fields into lists.

        Args:
            metadata_field (str): The metadata field to be split into a list.

        Returns:
            list: A list of values split by commas.
        """
        return metadata_field.split(', ') if metadata_field else []

    def transform(self):
        """
        Transforms the input data by organizing and structuring it into a more accessible format.

        The method iterates over the metadata, extracts relevant information, splits metadata fields
        into lists, and maps the image path to its associated document, tags, color palette,
        and detected objects.

        Returns:
            dict: A dictionary with image paths as keys and structured data as values.
        """
        transformed_data = {}

        for idx, metadata in enumerate(self.data['metadatas']):
            path = metadata.get('image_path')
            image_path = path.replace("app/", "../")
            # image_path = path
            document = self.data['documents'][idx]

            # Split the metadata fields into lists
            color_palette = self._split_metadata_field(metadata.get('color_palette', ''))
            detected_objects = self._split_metadata_field(metadata.get('detected_objects', ''))
            tags = self._split_metadata_field(metadata.get('tags', ''))

            # Structure the transformed data
            transformed_data[image_path] = {
                'document': document,
                'tags': tags,
                'color_palette': color_palette,
                'detected_objects': detected_objects
            }

        return transformed_data


class ChatUtils:
    """Utility class for chat-related operations such as formatting and query analysis.

    Attributes:
        None
    """

    def format_retrieved_data(self, documents, metadatas):
        """Formats retrieved documents and metadata into a readable string.

        Args:
            documents (list): List of document descriptions from the database.
            metadatas (list): List of metadata dictionaries containing tags and color palettes.

        Returns:
            str: A formatted string with descriptions, tags, and color palettes for each document.
        """
        return "\n".join(
            [config.DATA_FORMAT_TEMPLATE.format(doc=doc, tags=meta["tags"], palette=meta["color_palette"])
             for doc, meta in zip(documents, metadatas)]
        )

    def extract_relevant_paths(self, response_content, all_image_paths):
        """Extracts relevant image paths from the AI response content.

        Args:
            response_content (str): The full response text from the AI model.
            all_image_paths (list): List of all available image paths from the database.

        Returns:
            list: A list of image paths that are both in the response and the database.
        """
        if config.RELEVANT_IMAGES_PREFIX not in response_content:
            return []
        relevant_part = response_content.split(config.RELEVANT_IMAGES_PREFIX)[-1].strip()
        listed_paths = [path.strip() for path in relevant_part.split(",")]
        # return [path for path in listed_paths if path in all_image_paths]
        return [path.replace("app/", "../") for path in listed_paths if path in all_image_paths]

    def clean_response_text(self, response_content):
        """Removes inline image references from the response text.

        Args:
            response_content (str): The raw response text from the AI model.

        Returns:
            str: Cleaned response text with image references removed.
        """
        return re.sub(r'\[image: .*?\]', '', response_content).strip()

    def is_description_request(self, user_input):
        """Checks if the user input suggests a request to describe an image.

        Args:
            user_input (str): The user's input text.

        Returns:
            bool: True if the input contains description keywords and image references, False otherwise.
        """
        lower_input = user_input.lower()
        return any(keyword in lower_input for keyword in config.DESCRIBE_KEYWORDS) and \
               any(phrase in lower_input for phrase in config.THIS_IMAGE_PHRASES)

    def is_image_related_query(self, user_input):
        """Checks if the user input is related to images or gallery content.

        Args:
            user_input (str): The user's input text.

        Returns:
            bool: True if the input contains image-related keywords, False otherwise.
        """
        return any(keyword in user_input.lower() for keyword in config.IMAGE_RELATED_KEYWORDS)


def process_images_background(directory: str):
    try:
        db = ChromaDatabase(collection_name=config.DEFAULT_COLLECTION_NAME, persist_directory=config.DEFAULT_DB_PATH)
        db.store_images_in_chroma(directory)

    except Exception as e:
        print(f"Error processing images: {str(e)}")
