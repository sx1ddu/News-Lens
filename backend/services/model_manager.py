import logging

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import BIAS_MODEL_PATH, STANCE_MODEL_PATH

logger = logging.getLogger(__name__)


class ModelLoadError(Exception):
    """Raised when a model or tokenizer can't be loaded at startup."""


class ModelManager:
    """
    Loads and holds both classification models (and their own tokenizers)
    in memory, once, at startup.

    Each model gets its OWN tokenizer. Reusing one tokenizer for both
    models is only safe if they share an identical vocabulary, and we
    don't want to depend on that assumption silently being true.
    """

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Using device: %s", self.device)

        self.bias_tokenizer, self.bias_model = self._load_model(
            "bias", BIAS_MODEL_PATH
        )
        self.stance_tokenizer, self.stance_model = self._load_model(
            "stance", STANCE_MODEL_PATH
        )

        logger.info("Models loaded successfully")

    def _load_model(self, name: str, path):
        if not path.exists():
            raise ModelLoadError(
                f"{name} model folder not found at '{path}'. "
                "Did you forget to place the trained model weights there?"
            )

        try:
            tokenizer = AutoTokenizer.from_pretrained(path)
            model = AutoModelForSequenceClassification.from_pretrained(path)
        except Exception as error:
            raise ModelLoadError(
                f"Failed to load the {name} model from '{path}': {error}"
            ) from error

        model.to(self.device)
        model.eval()

        return tokenizer, model


# Loaded once when this module is first imported (app startup).
model_manager = ModelManager()
