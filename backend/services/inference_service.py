import logging

import torch

from services.model_manager import model_manager
from services.labels import (
    BIAS_LABELS,
    STANCE_LABELS,
    STANCE_MODEL_EXPECTED_NUM_LABELS,
)

logger = logging.getLogger(__name__)


class StanceModelIncompatibleError(Exception):
    """
    Raised when the stance model artifact currently on disk doesn't
    actually produce the Supports / Neutral / Questions-Critical labels
    this project requires (see services/labels.py for why).
    """


class InferenceService:
    """
    Runs the two classification models. Bias and stance are kept as two
    separate methods on purpose - they are two separate ML tasks and
    should never be collapsed into one "predict everything" method.
    """

    def __init__(self, manager=model_manager):
        self._manager = manager

    def predict_bias(self, article_text: str) -> dict:
        """Returns {"label": "Left" | "Center" | "Right", "confidence": float}."""
        return self._classify(
            text=article_text,
            tokenizer=self._manager.bias_tokenizer,
            model=self._manager.bias_model,
            labels=BIAS_LABELS,
        )

    def predict_stance(self, article_text: str) -> dict:
        """
        Returns {"label": "Supports" | "Neutral" | "Questions / Critical",
        "confidence": float}.

        Raises StanceModelIncompatibleError if the loaded stance model
        doesn't have the expected number of output classes - this can
        happen if the old 4-class Agree/Discuss/Disagree/Unrelated model
        is still the one on disk. We refuse to guess a mapping in that
        case instead of returning a mislabeled prediction.
        """
        num_labels = self._manager.stance_model.config.num_labels
        if num_labels != STANCE_MODEL_EXPECTED_NUM_LABELS:
            raise StanceModelIncompatibleError(
                f"The loaded stance model outputs {num_labels} classes, but "
                f"{STANCE_MODEL_EXPECTED_NUM_LABELS} "
                "(Supports / Neutral / Questions-Critical) are required. "
                "This model artifact needs to be replaced with a properly "
                "fine-tuned 3-class stance model."
            )

        return self._classify(
            text=article_text,
            tokenizer=self._manager.stance_tokenizer,
            model=self._manager.stance_model,
            labels=STANCE_LABELS,
        )

    def _classify(self, text: str, tokenizer, model, labels: dict) -> dict:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512,
        )
        inputs = {key: value.to(self._manager.device) for key, value in inputs.items()}

        with torch.no_grad():
            output = model(**inputs)

        probabilities = torch.softmax(output.logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class].item()

        return {
            "label": labels[predicted_class],
            "confidence": round(confidence * 100, 2),
        }


inference_service = InferenceService()
