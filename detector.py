import os
import re

LABEL_MAP = {0: "HAM", 1: "SPAM"}

SUSPICIOUS_WORDS = [
    "urgent", "verify", "account suspended", "click now", "winner",
    "prize", "claim", "password", "otp", "free", "congratulations",
    "limited time", "act now", "bank", "confirm", "unlock", "expir",
]

_backend = None


def _detect_backend():
    global _backend
    if _backend is not None:
        return _backend

    onnx_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "onnx_model", "model.onnx"
    )

    if os.path.exists(onnx_path):
        try:
            from onnxruntime import InferenceSession
            _backend = "onnx"
            return _backend
        except ImportError:
            pass

    try:
        import torch
        from transformers import pipeline
        _backend = "pytorch"
        return _backend
    except ImportError:
        pass

    _backend = "rule-based"
    return _backend


def classify_message(message):
    backend = _detect_backend()

    if backend == "onnx":
        return _classify_onnx(message)
    elif backend == "pytorch":
        return _classify_pytorch(message)
    else:
        return _classify_rule(message)


_onnx_session = None
_onnx_tokenizer = None


def _classify_onnx(message):
    global _onnx_session, _onnx_tokenizer

    if _onnx_session is None:
        from onnxruntime import InferenceSession
        from transformers import AutoTokenizer

        onnx_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "onnx_model"
        )
        _onnx_session = InferenceSession(os.path.join(onnx_dir, "model.onnx"))
        _onnx_tokenizer = AutoTokenizer.from_pretrained(onnx_dir)

    import numpy as np

    inputs = _onnx_tokenizer(
        message, return_tensors="np", padding=True, truncation=True, max_length=128
    )
    outputs = _onnx_session.run(
        None,
        {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64),
        },
    )
    logits = outputs[0][0]
    exp_logits = np.exp(logits - logits.max())
    probs = exp_logits / exp_logits.sum()
    label_id = int(probs.argmax())
    return {"label": LABEL_MAP.get(label_id, "HAM"), "confidence": float(probs[label_id])}


_pytorch_clf = None


def _classify_pytorch(message):
    global _pytorch_clf
    if _pytorch_clf is None:
        from transformers import pipeline
        from config import MODEL_NAME

        _pytorch_clf = pipeline("text-classification", model=MODEL_NAME)
    result = _pytorch_clf(message)[0]
    label_map = {"LABEL_0": "HAM", "LABEL_1": "SPAM"}
    return {
        "label": label_map.get(result["label"], result["label"]),
        "confidence": float(result["score"]),
    }


def _classify_rule(message):
    score = 0.0
    lowered = message.lower()

    urls = re.findall(r"https?://\S+|www\.\S+", message, re.IGNORECASE)
    if urls:
        score += 0.3

    keyword_count = 0
    for word in SUSPICIOUS_WORDS:
        if word in lowered:
            keyword_count += 1
    score += min(keyword_count * 0.15, 0.5)

    caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)
    if caps_ratio > 0.5 and len(message) > 10:
        score += 0.1

    exclamations = message.count("!")
    if exclamations >= 2:
        score += 0.1

    confidence = min(score, 0.99)
    label = "SPAM" if score >= 0.3 else "HAM"

    return {"label": label, "confidence": round(confidence, 4)}


def get_classifier():
    return classify_message
