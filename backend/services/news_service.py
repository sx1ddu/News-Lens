import logging

from newsapi import NewsApiClient

from config import NEWS_API_KEY

logger = logging.getLogger(__name__)


class NewsServiceError(Exception):
    """Raised when the News API can't give us usable articles."""


class NewsService:
    """Handles all communication with the News API. Nothing else."""

    def __init__(self, api_key: str = NEWS_API_KEY):
        if not api_key:
            # We don't crash the whole app at import time - the route
            # handler decides how to respond to the user. But we do log
            # loudly so a missing key isn't a silent mystery later.
            logger.warning("NEWS_API_KEY is not set - News API calls will fail")

        self._api_key = api_key
        self._client = NewsApiClient(api_key=api_key) if api_key else None

    def search_articles(self, query: str, page_size: int = 10) -> list[dict]:
        if not self._client:
            raise NewsServiceError("NEWS_API_KEY is not configured on the server.")

        try:
            response = self._client.get_everything(
                q=query,
                language="en",
                sort_by="relevancy",
                page_size=page_size,
            )
        except Exception as error:
            # newsapi-python raises its own NewsAPIException for API-level
            # errors (bad key, rate limit, bad query) and requests-level
            # exceptions for network failures. We don't need to tell them
            # apart here - either way the user gets a clean error and the
            # real exception is logged for debugging.
            logger.error("News API request failed: %s", error)
            raise NewsServiceError(
                "Could not fetch articles from the News API "
                "(invalid key, rate limit, or network issue)."
            ) from error

        articles = response.get("articles", [])

        if not articles:
            logger.info("News API returned no articles for query=%r", query)

        return [article for article in articles if self._is_usable(article)]

    @staticmethod
    def _is_usable(article: dict) -> bool:
        """Filters out articles News API sometimes returns with missing data."""
        return bool(article.get("url")) and bool(article.get("title"))


news_service = NewsService()
