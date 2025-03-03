import os

# File paths and database settings
current_dir = os.path.dirname(os.path.abspath(__file__))

database_path = os.path.join(current_dir, "..", "storage")
database_path = os.path.normpath(database_path) # Normalize the path to handle any platform-specific issues (e.g., Windows vs. Unix)

env_path = os.path.join(current_dir,"..", "..", ".env")
env_path = os.path.normpath(env_path)

image_data_path = os.path.join(current_dir, "..", "static", "image_data")
image_data_path = os.path.normpath(image_data_path)


DEFAULT_DB_PATH = database_path
DEFAULT_COLLECTION_NAME = "image_embeddings2"
ENV_FILE_PATH = env_path
IMAGE_DATA_FILE_PATH = image_data_path



# API and model settings
DEFAULT_MODEL_NAME = "gemini-2.0-flash"
API_KEY_ENV_VAR = "GEMINI_API_KEY"

# System message for ChatSession
SYSTEM_MESSAGE = """You are an AI assistant for an image gallery, designed to help users explore and understand images with precision and adaptability. Follow these guidelines to respond conversationally and accurately:

    1. **Query Handling**:
       - For requests like "show me giraffes" or "similar images," respond with "Here are some giraffe images from the gallery" and use the provided data to select relevant images.
       - For general questions (e.g., "Who is Donald Trump?"), give a concise, factual answer (1-2 sentences, 100-150 characters) like "Donald Trump is a former U.S. President and businessman." If unsure, say: "I’m mainly here for image-related queries, but here’s a brief insight: [answer]. How can I assist with the gallery?"

    2. **Personalization**: 
       - If the user shares details like their name in the conversation (e.g., "I am Emil"), use it to personalize responses (e.g., "Hi Emil!") within the current chat. Acknowledge it if asked (e.g., "Do you know my name?"), based on the chat history, but clarify you don’t store personal data long-term: "Yes, you mentioned it’s [name]! I don’t store personal info, just reflect our chat."

    3. **Negation Handling**:
       - When the user includes negation words like "not," "excluding," "no," "without," or similar (e.g., "not dogs," "excluding giraffes," "no cats"), treat these as instructions to *exclude* the mentioned items from the response.
       - Steps to process negated queries:
           1. Identify the positive part (if any) before the negation (e.g., "animals" in "animals not dogs") to determine what to include.
           2. Identify the negated part after the negation word (e.g., "dogs" in "not dogs") to determine what to exclude.
           3. From the retrieved data, select items that match the positive part (if present) and explicitly remove any that match the negated part, using descriptions, tags, or context to judge relevance.
       - Examples:
           - "Show me animals not dogs" → Focus on animal images, exclude anything tagged or described as "dog" or dog-like.
           - "Images excluding giraffes" → Use all retrieved images, exclude those with "giraffe" in tags or descriptions.
           - "Not a cat" → Select from all images, avoid anything cat-related.
           - "Show me landscapes without water or trees" → Find landscape images, exclude those with "water" or "trees" in descriptions or tags.
           - "Animals not dogs or cats" → Include animal images, exclude both "dogs" and "cats."

    4. **Ambiguity and Minimal Input**:
       - If vague (e.g., "What’s this?" with an image), assume a description of the most similar gallery image is wanted.
       - If only an image is provided, describe the closest match.
       - If only a phrase like "giraffe" is given, treat it as a request for similar images unless it’s a question.

    5. **Edge Cases**:
       - If no relevant images match (or all match negated terms), say: "I couldn’t find a close match excluding [term], but here’s something else."
       - If text and image conflict (e.g., "Show dogs" with a cat image), prioritize the image and note: "This looks like a cat, so I’ll show cat images."
       - For off-topic queries (e.g., "Who took these?"), say: "I’m here for image-related questions. How can I assist?"

    6. **Response Format**:
       - Keep responses natural, concise, and engaging.
       - Don’t list file paths in the text; say "I’ll show the images below" if relevant.
       - End with 'Relevant images: <path1>, <path2>, ...' if images are referenced, otherwise omit.

    Use the provided data (descriptions, tags, paths) to craft accurate, context-aware responses, and prioritize user intent, especially with negation."""

# Keywords for detecting description requests
DESCRIBE_KEYWORDS = ["describe", "tell me more", "what is", "explain", "information", "details"]
THIS_IMAGE_PHRASES = ["this image", "this"]

# Keywords for detecting image-related queries
IMAGE_RELATED_KEYWORDS = ["image", "picture", "photo", "gallery", "show me", "similar", "describe"]

# General query prompt
GENERAL_QUERY_PROMPT = (
    "Provide a short, factual, and conversational response (1-2 sentences, 100-150 characters total) to the question: '{query}'. "
    "If unsure, say: 'I’m primarily here to help with image-related questions, but I can offer a brief insight: [short answer]. How can I assist with the gallery?'"
)

# Summary prompt for combining image descriptions
SUMMARY_PROMPT = (
    "Summarize the following image descriptions into a single, concise paragraph (about 2-3 sentences, "
    "150-200 characters total) that captures the main subjects, settings, and any notable features or "
    "actions across all images. Keep the tone professional, engaging, and similar to Gemini or ChatGPT:\n\n"
    "{descriptions}\n"
)

# Error messages
NO_INPUT_ERROR = "Please provide either text input or an image."
NO_DESCRIPTION_AVAILABLE = "No relevant descriptions available for these images."
NO_IMAGES_FOUND = "No relevant images were found."
FAILED_IMAGE_LOAD = "Failed to load the image"

# Formatting strings
RELEVANT_IMAGES_PREFIX = "Relevant images:"
HUMAN_MESSAGE_TEMPLATE = (
    "The user asked: '{input}'\n\n"
    "Here are some relevant images from the gallery:\n{data}\n\n"
    "Image paths: {paths}"
)
DATA_FORMAT_TEMPLATE = (
    "- Description: {doc}\n  Tags: {tags}\n  Color Palette: {palette}"
)

# History settings
MAX_HISTORY_SIZE = 6
DEFAULT_DELAY = 2

# Prompt for image description
IMAGE_DESCRIPTION_PROMPT = """
Describe the image in one paragraph, covering the following aspects:

Visual Elements: Focus on the main subjects—people, objects, or key features—including their appearance, colors, sizes, and placement in the frame.

Setting/Environment: Note the location, time of day, weather, and any key background details (e.g., nature, architecture).

Action/Emotion: Describe any actions, interactions, or emotional undertones in the image.

Context/Story: Speculate on the story or context, and explain how the image makes you feel and why.

Additional Details: Highlight any notable lighting, textures, angles, or symbolic elements.

Be descriptive to offer a vivid picture while keeping it concise.
"""

# Error messages
ERROR_LOADING_IMAGE = "Error loading image: {e}"

# API and model settings

DEFAULT_LANGUAGE = "English"

# Prompt template for image analysis
IMAGE_ANALYSIS_SYSTEM_PROMPT = """
Analyze the provided image and generate professional metadata in the following structure: detected objects, color palette, potential use cases, and tags. Provide the metadata in {language}.
'{format_instructions}'
"""

IMAGE_ANALYSIS_HUMAN_TEXT = "Analyze this image:"

# Error messages (optional, added for consistency with previous examples)
ERROR_ENCODING_IMAGE = "Error encoding image: {e}"


# Messages
API_KEY_ERROR = "GEMINI_API_KEY not found in environment variables."
COLLECTION_FOUND_MSG = "Collection found."
COLLECTION_NOT_FOUND_MSG = "Collection does not exist, creating..."
IMAGE_EXISTS_MSG = "Image {image_name} already exists in the collection. Skipping..."
PROCESSING_IMAGE_MSG = "Processing {image_filename}..."
ALL_IMAGES_PROCESSED_MSG = "All images have been processed and stored in Chroma. Collection Name: {collection_name}"
COLLECTION_RESET_MSG = "Collection {collection_name} has been reset."
COLLECTION_NOT_EXISTS_MSG = "Collection {collection_name} does not exist."
NO_QUERY_INPUT_ERROR = "Please provide both query_text and query_image."
