from fastapi import APIRouter, HTTPException

from friday.api.schemas.crawl import CrawlRequest
from friday.services.crawler import WebCrawler

router = APIRouter()


@router.post("/crawl")
async def crawl_site(request: CrawlRequest):
    try:
        crawler = WebCrawler(persist_dir=request.persist_dir, provider=request.provider)

        pages_data = crawler.crawl(
            url=request.url,
            max_pages=request.max_pages,
            same_domain=request.same_domain,
        )

        stats = crawler.get_embeddings_stats()

        return {
            "pages_processed": len(pages_data),
            "total_documents": stats["total_documents"],
            "embedding_dimension": stats["embedding_dimension"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
