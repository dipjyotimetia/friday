"""
Embeddings Service Module

This module provides a service for managing and querying document embeddings using various LLM providers.
It handles document splitting, embedding generation, similarity search, and vector database management
using Chroma DB.

Features:
- Document splitting with configurable chunk sizes
- Embedding generation for single and batch texts
- Similarity search with configurable k-nearest neighbors
- Persistent storage of embeddings
- Collection statistics and management
- Support for multiple LLM providers (OpenAI, Google, Ollama, Mistral)

Example:
    >>> service = EmbeddingsService(provider="openai")
    >>> service.create_database(["This is a sample text"], [{"source": "example"}])
    >>> results = service.similarity_search("sample")
"""

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from friday.llm.llm import ModelProvider, get_embedding_client


class EmbeddingsService:
    """
    A service class for managing document embeddings and vector search operations.

    This class provides functionality for:
    - Creating and managing a vector database
    - Generating embeddings for documents
    - Performing similarity searches
    - Managing document collections

    Attributes:
        embeddings: The embedding client from the selected provider
        text_splitter: Utility for splitting text into chunks
        persist_directory (Path): Directory where the vector database is stored
        provider (ModelProvider): The LLM provider being used
        db (Chroma): The vector database instance
    """

    def __init__(
        self,
        provider: ModelProvider = "openai",
        persist_directory: str = "./data/chroma",
        chunk_size: int = 1000,  # Maximum size of each text chunk
        chunk_overlap: int = 200,  # Number of characters to overlap between chunks
    ):
        """
        Initialize the embeddings service.

        Args:
            provider: The LLM provider to use for embeddings (default: "openai")
            persist_directory: Path where the vector database will be stored
            chunk_size: Maximum size of each text chunk for splitting
            chunk_overlap: Number of characters to overlap between chunks

        Example:
            >>> service = EmbeddingsService(provider="openai", chunk_size=500)
        """
        self.embeddings = get_embedding_client(provider)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        self.persist_directory = Path(persist_directory)
        self.provider = provider
        self.db = self._load_or_create_db()

    def _load_or_create_db(self) -> Chroma:
        """Load the database if it exists, otherwise create a new one."""
        if not self.persist_directory.exists():
            print(
                f"Persist directory {self.persist_directory} does not exist. Creating new directory."
            )
            self.persist_directory.mkdir(parents=True, exist_ok=True)

        try:
            db = Chroma(
                persist_directory=str(self.persist_directory),
            )
            print("Loaded existing Chroma DB")  # Debugging
            return db
        except (ValueError, Exception) as e:
            print(f"Error loading Chroma DB: {e}")  # Debugging
            print("Creating a new Chroma DB")  # Debugging
            return Chroma(
                persist_directory=str(self.persist_directory),
            )

    def create_database(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        collection_name: str = "default",
    ) -> None:
        """
        Create a new vector database from the provided texts and metadata.

        Args:
            texts: List of text documents to embed
            metadatas: Optional list of metadata dictionaries for each text
            collection_name: Name of the collection to create

        Raises:
            ValueError: If texts is empty or metadata length doesn't match texts

        Example:
            >>> texts = ["Document 1", "Document 2"]
            >>> metadata = [{"source": "web"}, {"source": "file"}]
            >>> service.create_database(texts, metadata)
        """
        docs = self.text_splitter.create_documents(texts, metadatas=metadatas)
        self.db = Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory),
            collection_name=collection_name,
        )

    def similarity_search(self, query: str, k: int = 4) -> List[str]:
        """
        Search for documents similar to the query text.

        Args:
            query: The search query text
            k: Number of similar documents to return (default: 4)

        Returns:
            List[str]: List of similar document contents

        Raises:
            ValueError: If query is empty or k < 1

        Example:
            >>> results = service.similarity_search("machine learning", k=3)
        """

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
        self.persist_directory.rmdir()
