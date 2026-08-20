import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_NAME = "mrm8488/bert-tiny-finetuned-sms-spam-detection"

DATABASE_PATH = os.path.join(BASE_DIR, "data", "security_events.db")
LOG_PATH = os.path.join(BASE_DIR, "logs", "security.log")
QUARANTINE_PATH = os.path.join(BASE_DIR, "quarantine")

SUSPICIOUS_KEYWORDS = [
    "urgent",
    "verify",
    "account suspended",
    "click now",
    "winner",
    "prize",
    "claim",
    "password",
    "otp",
    "free",
    "congratulations",
    "limited time",
    "act now",
    "bank",
    "confirm",
    "unlock",
    "expir",
]

RISK_THRESHOLDS = {
    "CRITICAL": 80,
    "HIGH": 60,
    "MEDIUM": 30,
    "LOW": 0,
}

RISK_WEIGHTS = {
    "ml_spam": 70,
    "url_detected": 15,
    "keyword": 5,
    "unknown_sender": 5,
}
