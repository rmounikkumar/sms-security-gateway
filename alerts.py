import logging
import os
from config import LOG_PATH, QUARANTINE_PATH

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
os.makedirs(QUARANTINE_PATH, exist_ok=True)

logger = logging.getLogger("sms-security")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_PATH)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
logger.addHandler(console_handler)


def log_event(event_id, sender, risk_result):
    severity = risk_result["severity"]
    action = risk_result["action"]
    score = risk_result["risk_score"]

    msg = (
        f"Event#{event_id} | Sender={sender} | "
        f"Score={score} | Severity={severity} | Action={action}"
    )

    if severity == "CRITICAL":
        logger.critical(msg)
    elif severity == "HIGH":
        logger.warning(msg)
    else:
        logger.info(msg)

    if action == "QUARANTINE":
        quarantine_event(event_id, sender, risk_result)


def quarantine_event(event_id, sender, risk_result):
    filepath = os.path.join(QUARANTINE_PATH, f"event_{event_id}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Event ID: {event_id}\n")
        f.write(f"Sender: {sender}\n")
        f.write(f"Timestamp: {risk_result.get('timestamp', 'N/A')}\n")
        f.write(f"ML Label: {risk_result['ml_label']}\n")
        f.write(f"ML Confidence: {risk_result['ml_confidence']}\n")
        f.write(f"Risk Score: {risk_result['risk_score']}\n")
        f.write(f"Severity: {risk_result['severity']}\n")
        f.write(f"Action: {risk_result['action']}\n")
        f.write(f"URLs Found: {', '.join(risk_result['urls_found'])}\n")
        f.write(f"Reasons:\n")
        for reason in risk_result["reasons"]:
            f.write(f"  - {reason}\n")
