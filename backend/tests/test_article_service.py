import pytest

from services.article_service import ArticleService, ArticleExtractionError


def test_deduplicate_removes_same_url():
    articles = [
        {"url": "https://a.com/x", "title": "First"},
        {"url": "https://a.com/x", "title": "Duplicate URL, different case"},
    ]
    result = ArticleService.deduplicate(articles)
    assert len(result) == 1


def test_deduplicate_removes_same_title():
    articles = [
        {"url": "https://a.com/1", "title": "Same Title"},
        {"url": "https://b.com/2", "title": "same title"},
    ]
    result = ArticleService.deduplicate(articles)
    assert len(result) == 1


def test_deduplicate_keeps_distinct_articles():
    articles = [
        {"url": "https://a.com/1", "title": "One"},
        {"url": "https://b.com/2", "title": "Two"},
    ]
    result = ArticleService.deduplicate(articles)
    assert len(result) == 2


def test_extract_text_raises_when_download_fails(monkeypatch):
    service = ArticleService()
    monkeypatch.setattr(
        "services.article_service.trafilatura.fetch_url", lambda url, timeout: None
    )

    with pytest.raises(ArticleExtractionError):
        service.extract_text("https://example.com/broken")


def test_extract_text_raises_when_too_short(monkeypatch):
    service = ArticleService()
    monkeypatch.setattr(
        "services.article_service.trafilatura.fetch_url",
        lambda url, timeout: "<html>fake page</html>",
    )
    monkeypatch.setattr(
        "services.article_service.trafilatura.extract", lambda html: "Too short."
    )

    with pytest.raises(ArticleExtractionError):
        service.extract_text("https://example.com/thin")


def test_extract_text_returns_clean_text(monkeypatch):
    service = ArticleService()
    long_text = "word " * 60
    monkeypatch.setattr(
        "services.article_service.trafilatura.fetch_url",
        lambda url, timeout: "<html>fake page</html>",
    )
    monkeypatch.setattr(
        "services.article_service.trafilatura.extract", lambda html: long_text
    )

    result = service.extract_text("https://example.com/ok")
    assert result == long_text.strip()
