"""Tests for test case generator functionality."""

from unittest.mock import MagicMock, patch
import pytest

from friday.services.test_generator import TestCaseGenerator


class TestTestCaseGenerator:
    """Test TestCaseGenerator class functionality."""

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    def test_init_default_provider(self, mock_embeddings, mock_llm):
        """Test TestCaseGenerator initialization with default provider."""
        mock_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        
        generator = TestCaseGenerator()
        
        mock_llm.assert_called_once_with("openai")
        mock_embeddings.assert_called_once_with(provider="openai")
        assert generator.llm is not None
        assert generator.embeddings_service is not None

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    def test_init_custom_provider(self, mock_embeddings, mock_llm):
        """Test TestCaseGenerator initialization with custom provider."""
        mock_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        
        generator = TestCaseGenerator(provider="gemini")
        
        mock_llm.assert_called_once_with("gemini")
        mock_embeddings.assert_called_once_with(provider="gemini")

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    def test_template_structure(self, mock_embeddings, mock_llm):
        """Test that the prompt template is properly structured."""
        mock_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        
        generator = TestCaseGenerator()
        
        # Check that template contains expected placeholders
        assert "{requirement}" in generator.template
        assert "{context}" in generator.template
        assert "Test Case ID" in generator.template
        assert "Title" in generator.template
        assert "Test Steps" in generator.template
        assert "Expected Results" in generator.template

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    def test_template_format(self, mock_embeddings, mock_llm):
        """Test that template can be formatted with required parameters."""
        mock_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        
        generator = TestCaseGenerator()
        
        # Test template formatting
        formatted = generator.template.format(
            requirement="Test user login functionality",
            context="User authentication system with OAuth2"
        )
        
        assert "Test user login functionality" in formatted
        assert "User authentication system with OAuth2" in formatted
        assert "{requirement}" not in formatted
        assert "{context}" not in formatted

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    @patch("friday.services.test_generator.PromptTemplate")
    def test_prompt_template_integration(self, mock_prompt_template, mock_embeddings, mock_llm):
        """Test integration with LangChain PromptTemplate."""
        mock_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        mock_template = MagicMock()
        mock_prompt_template.return_value = mock_template
        
        generator = TestCaseGenerator()
        
        # Verify PromptTemplate is imported (should not raise ImportError)
        from langchain_core.prompts import PromptTemplate
        assert PromptTemplate is not None

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    def test_embeddings_service_integration(self, mock_embeddings_class, mock_llm):
        """Test integration with EmbeddingsService."""
        mock_llm.return_value = MagicMock()
        mock_embeddings_instance = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings_instance
        
        generator = TestCaseGenerator(provider="gemini")
        
        # Verify EmbeddingsService was initialized with correct provider
        mock_embeddings_class.assert_called_once_with(provider="gemini")
        assert generator.embeddings_service == mock_embeddings_instance

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    def test_llm_client_integration(self, mock_embeddings, mock_llm_client):
        """Test integration with LLM client."""
        mock_llm_instance = MagicMock()
        mock_llm_client.return_value = mock_llm_instance
        mock_embeddings.return_value = MagicMock()
        
        generator = TestCaseGenerator(provider="mistral")
        
        # Verify LLM client was created with correct provider
        mock_llm_client.assert_called_once_with("mistral")
        assert generator.llm == mock_llm_instance


class TestTestCaseGeneratorEdgeCases:
    """Test edge cases and error conditions."""

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    def test_empty_requirement_template(self, mock_embeddings, mock_llm):
        """Test template with empty requirement."""
        mock_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        
        generator = TestCaseGenerator()
        
        formatted = generator.template.format(
            requirement="",
            context="Some context"
        )
        
        # Should not crash and should handle empty requirement
        assert "Requirement:" in formatted
        assert "Some context" in formatted

    @patch("friday.services.test_generator.get_llm_client")
    @patch("friday.services.test_generator.EmbeddingsService")
    def test_none_values_template(self, mock_embeddings, mock_llm):
        """Test template with None values."""
        mock_llm.return_value = MagicMock()
        mock_embeddings.return_value = MagicMock()
        
        generator = TestCaseGenerator()
        
        # Should handle None values gracefully
        formatted = generator.template.format(
            requirement=str(None),
            context=str(None)
        )
        
        assert "None" in formatted