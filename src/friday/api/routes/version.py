from fastapi import APIRouter

from friday.version import __version__

router = APIRouter()


@router.get("/version")
def get_version():
    return {"version": __version__}
