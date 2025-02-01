from typing import Literal

from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

ModelProvider = Literal["vertex", "openai", "ollama"]


def get_llm_client(provider: ModelProvider):
    """
    Get the LLM client based on the provider
    """
    if provider == "vertex":
        return VertexAI(
            model_name="gemini-pro",
            kwargs={"temperature": 0.0, "max_tokens": 1024, "timeout": None},
        )
    elif provider == "openai":
        return ChatOpenAI(
            model_name="gpt-4-turbo-preview",
            temperature=0,
            max_tokens=1024,
            timeout=None,
            max_retries=2,
        )
    elif provider == "ollama":
        return ChatOllama(
            model="llama3.1",
            temperature=0,
            max_tokens=1024,
            timeout=None,
        )
    else:
        raise ValueError("Unsupported provider. Use 'vertex', 'openai' or 'ollama'.")


def get_embedding_client(provider: str):
    """
    Get the embeddings client based on the provider
    """
    providers = {
        "vertex": lambda: VertexAIEmbeddings(model_name="text-embedding-005"),
        "openai": lambda: OpenAIEmbeddings(model="text-embedding-3-small"),
        "ollama": lambda: OllamaEmbeddings(model="llama3"),
    }
    try:
        return providers[provider]()
    except KeyError:
        raise ValueError("Unsupported provider. Use 'vertex', 'openai' or 'ollama'.")
