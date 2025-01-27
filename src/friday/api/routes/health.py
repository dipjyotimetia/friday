from fastapi import APIRouter

from friday.version import __version__

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": __version__}
