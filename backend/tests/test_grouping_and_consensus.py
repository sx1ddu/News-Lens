from services.grouping_service import GroupingService
from services.consensus_service import ConsensusService


def _article(bias_label, stance_label=None, summary="Some summary. More text."):
    return {
        "bias": {"label": bias_label, "confidence": 90.0},
        "stance": {"label": stance_label, "confidence": 80.0} if stance_label else None,
        "summary": summary,
    }


def test_group_by_bias_buckets_correctly():
    grouping = GroupingService()
    articles = [_article("Left"), _article("Right"), _article("Center"), _article("Left")]

    groups = grouping.group_by_bias(articles)

    assert len(groups["left"]) == 2
    assert len(groups["right"]) == 1
    assert len(groups["center"]) == 1


def test_group_by_stance_ignores_articles_without_stance():
    grouping = GroupingService()
    articles = [
        _article("Left", "Supports"),
        _article("Right", None),
        _article("Center", "Neutral"),
    ]

    groups = grouping.group_by_stance(articles)

    assert len(groups["supports"]) == 1
    assert len(groups["neutral"]) == 1
    assert len(groups["critical"]) == 0


def test_consensus_is_extractive_and_bounded():
    consensus = ConsensusService()
    articles = [
        _article("Left", "Supports", summary="First point here. Extra detail."),
        _article("Center", "Supports", summary="Second point here. Extra detail."),
    ]

    result = consensus.build_consensus(articles)

    assert "First point here." in result
    assert "Second point here." in result


def test_consensus_empty_group_returns_empty_string():
    consensus = ConsensusService()
    assert consensus.build_consensus([]) == ""
