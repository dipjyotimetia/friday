import os
import shutil
from datetime import datetime

import pytest
from chromadb import PersistentClient
from chromadb.utils import embedding_functions


@pytest.fixture
def test_client():
    """Setup test ChromaDB client with sample data"""
    # Test directory
    test_dir = "./test_data/chroma"
    os.makedirs(test_dir, exist_ok=True)

    # Create client
    client = PersistentClient(path=test_dir)

    # Create test collection with sample data
    collection = client.create_collection(
        name="test_collection",
        embedding_function=embedding_functions.DefaultEmbeddingFunction(),
    )

    # Add sample documents
    collection.add(
        documents=["This is a test document", "Another test document"],
        metadatas=[
            {
                "url": "https://en.wikipedia.org/wiki/Vector_database",
                "timestamp": datetime.now().isoformat(),
            },
        ],
        ids=["1", "2"],
    )

    yield client

    # Cleanup
    shutil.rmtree(test_dir, ignore_errors=True)


def test_chroma_persistence(test_client):
    """Test ChromaDB persistence"""
    # Verify collections exist
    collections = test_client.list_collections()
    assert len(collections) > 0, "No collections found"

    # Verify test collection
    collection = test_client.get_collection("test_collection")
    assert collection is not None, "Test collection not found"


def test_chroma_contents(test_client):
    """Test ChromaDB query functionality"""
    collection = test_client.get_collection("test_collection")

    # Test documents exist
    results = collection.query(query_texts=["test query"], n_results=1)

    assert len(results["documents"]) > 0, "No documents found"
    assert len(results["embeddings"]) > 0, "No embeddings found"
    assert len(results["metadatas"]) > 0, "No metadata found"

    # Test vector search
    search_results = collection.query(query_texts=["test query"], n_results=5)
    assert len(search_results["documents"]) <= 5, "Search results exceeded limit"

    # Test metadata fields
    metadata = results["metadatas"][0]
    assert "url" in metadata, "URL missing from metadata"
    assert "timestamp" in metadata, "Timestamp missing from metadata"
