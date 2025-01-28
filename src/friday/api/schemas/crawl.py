from openai import BaseModel


class CrawlRequest(BaseModel):
    url: str
    provider: str = "vertex"
    max_pages: int = 10
    same_domain: bool = True


class CrawlResponse(BaseModel):
    pages_processed: int
    total_documents: int
    embedding_dimension: int
