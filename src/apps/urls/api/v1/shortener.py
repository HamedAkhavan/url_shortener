
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from apps.urls.models import URLShortener
from apps.urls.schema import (
    URLShortenerRequest,
    URLShortenerResponse,
    URLShortenerStatsResponse,
)
from core.database import create_session
from core.utils import random_string

router = APIRouter(
    tags=["shortener"],
)


@router.post(
    "/shorten",
    response_model=URLShortenerResponse,
)
async def shorten_url(data: URLShortenerRequest, db: Session = Depends(create_session)):
    """Create a short code for the given original URL."""
    short_code = random_string()
    url_entry = URLShortener.objects.create(
        session=db,
        original_url=str(data.original_url),
        short_code=short_code,
    )
    return url_entry


@router.get(
    "/{short_code}",
)
async def redirect_to_original_url(
    short_code: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(create_session),
):
    """Redirect to the original URL based on the short code."""
    url_entry = URLShortener.objects.get(db, short_code=short_code)
    background_tasks.add_task(url_entry.increment_access_count, db)

    return RedirectResponse(url_entry.original_url)


@router.get(
    "/stats/{short_code}",
    response_model=URLShortenerStatsResponse,
)
async def get_url_stats(
    short_code: str,
    db: Session = Depends(create_session),
):
    """Get statistics for the given short code."""
    url_entry = URLShortener.objects.get(db, short_code=short_code)
    return url_entry
