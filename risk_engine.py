import re
from config import SUSPICIOUS_KEYWORDS, RISK_THRESHOLDS, RISK_WEIGHTS


def extract_urls(message):
    return re.findall(r"https?://\S+|www\.\S+", message, re.IGNORECASE)


def calculate_risk(message, ml_result):
    score = 0
    reasons = []

    label = ml_result["label"].upper()
    confidence = ml_result["confidence"]

    if label == "SPAM":
        ml_score = int(confidence * RISK_WEIGHTS["ml_spam"])
        score += ml_score
        reasons.append(f"BERT classified as spam (+{ml_score}pts)")
    elif label == "HAM":
        reasons.append("BERT classified as ham (+0pts)")

    urls = extract_urls(message)
    if urls:
        score += RISK_WEIGHTS["url_detected"]
        reasons.append(f"URL detected (+{RISK_WEIGHTS['url_detected']}pts)")

    lowered = message.lower()
    keyword_hits = []
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in lowered:
            keyword_hits.append(keyword)
            score += RISK_WEIGHTS["keyword"]
            reasons.append(f"Suspicious keyword: {keyword} (+{RISK_WEIGHTS['keyword']}pts)")

    score = min(score, 100)

    if score >= RISK_THRESHOLDS["CRITICAL"]:
        severity = "CRITICAL"
        action = "QUARANTINE"
    elif score >= RISK_THRESHOLDS["HIGH"]:
        severity = "HIGH"
        action = "REVIEW"
    elif score >= RISK_THRESHOLDS["MEDIUM"]:
        severity = "MEDIUM"
        action = "REVIEW"
    else:
        severity = "LOW"
        action = "ALLOW"

    return {
        "risk_score": score,
        "severity": severity,
        "action": action,
        "reasons": reasons,
        "urls_found": urls,
        "keyword_hits": keyword_hits,
        "ml_label": label,
        "ml_confidence": confidence,
    }
