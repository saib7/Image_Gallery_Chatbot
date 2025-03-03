import chromadb
from app.config import config


class GalleryDatabase:
    """Manages interactions with the ChromaDB database for storing and retrieving image embeddings.

    Attributes:
        client (chromadb.PersistentClient): The persistent ChromaDB client instance.
        collection (chromadb.Collection): The specific collection for image embeddings.
    """

    def __init__(self, db_path=config.DEFAULT_DB_PATH, collection_name=config.DEFAULT_COLLECTION_NAME):
        """Initializes the database client and collection.

        Args:
            db_path (str, optional): Path to the database directory. Defaults to config.DEFAULT_DB_PATH.
            collection_name (str, optional): Name of the collection. Defaults to config.DEFAULT_COLLECTION_NAME.
        """
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(collection_name) ## use get_or_create_collection

    def retrieve_relevant_documents(self, query_embedding, top_k=5):
        """Retrieves top-k relevant documents and metadata based on a query embedding.

        Args:
            query_embedding (numpy.ndarray): The embedding vector for the query.
            top_k (int, optional): Number of top results to retrieve. Defaults to 5.

        Returns:
            tuple: (documents, metadatas, image_paths) where:
                - documents (list): List of document descriptions.
                - metadatas (list): List of metadata dictionaries.
                - image_paths (list): List of image file paths.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas"]
        )
        return results["documents"][0], results["metadatas"][0], [m["image_path"] for m in results["metadatas"][0]]

