import os
from app.vectrodb_models.vectrodb import ChromaDatabase

current_dir = os.path.dirname(os.path.abspath(__file__))
image_data_path = os.path.join(current_dir, "..", "static", "image_data")
persist_dir = os.path.join(current_dir, "..", "storage")

# Normalize the path to handle any platform-specific issues (e.g., Windows vs. Unix)
image_data_path = os.path.normpath(image_data_path)
persist_dir = os.path.normpath(persist_dir)
print(image_data_path)
print(persist_dir)



# Store images
db = ChromaDatabase(collection_name="image_embeddings2", persist_directory=persist_dir)
db.store_images_in_chroma(image_data_path)
