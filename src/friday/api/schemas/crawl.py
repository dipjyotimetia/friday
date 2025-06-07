from pydantic import BaseModel


class CrawlRequest(BaseModel):
    url: str
    provider: str = "openai"
    max_pages: int = 10
    same_domain: bool = True


class CrawlResponse(BaseModel):
    pages_processed: int
    total_documents: int
    embedding_dimension: int
