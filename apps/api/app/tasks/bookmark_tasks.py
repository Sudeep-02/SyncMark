import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sqlmodel import Session

from app.core.celery_config import celery_app
from app.core.database import engine
from app.models.bookmark_model import Bookmark


@celery_app.task(
    bind=True,
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def fetch_metadata(self, bookmark_id: str):
    with Session(engine) as db:
        bookmark = db.get(Bookmark, bookmark_id)
        if not bookmark:
            return

        try:
            response = requests.get(
                bookmark.url,
                timeout=5,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; SyncmarkBot/1.0)"
                },
            )

            # Only process HTML responses
            content_type = response.headers.get("Content-Type", "")
            if not response.ok or "text/html" not in content_type:
                return

            soup = BeautifulSoup(response.text, "html.parser")

            # ---------- TITLE ----------
            title_tag = soup.find("title")
            if title_tag and title_tag.string:
                title_value = str(title_tag.string).strip()
                if not bookmark.title:
                    bookmark.title = title_value


            # ---------- DESCRIPTION ----------
            description_tag = soup.find("meta", attrs={"name": "description"})
            if description_tag:
                content = description_tag.get("content")
                if isinstance(content, str):
                    bookmark.description = content.strip()


            # ---------- OG IMAGE ----------
            og_image_tag = soup.find("meta", attrs={"property": "og:image"})
            if og_image_tag:
                content = og_image_tag.get("content")
                if isinstance(content, str):
                    bookmark.cover_image_url = urljoin(bookmark.url, content)


            # ---------- FAVICON ----------
            icon_tag = soup.find("link", attrs={"rel": True})
            if icon_tag:
                rel_value = icon_tag.get("rel")
                href = icon_tag.get("href")

                if isinstance(rel_value, list):
                    rel_string = " ".join(rel_value).lower()
                elif isinstance(rel_value, str):
                    rel_string = rel_value.lower()
                else:
                    rel_string = ""

                if "icon" in rel_string and isinstance(href, str):
                    bookmark.favicon_url = urljoin(bookmark.url, href)
            db.add(bookmark)
            db.commit()

        except requests.RequestException as exc:
            raise exc