import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import warnings
from app.config import config

warnings.filterwarnings("ignore")


class CLIPEmbedding:
    """
    A class for generating text and image embeddings using the CLIP model.
    This class provides methods for embedding images and text using CLIP's vision and text encoders,
    which project both into a shared feature space for cross-modal tasks.

    Attributes:
        device (str): The device to run the model on (either "cuda" for GPU or "cpu").
        clip_model (CLIPModel): The pre-trained CLIP model used for generating embeddings.
        clip_processor (CLIPProcessor): The processor for preparing inputs for the CLIP model.
    """

    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        """
               Initializes the CLIPEmbedding class and loads the CLIP model and processor.

               Args:
                   device (str, optional): The device to use for model inference. Defaults to "cuda" if available, otherwise "cpu".
               """
        self.device = device
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def embed_image(self, image_path):
        """
        Generates an embedding for an image by passing it through the CLIP model.

        Args:
            image_path (str): The path to the image file to be embedded.

        Returns:
            numpy.ndarray: A 1D array representing the image's embedding, normalized to unit length.
        """
        # Load image
        image = Image.open(image_path).convert("RGB")

        # Process the image for CLIP
        inputs = self.clip_processor(images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            image_embedding = self.clip_model.get_image_features(**inputs)

        # Normalize the image embedding to unit length
        image_embedding = image_embedding / image_embedding.norm(p=2, dim=-1, keepdim=True)

        return image_embedding.cpu().numpy().flatten()  # Flatten the embedding to a 1D array

    def embed_text(self, query_text: str):
        """
        Generates an embedding for a given text query using the CLIP model's text encoder.

        Args:
            query_text (str): The text input to be embedded.

        Returns:
            numpy.ndarray:: A 1D array representing the text's embedding, normalized to unit length.
        """
        text_inputs = self.clip_processor(text=[query_text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_features = self.clip_model.get_text_features(**text_inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy().flatten()


class EmbeddingProcessor:
    """Generates embeddings for text and images using the CLIP model.

    Attributes:
        clip (CLIPEmbedding): The CLIP embedding model instance.
    """

    def __init__(self):
        """Initializes the CLIP embedding model."""
        self.clip = CLIPEmbedding()

    def generate_query_embedding(self, text=None, image_path=None):
        """Generates a query embedding from text, image, or both.

        Args:
            text (str, optional): Text input for embedding. Defaults to None.
            image_path (str, optional): Path to the image for embedding. Defaults to None.

        Returns:
            numpy.ndarray: The resulting embedding vector.

        Raises:
            ValueError: If neither text nor image_path is provided.
        """
        if not text and not image_path:
            raise ValueError(config.NO_INPUT_ERROR)
        if image_path and text:
            return (self.clip.embed_image(image_path) + self.clip.embed_text(text)) / 2
        return self.clip.embed_image(image_path) if image_path else self.clip.embed_text(text)

