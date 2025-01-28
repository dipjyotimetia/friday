import logging
from fastapi import APIRouter, HTTPException

from friday.api.schemas.crawl import CrawlRequest
from friday.services.crawler import WebCrawler
from friday.services.embeddings import EmbeddingsService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/crawl")
async def crawl_site(request: CrawlRequest):
    try:
        crawler = WebCrawler(
            max_pages=request.max_pages, same_domain_only=request.same_domain
        )

        pages_data = crawler.crawl(request.url)
        embeddings_service = EmbeddingsService(provider=request.provider)

        texts = []
        metadata = []

        for page in pages_data:
            texts.append(page["text"])
            metadata.append(
                {"source": page["url"], "type": "webpage", "title": page["title"]}
            )

        embeddings_service.create_database(texts, metadata)

        stats = embeddings_service.get_collection_stats()

        return {
            "pages_processed": len(pages_data),
            "total_documents": stats["total_documents"],
            "embedding_dimension": stats["embedding_dimension"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
