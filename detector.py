import os
import numpy as np

ONNX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "onnx_model")
LABEL_MAP = {0: "HAM", 1: "SPAM"}

_session = None
_tokenizer = None
_use_onnx = os.path.exists(os.path.join(ONNX_DIR, "model.onnx"))


def _load_onnx():
    global _session, _tokenizer
    if _session is not None:
        return
    from onnxruntime import InferenceSession
    from transformers import AutoTokenizer
    _session = InferenceSession(os.path.join(ONNX_DIR, "model.onnx"))
    _tokenizer = AutoTokenizer.from_pretrained(ONNX_DIR)


def _load_transformers():
    global _classifier
    if "_classifier" not in globals() or _classifier is None:
        from transformers import pipeline
        from config import MODEL_NAME
        _classifier = pipeline("text-classification", model=MODEL_NAME)
    return _classifier


def classify_message(message):
    if _use_onnx:
        return _classify_onnx(message)
    return _classify_transformers(message)


def get_classifier():
    return classify_message


def _classify_onnx(message):
    _load_onnx()
    inputs = _tokenizer(
        message,
        return_tensors="np",
        padding=True,
        truncation=True,
        max_length=128,
    )
    outputs = _session.run(
        None,
        {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64),
        },
    )
    logits = outputs[0][0]
    exp_logits = np.exp(logits - np.max(logits))
    probs = exp_logits / exp_logits.sum()
    label_id = int(np.argmax(probs))
    confidence = float(probs[label_id])
    return {
        "label": LABEL_MAP.get(label_id, f"LABEL_{label_id}"),
        "confidence": confidence,
    }


def _classify_transformers(message):
    clf = _load_transformers()
    result = clf(message)[0]
    label_map = {"LABEL_0": "HAM", "LABEL_1": "SPAM"}
    return {
        "label": label_map.get(result["label"], result["label"]),
        "confidence": float(result["score"]),
    }
