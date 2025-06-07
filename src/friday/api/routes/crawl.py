import structlog
from fastapi import APIRouter, HTTPException

from friday.api.schemas.crawl import CrawlRequest
from friday.services.crawler import WebCrawler
from friday.services.embeddings import EmbeddingsService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/crawl")
async def crawl_site(request: CrawlRequest):
    try:
        import asyncio
        
        crawler = WebCrawler(
            max_pages=request.max_pages, same_domain_only=request.same_domain
        )

        # Run crawler in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        pages_data = await loop.run_in_executor(None, crawler.crawl, request.url)

        import time
        
        # Use a unique collection name to avoid embedding dimension conflicts
        collection_name = f"crawl_{int(time.time())}"
        
        embeddings_service = EmbeddingsService(
            provider=request.provider, persist_directory="./data/chroma"
        )

        texts = []
        metadata = []

        for page in pages_data:
            texts.append(page["text"])
            metadata.append(
                {"source": page["url"], "type": "webpage", "title": page["title"]}
            )

        # Run embeddings creation in thread pool as well with unique collection name
        await loop.run_in_executor(None, embeddings_service.create_database, texts, metadata, collection_name)

        stats = embeddings_service.get_collection_stats()

        return {
            "pages_processed": len(pages_data),
            "total_documents": stats["total_documents"],
            "embedding_dimension": stats["embedding_dimension"],
        }

    except Exception as e:
        logger.error(f"Error in crawl endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
