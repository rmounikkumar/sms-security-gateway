import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from detector import classify_message

test_messages = [
    "Congratulations! You won a free iPhone. Click here to claim.",
    "Hey, are we still meeting for lunch tomorrow?",
    "URGENT: Your bank account has been suspended. Verify immediately.",
    "WINNER! You have been selected for a $1000 prize! Call now!",
    "Free entry to win a car! Text WIN to 80085",
    "Your OTP is 4521. Do not share it with anyone.",
    "Can you pick up milk on the way home?",
]

for msg in test_messages:
    result = classify_message(msg)
    label = "SPAM" if result["label"] == "LABEL_1" else "HAM"
    print(f"  [{label:4s}] {result['confidence']:.4f} | {msg}")
