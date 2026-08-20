import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from detector import classify_message
from risk_engine import calculate_risk

tests = [
    "URGENT! Verify your bank account at http://evil-bank.com",
    "Hey, lunch tomorrow at noon?",
    "Congratulations! You won $1000! Click http://scam.win to claim your prize NOW!",
    "Your OTP is 4521. Do not share.",
]

for msg in tests:
    ml = classify_message(msg)
    risk = calculate_risk(msg, ml)
    print(f"Message:   {msg[:60]}...")
    print(f"  ML:       {risk['ml_label']} ({risk['ml_confidence']:.4f})")
    print(f"  Score:    {risk['risk_score']}/100")
    print(f"  Severity: {risk['severity']}")
    print(f"  Action:   {risk['action']}")
    print(f"  Reasons:  {risk['reasons']}")
    print()
