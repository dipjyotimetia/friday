import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from friday.llm.llm import ModelProvider, get_embedding_client


class EmbeddingsService:
    def __init__(
        self,
        provider: ModelProvider = "vertex",
        persist_directory: str = "./data/chroma",
        chunk_size: int = 1000,  # Maximum size of each text chunk
        chunk_overlap: int = 200,  # Number of characters to overlap between chunks
    ):
        """Initialize the embeddings service with configurable persistence directory"""
        self.embeddings = get_embedding_client(provider)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        self.persist_directory = Path(persist_directory)
        self.db = None

    def create_database(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        collection_name: str = "default",
    ) -> None:
        docs = self.text_splitter.create_documents(texts, metadatas=metadatas)
        self.db = Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory),
            collection_name=collection_name,
        )

    def similarity_search(self, query: str, k: int = 4) -> List[str]:
        """Search for similar documents with input validation"""

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if k < 1:
            raise ValueError("k must be positive")
        if not self.db:
            raise ValueError("Database not initialized. Call create_database first.")

        results = self.db.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def get_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for a single text"""
        return self.embeddings.embed_query(text)

    def batch_embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        return self.embeddings.embed_documents(texts)

    def add_texts(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> List[str]:
        """Add texts with validation"""

        if not texts:
            raise ValueError("Cannot add empty text list")
        if metadatas and len(texts) != len(metadatas):
            raise ValueError("Number of texts and metadata entries must match")
        if not self.db:
            raise ValueError("Database not initialized. Call create_database first.")

        ids = [str(uuid.uuid4()) for _ in texts]
        self.db.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        return ids

    def find_nearest_neighbors(
        self, text: str, k: int = 4, include_distances: bool = True
    ) -> Dict[str, List]:
        """Find k-nearest neighbors for a given text"""
        if not self.db:
            raise ValueError("Database not initialized. Call create_database first.")

        embedding = self.get_embeddings(text)
        results = self.db.similarity_search_by_vector_with_relevance_scores(
            embedding, k=k
        )
        documents = []
        distances = []
        for doc, distance in results:
            documents.append({"content": doc.page_content, "metadata": doc.metadata})
            distances.append(distance)
        return {
            "documents": documents,
            "distances": distances if include_distances else None,
        }

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the current database"""
        if not self.db:
            raise ValueError("Database not initialized. Call create_database first.")

        collection = self.db.get()

        # Handle empty collection
        if not collection["documents"]:
            return {
                "total_documents": 0,
                "embedding_dimension": 0,
                "unique_metadata_keys": [],
            }

        # Get unique metadata keys with null checks
        unique_keys = set()
        if collection["metadatas"]:
            for metadata in collection["metadatas"]:
                if metadata:  # Check if metadata item exists
                    unique_keys.update(metadata.keys())

        return {
            "total_documents": len(collection["documents"]),
            "embedding_dimension": len(collection["embeddings"][0])
            if collection["embeddings"]
            else 0,
            "unique_metadata_keys": list(unique_keys),
        }

    def cleanup(self) -> None:
        """Clean up resources and delete the database"""
        if self.db:
            self.db.delete_collection()
        self.db = None
