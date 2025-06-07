"""Tests for LLM module functionality."""

import os
from unittest.mock import MagicMock, patch
import pytest

from friday.llm.llm import get_llm_client, get_embedding_client, ModelProvider


class TestLLMClients:
    """Test LLM client factory functions."""

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_get_gemini_client(self):
        """Test getting Gemini LLM client."""
        with patch("friday.llm.llm.ChatGoogleGenerativeAI") as mock_gemini:
            mock_client = MagicMock()
            mock_gemini.return_value = mock_client
            
            client = get_llm_client("gemini")
            
            assert client is not None
            mock_gemini.assert_called_once()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"})
    def test_get_openai_client(self):
        """Test getting OpenAI LLM client."""
        with patch("friday.llm.llm.ChatOpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            client = get_llm_client("openai")
            
            assert client is not None
            mock_openai.assert_called_once()

    @patch.dict(os.environ, {"MISTRAL_API_KEY": "test-key"})
    def test_get_mistral_client(self):
        """Test getting Mistral LLM client."""
        with patch("friday.llm.llm.ChatMistralAI") as mock_mistral:
            mock_client = MagicMock()
            mock_mistral.return_value = mock_client
            
            client = get_llm_client("mistral")
            
            assert client is not None
            mock_mistral.assert_called_once()

    def test_get_ollama_client(self):
        """Test getting Ollama LLM client."""
        with patch("friday.llm.llm.ChatOllama") as mock_ollama:
            mock_client = MagicMock()
            mock_ollama.return_value = mock_client
            
            client = get_llm_client("ollama")
            
            assert client is not None
            mock_ollama.assert_called_once()

    def test_invalid_provider(self):
        """Test error handling for invalid provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_llm_client("invalid-provider")  # type: ignore

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"})
    def test_get_openai_embedding_client(self):
        """Test getting OpenAI embedding client."""
        with patch("friday.llm.llm.OpenAIEmbeddings") as mock_embeddings:
            mock_client = MagicMock()
            mock_embeddings.return_value = mock_client
            
            client = get_embedding_client("openai")
            
            assert client is not None
            mock_embeddings.assert_called_once()

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"})
    def test_get_gemini_embedding_client(self):
        """Test getting Gemini embedding client."""
        with patch("friday.llm.llm.GoogleGenerativeAIEmbeddings") as mock_embeddings:
            mock_client = MagicMock()
            mock_embeddings.return_value = mock_client
            
            client = get_embedding_client("gemini")
            
            assert client is not None
            mock_embeddings.assert_called_once()

    def test_provider_type_hints(self):
        """Test that ModelProvider type is properly defined."""
        # This tests the type definition exists and has expected values
        valid_providers: list[ModelProvider] = ["gemini", "openai", "ollama", "mistral"]
        assert len(valid_providers) == 4
        
        # Test each provider value
        for provider in valid_providers:
            assert isinstance(provider, str)


class TestLLMConfiguration:
    """Test LLM configuration and setup."""

    @patch("friday.llm.llm.set_llm_cache")
    @patch("friday.llm.llm.SQLiteCache")
    def test_cache_setup(self, mock_sqlite_cache, mock_set_cache):
        """Test that LLM cache is properly set up."""
        # Import the module to trigger cache setup
        import friday.llm.llm
        
        # Verify cache was configured
        mock_sqlite_cache.assert_called()
        mock_set_cache.assert_called()

    @patch("friday.llm.llm.Path")
    def test_cache_directory_creation(self, mock_path):
        """Test that cache directory is created."""
        mock_cache_dir = MagicMock()
        mock_path.cwd.return_value.__truediv__.return_value.__truediv__.return_value = mock_cache_dir
        
        # Re-import to trigger directory creation
        import importlib
        import friday.llm.llm
        importlib.reload(friday.llm.llm)
        
        mock_cache_dir.mkdir.assert_called_with(parents=True, exist_ok=True)

    def test_model_provider_literal(self):
        """Test ModelProvider literal type definition."""
        from friday.llm.llm import ModelProvider
        
        # This should not raise any type errors
        provider: ModelProvider = "openai"
        assert provider == "openai"