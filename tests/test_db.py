import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import init_db, insert_event, get_all_events, get_stats, get_event_by_id
from alerts import log_event

init_db()
print("Database initialized.\n")

test_cases = [
    ("+919999999999", "URGENT! Verify your bank at http://evil.com", {"ml_label": "SPAM", "ml_confidence": 0.95, "risk_score": 91, "severity": "CRITICAL", "action": "QUARANTINE", "reasons": ["BERT spam (+66pts)", "URL detected (+15pts)", "urgent (+5pts)"], "urls_found": ["http://evil.com"]}),
    ("+918888888888", "Hey, lunch tomorrow?", {"ml_label": "HAM", "ml_confidence": 0.94, "risk_score": 0, "severity": "LOW", "action": "ALLOW", "reasons": ["BERT ham (+0pts)"], "urls_found": []}),
    ("+917777777777", "You won a FREE prize! Claim at http://scam.win NOW!", {"ml_label": "SPAM", "ml_confidence": 0.88, "risk_score": 75, "severity": "HIGH", "action": "REVIEW", "reasons": ["BERT spam (+61pts)", "URL detected (+15pts)", "free (+5pts)", "prize (+5pts)"], "urls_found": ["http://scam.win"]}),
]

for sender, message, risk in test_cases:
    event_id = insert_event(sender, message, risk)
    log_event(event_id, sender, risk)
    print(f"Inserted event #{event_id}")

print("\n--- All Events ---")
for event in get_all_events():
    print(f"  #{event['id']} | {event['sender']} | Score={event['risk_score']} | {event['severity']} | {event['action']}")

print("\n--- Stats ---")
stats = get_stats()
print(f"  Total: {stats['total']}")
print(f"  Spam: {stats['spam_detected']}")
print(f"  Quarantined: {stats['quarantined']}")
print(f"  High Risk: {stats['high_risk']}")
print(f"  Distribution: {stats['severity_distribution']}")

print("\n--- Single Event ---")
e = get_event_by_id(1)
if e:
    print(f"  #{e['id']} | {e['message'][:40]}... | Reasons:\n    {e['reasons']}")
