import logging

from transformers import pipeline, AutoTokenizer

logger = logging.getLogger(__name__)

_MODEL_NAME = "facebook/bart-large-cnn"
_MAX_INPUT_TOKENS = 1024  # BART's hard limit
_SHORT_ARTICLE_WORD_THRESHOLD = 120


class SummaryService:
    """
    Generates a short summary of an article using BART.

    Loads the model once at startup (not per-request) since loading a
    transformer pipeline is expensive.
    """

    def __init__(self):
        self._tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        self._summarizer = pipeline("summarization", model=_MODEL_NAME)

    def summarize(self, text: str) -> str:
        text = (text or "").strip()

        if not text:
            return ""

        if len(text.split()) < _SHORT_ARTICLE_WORD_THRESHOLD:
            # Short articles are already summary-length; running them
            # through BART would just reword them for no benefit.
            return text

        try:
            # BART can only accept _MAX_INPUT_TOKENS tokens. We truncate
            # to token length ONCE here, then summarize that truncated
            # text directly - we don't decode-and-resummarize, since that
            # was silently truncating twice for no reason.
            truncated_text = self._truncate_to_token_limit(text)

            summary = self._summarizer(
                truncated_text,
                max_length=120,
                min_length=40,
                do_sample=False,
            )
            return summary[0]["summary_text"]

        except Exception as error:
            logger.error("Summarization failed: %s", error)
            # Fall back to a simple text snippet so one bad article
            # doesn't fail the whole request - this is clearly NOT a
            # real summary, just a safe degraded result.
            return text[:400].rsplit(" ", 1)[0] + "..."

    def _truncate_to_token_limit(self, text: str) -> str:
        token_ids = self._tokenizer(
            text,
            max_length=_MAX_INPUT_TOKENS,
            truncation=True,
        )["input_ids"]

        return self._tokenizer.decode(token_ids, skip_special_tokens=True)


summary_service = SummaryService()
