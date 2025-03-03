import os
from app.vectrodb_models.vectordb import ChromaDatabase
from app.config import config



image_data_path = "../static/image_data"
persist_dir = config.DEFAULT_DB_PATH
print(image_data_path)
print(persist_dir)



# Store images
db = ChromaDatabase(collection_name="image_embeddings2", persist_directory=persist_dir)
db.store_images_in_chroma(image_data_path)
