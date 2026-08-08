"""
Runs the full per-article pipeline: extract text -> summarize -> predict
bias -> predict stance -> build the final article result.

Kept as plain functions (not a class) since it has no state of its own -
it just wires the other services together in order.
"""

import logging

from services.article_service import article_service, ArticleExtractionError
from services.summary_service import summary_service
from services.inference_service import inference_service, StanceModelIncompatibleError

logger = logging.getLogger(__name__)


def analyze_article(raw_article: dict) -> dict:
    """
    Takes one raw article dict from the News API and returns a fully
    analyzed result dict (title, summary, bias, stance, ...).

    Raises ArticleExtractionError if the article's text can't be fetched
    or is unusable - the caller is expected to catch this per-article so
    one bad URL doesn't fail the whole search.
    """
    url = raw_article["url"]

    article_text = article_service.extract_text(url)

    summary = summary_service.summarize(article_text)
    bias = inference_service.predict_bias(article_text)

    stance = None
    try:
        stance = inference_service.predict_stance(article_text)
    except StanceModelIncompatibleError as error:
        # This will be true for every article until a real 3-class
        # stance model is trained - we log once per article rather than
        # crash, and let the route report it as a known limitation.
        logger.debug("Stance prediction unavailable: %s", error)

    return {
        "title": raw_article["title"],
        "source": raw_article.get("source", {}).get("name", "Unknown"),
        "url": url,
        "image": raw_article.get("urlToImage"),
        "published": raw_article.get("publishedAt"),
        "summary": summary,
        "bias": bias,
        "stance": stance,
    }
