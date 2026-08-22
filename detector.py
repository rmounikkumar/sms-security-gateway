from transformers import pipeline
from config import MODEL_NAME

_classifier = None


def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline("text-classification", model=MODEL_NAME)
    return _classifier


LABEL_MAP = {"LABEL_0": "HAM", "LABEL_1": "SPAM"}


def classify_message(message):
    classifier = get_classifier()
    result = classifier(message)[0]
    return {
        "label": LABEL_MAP.get(result["label"], result["label"]),
        "confidence": float(result["score"]),
    }
