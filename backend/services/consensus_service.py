"""
Builds a short "what these articles are saying" preview for a stance group.

This is intentionally EXTRACTIVE, not a new AI-generated summary: it pulls
the first sentence from each article's existing summary and joins them.
We do this on purpose so we never claim the system "understood the
consensus" when it's really just stitching together sentences we already
generated. A student should be able to explain exactly where every word
in a consensus preview came from.
"""

_MAX_ARTICLES_IN_PREVIEW = 3


class ConsensusService:
    def build_consensus(self, articles: list[dict]) -> str:
        if not articles:
            return ""

        sentences = []
        for article in articles[:_MAX_ARTICLES_IN_PREVIEW]:
            summary = (article.get("summary") or "").strip()
            if not summary:
                continue

            first_sentence = summary.split(". ")[0].rstrip(".") + "."
            sentences.append(first_sentence)

        return " ".join(sentences)


consensus_service = ConsensusService()
