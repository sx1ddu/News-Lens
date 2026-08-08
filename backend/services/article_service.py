import logging

import trafilatura

from config import ARTICLE_FETCH_TIMEOUT, MIN_ARTICLE_WORDS

logger = logging.getLogger(__name__)


class ArticleExtractionError(Exception):
    """Raised when an article's full text can't be extracted or is unusable."""


class ArticleService:
    """Downloads a news article's page and pulls out the clean article text."""

    def extract_text(self, url: str) -> str:
        """
        Returns the cleaned article text, or raises ArticleExtractionError.
        Callers should catch this per-article so one bad URL doesn't take
        down the whole search request.
        """
        downloaded = self._download(url)

        text = trafilatura.extract(downloaded)

        if not text or not text.strip():
            raise ArticleExtractionError("No readable text found on the page.")

        text = text.strip()
        word_count = len(text.split())

        if word_count < MIN_ARTICLE_WORDS:
            # Very short "articles" are usually paywalls, cookie notices,
            # or "enable JavaScript" stubs, not real content.
            raise ArticleExtractionError(
                f"Extracted text is too short ({word_count} words) to be a "
                "real article - likely a paywall or loading page."
            )

        return text

    def _download(self, url: str) -> str:
        try:
            downloaded = trafilatura.fetch_url(url, timeout=ARTICLE_FETCH_TIMEOUT)
        except Exception as error:
            raise ArticleExtractionError(f"Failed to download page: {error}") from error

        if downloaded is None:
            raise ArticleExtractionError("Page could not be downloaded.")

        return downloaded

    @staticmethod
    def deduplicate(articles: list[dict]) -> list[dict]:
        """
        Removes articles that share the same URL or the same normalized
        title. News API frequently returns the same wire-service story
        from multiple outlets.
        """
        seen_urls = set()
        seen_titles = set()
        unique_articles = []

        for article in articles:
            url = (article.get("url") or "").strip().lower()
            title = (article.get("title") or "").strip().lower()

            if url in seen_urls or title in seen_titles:
                continue

            seen_urls.add(url)
            seen_titles.add(title)
            unique_articles.append(article)

        return unique_articles


article_service = ArticleService()
