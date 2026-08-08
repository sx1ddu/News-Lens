"""
Central place for the label sets used by the two AI classification tasks.

These two tasks are DIFFERENT and must never be mixed:

  Bias   -> what political leaning the article/source appears to have
  Stance -> whether the article supports, is neutral on, or questions
            the topic the user searched for

IMPORTANT - read this before touching STANCE_LABELS:
The stance_model currently stored under backend/models/stance_model was
fine-tuned as a 4-class "headline vs. body" stance-detection model
(Agree / Discuss / Disagree / Unrelated). That is NOT the same task as
the 3-class Supports / Neutral / Questions-Critical scheme this project
requires. STANCE_LABELS below reflects the REQUIRED scheme, not what the
current model artifact actually outputs. Until a real 3-class stance
model is trained and dropped into that folder, InferenceService.predict_stance
raises StanceModelIncompatibleError instead of quietly mislabeling
predictions - see inference_service.py.
"""

BIAS_LABELS = {
    0: "Left",
    1: "Center",
    2: "Right",
}

STANCE_LABELS = {
    0: "Supports",
    1: "Neutral",
    2: "Questions / Critical",
}

# The label count the currently-loaded stance model artifact actually has.
# Used only to detect the mismatch described above - not to relabel anything.
STANCE_MODEL_EXPECTED_NUM_LABELS = len(STANCE_LABELS)
