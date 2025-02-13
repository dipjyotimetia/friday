"""
This module provides a unified interface for different Language Learning Model (LLM) providers
and their embedding capabilities.

It supports multiple LLM providers including:
- Google's Gemini
- OpenAI
- Ollama
- Mistral

The module handles caching of LLM responses using SQLite and provides factory methods
to create LLM and embedding clients.
"""

from pathlib import Path
from typing import Callable, Literal

from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from friday.config.config import GOOGLE_API_KEY, MISTRAL_API_KEY, OPENAI_API_KEY

# Setup cache directory for LLM responses
cache_dir = Path.cwd() / "data" / "cache"
cache_dir.mkdir(parents=True, exist_ok=True)
cache_path = cache_dir / "langchain.db"

set_llm_cache(SQLiteCache(database_path=str(cache_path)))

ModelProvider = Literal["gemini", "openai", "ollama", "mistral"]

LLMClient = Callable[[], object]
EmbeddingClient = Callable[[], object]


_llm_providers: dict[ModelProvider, LLMClient] = {
    "gemini": lambda: ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        convert_system_message_to_human=True,
        temperature=0,
        max_tokens=1024,
        timeout=None,
        max_retries=2,
        cache=True,
        api_key=GOOGLE_API_KEY,
    ),
    "openai": lambda: ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=1024,
        timeout=None,
        max_retries=2,
        cache=True,
        api_key=OPENAI_API_KEY,
    ),
    "ollama": lambda: ChatOllama(
        model="llama3.3",
        temperature=0,
        max_tokens=1024,
        timeout=None,
        cache=True,
        api_key=None,
    ),
    "mistral": lambda: ChatMistralAI(
        model="Codestral",
        temperature=0,
        max_tokens=1024,
        timeout=None,
        cache=True,
        api_key=MISTRAL_API_KEY,
    ),
}


def get_llm_client(provider: ModelProvider) -> object:
    """
    Creates and returns an LLM client instance based on the specified provider.

    Args:
        provider (ModelProvider): The name of the LLM provider to use.
            Must be one of: 'gemini', 'openai', 'ollama', or 'mistral'.

    Returns:
        object: An instance of the LLM client for the specified provider.

    Raises:
        ValueError: If an unsupported provider is specified.

    Example:
        >>> llm = get_llm_client("gemini")
        >>> response = llm.generate("What is Python?")
    """
    try:
        llm_client_factory = _llm_providers[provider]
        return llm_client_factory()
    except KeyError:
        raise ValueError(
            "Unsupported provider. Use 'gemini', 'openai', 'ollama' or 'mistral'."
        )


_embedding_providers: dict[ModelProvider, EmbeddingClient] = {
    "gemini": lambda: GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", api_key=GOOGLE_API_KEY
    ),
    "openai": lambda: OpenAIEmbeddings(
        model="text-embedding-3-small", api_key=OPENAI_API_KEY
    ),
    "ollama": lambda: OllamaEmbeddings(model="llama3"),
    "mistral": lambda: MistralAIEmbeddings(
        model="mistral-embed", api_key=MISTRAL_API_KEY
    ),
}


def get_embedding_client(provider: ModelProvider) -> object:
    """
    Creates and returns an embedding client instance based on the specified provider.

    Args:
        provider (ModelProvider): The name of the embedding provider to use.
            Must be one of: 'gemini', 'openai', 'ollama', or 'mistral'.

    Returns:
        object: An instance of the embedding client for the specified provider.

    Raises:
        ValueError: If an unsupported provider is specified.

    Example:
        >>> embedding_client = get_embedding_client("openai")
        >>> embeddings = embedding_client.embed_documents(["Hello, world!"])
    """
    try:
        embedding_client_factory = _embedding_providers[provider]
        return embedding_client_factory()
    except KeyError:
        raise ValueError(
            "Unsupported provider. Use 'gemini', 'openai', 'ollama' or 'mistral'."
        )
