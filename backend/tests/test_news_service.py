import pytest

from services.news_service import NewsService, NewsServiceError


class _FakeClient:
    def __init__(self, articles=None, raise_error=False):
        self._articles = articles or []
        self._raise_error = raise_error

    def get_everything(self, **kwargs):
        if self._raise_error:
            raise RuntimeError("News API rate limit exceeded")
        return {"articles": self._articles}


def test_missing_api_key_raises():
    service = NewsService(api_key=None)
    with pytest.raises(NewsServiceError):
        service.search_articles("ai policy")


def test_api_failure_raises_clean_error():
    service = NewsService(api_key="fake-key")
    service._client = _FakeClient(raise_error=True)

    with pytest.raises(NewsServiceError):
        service.search_articles("ai policy")


def test_filters_out_articles_missing_url_or_title():
    service = NewsService(api_key="fake-key")
    service._client = _FakeClient(
        articles=[
            {"url": "https://a.com", "title": "Good article"},
            {"url": "", "title": "Missing URL"},
            {"url": "https://b.com", "title": ""},
        ]
    )

    results = service.search_articles("ai policy")
    assert len(results) == 1
    assert results[0]["title"] == "Good article"


def test_empty_results_returns_empty_list():
    service = NewsService(api_key="fake-key")
    service._client = _FakeClient(articles=[])

    results = service.search_articles("a very obscure query")
    assert results == []
