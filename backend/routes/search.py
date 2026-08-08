import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, HTTPException

from config import ARTICLE_LIMIT
from schemas import SearchRequest, SearchResponse, StanceGroup
from services.news_service import news_service, NewsServiceError
from services.article_service import article_service, ArticleExtractionError
from services.article_analysis_service import analyze_article
from services.grouping_service import grouping_service
from services.consensus_service import consensus_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Article extraction is network-bound (downloading a web page), so a small
# thread pool lets us fetch several articles at once instead of one at a
# time. We do NOT parallelize the model inference steps - those run on
# the main thread, sequentially, which keeps the pipeline easy to follow.
_EXTRACTION_WORKERS = 5


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    try:
        raw_articles = news_service.search_articles(
            query=request.query, page_size=min(request.page_size, ARTICLE_LIMIT)
        )
    except NewsServiceError as error:
        logger.error("News service failed for query=%r: %s", request.query, error)
        raise HTTPException(status_code=502, detail=str(error))

    raw_articles = article_service.deduplicate(raw_articles)

    results, failed_count = _analyze_all(raw_articles)

    stance_unavailable_reason = None
    if results and all(article["stance"] is None for article in results):
        stance_unavailable_reason = (
            "The stance model currently loaded is not the required 3-class "
            "Supports/Neutral/Questions-Critical model, so stance "
            "predictions are unavailable. See services/labels.py."
        )

    bias_groups = grouping_service.group_by_bias(results)
    stance_groups = None

    if stance_unavailable_reason is None:
        raw_stance_groups = grouping_service.group_by_stance(results)
        stance_groups = {
            key: StanceGroup(
                count=len(articles),
                consensus=consensus_service.build_consensus(articles),
                articles=articles,
            )
            for key, articles in raw_stance_groups.items()
        }

    return SearchResponse(
        topic=request.query,
        total_articles=len(raw_articles),
        processed_articles=len(results),
        failed_articles=failed_count,
        articles=results,
        bias_groups=bias_groups,
        stance_groups=stance_groups,
        stance_unavailable_reason=stance_unavailable_reason,
    )


def _analyze_all(raw_articles: list[dict]) -> tuple[list[dict], int]:
    """
    Runs analyze_article() for every raw article. Extraction happens
    concurrently; a failure on one article is logged and skipped rather
    than failing the whole request.
    """
    results = []
    failed_count = 0

    with ThreadPoolExecutor(max_workers=_EXTRACTION_WORKERS) as executor:
        future_to_article = {
            executor.submit(analyze_article, article): article
            for article in raw_articles
        }

        for future in as_completed(future_to_article):
            article = future_to_article[future]
            try:
                results.append(future.result())
            except ArticleExtractionError as error:
                failed_count += 1
                logger.info(
                    "Skipping article '%s' (%s): %s",
                    article.get("title"),
                    article.get("url"),
                    error,
                )
            except Exception as error:
                # Anything unexpected (model error, etc.) - don't let one
                # article take down the whole request.
                failed_count += 1
                logger.error(
                    "Unexpected error analyzing article '%s': %s",
                    article.get("title"),
                    error,
                )

    return results, failed_count
