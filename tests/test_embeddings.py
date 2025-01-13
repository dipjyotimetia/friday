import shutil
from pathlib import Path
from typing import Dict, Generator, List

import pytest

from friday.services.embeddings import EmbeddingsService


@pytest.fixture(scope="function")
def test_dir(tmp_path) -> Generator[Path, None, None]:
    """Create a temporary directory for test data"""
    test_path = tmp_path / "test_embeddings"
    test_path.mkdir(exist_ok=True)
    yield test_path
    # Cleanup after test
    shutil.rmtree(test_path)


@pytest.fixture(scope="function")
def embeddings_service(test_dir) -> EmbeddingsService:
    """Create a fresh embeddings service instance for each test"""
    return EmbeddingsService(persist_directory=str(test_dir))


@pytest.fixture
def sample_texts() -> List[str]:
    """Sample texts for testing"""
    return [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a versatile programming language",
    ]


@pytest.fixture
def sample_metadata() -> List[Dict]:
    """Sample metadata for testing"""
    return [
        {"source": "test1", "category": "sample"},
        {"source": "test2", "category": "ai"},
        {"source": "test3", "category": "programming"},
    ]


class TestEmbeddingsService:
    def test_create_database(self, embeddings_service, sample_texts, sample_metadata):
        """Test database creation with texts and metadata"""
        embeddings_service.create_database(sample_texts, sample_metadata)
        assert embeddings_service.db is not None

        # Verify persistence
        assert Path(embeddings_service.persist_directory).exists()

    def test_similarity_search(self, embeddings_service, sample_texts):
        """Test similarity search functionality"""
        embeddings_service.create_database(sample_texts)
        results = embeddings_service.similarity_search("artificial intelligence", k=2)

        assert isinstance(results, list)
        assert len(results) <= 2
        assert isinstance(results[0], str)

    def test_get_embeddings(self, embeddings_service):
        """Test single text embedding generation"""
        text = "Test embedding generation"
        embedding = embeddings_service.get_embeddings(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    def test_batch_embed_texts(self, embeddings_service, sample_texts):
        """Test batch embedding generation"""
        embeddings = embeddings_service.batch_embed_texts(sample_texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == len(sample_texts)
        assert all(isinstance(emb, list) for emb in embeddings)

    def test_add_and_delete_texts(self, embeddings_service, sample_texts):
        """Test adding and deleting texts"""
        embeddings_service.create_database(sample_texts[:2])
        new_ids = embeddings_service.add_texts([sample_texts[2]])

        assert len(new_ids) == 1

        # Test deletion
        embeddings_service.delete_texts(new_ids)
        results = embeddings_service.similarity_search(sample_texts[2], k=1)
        assert sample_texts[2] not in results

    def test_update_texts(self, embeddings_service, sample_texts):
        """Test updating existing texts"""
        embeddings_service.create_database(sample_texts[:2])
        ids = embeddings_service.add_texts([sample_texts[2]])

        updated_text = ["Updated test text"]
        embeddings_service.update_texts(ids, updated_text)

        results = embeddings_service.similarity_search("Updated test", k=1)
        assert any("Updated test" in result for result in results)

    def test_semantic_search(self, embeddings_service, sample_texts, sample_metadata):
        """Test semantic search with threshold"""
        embeddings_service.create_database(sample_texts, sample_metadata)
        results = embeddings_service.semantic_search(
            "programming language", k=2, threshold=0.5
        )

        assert isinstance(results, list)
        assert len(results) <= 2
        assert all(isinstance(result, dict) for result in results)
        assert all("score" in result for result in results)
        assert all(result["score"] >= 0.5 for result in results)

    def test_get_collection_stats(
        self, embeddings_service, sample_texts, sample_metadata
    ):
        """Test collection statistics"""
        embeddings_service.create_database(sample_texts, sample_metadata)
        stats = embeddings_service.get_collection_stats()

        assert isinstance(stats, dict)
        assert stats["total_documents"] == len(sample_texts)
        assert stats["embedding_dimension"] > 0
        assert isinstance(stats["unique_metadata_keys"], list)
        assert "source" in stats["unique_metadata_keys"]
        assert "category" in stats["unique_metadata_keys"]

    def test_find_nearest_neighbors(self, embeddings_service, sample_texts):
        """Test nearest neighbors search"""
        embeddings_service.create_database(sample_texts)
        results = embeddings_service.find_nearest_neighbors(
            "artificial intelligence", k=2, include_distances=True
        )

        assert isinstance(results, dict)
        assert "documents" in results
        assert "distances" in results
        assert len(results["documents"]) <= 2
        assert len(results["distances"]) <= 2
        assert all(isinstance(d, float) for d in results["distances"])

    def test_load_database(self, embeddings_service, sample_texts, test_dir):
        """Test loading an existing database"""
        # Create and persist a database
        embeddings_service.create_database(sample_texts)

        # Create new service instance and load existing database
        new_service = EmbeddingsService(persist_directory=str(test_dir))
        new_service.load_database()

        # Verify loaded data
        original_results = embeddings_service.similarity_search("test", k=1)
        loaded_results = new_service.similarity_search("test", k=1)
        assert original_results == loaded_results

    def test_error_handling(self, embeddings_service):
        """Test error handling for uninitialized database operations"""
        with pytest.raises(ValueError, match="Database not initialized"):
            embeddings_service.similarity_search("test")

        with pytest.raises(ValueError, match="Database not initialized"):
            embeddings_service.add_texts(["test"])

        with pytest.raises(ValueError, match="Database not initialized"):
            embeddings_service.get_collection_stats()

        non_existent_dir = Path("/non/existent/path")
        service_with_invalid_path = EmbeddingsService(
            persist_directory=str(non_existent_dir)
        )
        with pytest.raises(ValueError, match="No database found"):
            service_with_invalid_path.load_database()
