import requests
from sqlmodel import Session

from app.core.celery_config import celery_app
from app.core.database import engine
from app.models.bookmark_model import Bookmark


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 5},
)
def fetch_metadata(self, bookmark_id: str):
    with Session(engine) as db:
        bookmark = db.get(Bookmark, bookmark_id)
        if not bookmark:
            return

        try:
            response = requests.get(bookmark.url, timeout=5)
            if response.ok:
                bookmark.title = bookmark.title or bookmark.url
                db.add(bookmark)
                db.commit()
        except Exception:
            raise
