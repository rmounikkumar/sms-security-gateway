import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

print("=" * 60)
print("  FULL PROJECT BUG CHECK")
print("=" * 60)

errors = []

# Test 1: Imports
print("\n[1/8] Testing imports...")
try:
    from config import MODEL_NAME, DATABASE_PATH, SUSPICIOUS_KEYWORDS, RISK_THRESHOLDS, RISK_WEIGHTS
    print("  config.py OK")
except Exception as e:
    print(f"  config.py FAIL: {e}")
    errors.append(str(e))

try:
    from detector import classify_message, get_classifier
    print("  detector.py OK")
except Exception as e:
    print(f"  detector.py FAIL: {e}")
    errors.append(str(e))

try:
    from risk_engine import calculate_risk, extract_urls
    print("  risk_engine.py OK")
except Exception as e:
    print(f"  risk_engine.py FAIL: {e}")
    errors.append(str(e))

try:
    from database import init_db, insert_event, get_all_events, get_event_by_id, get_stats
    print("  database.py OK")
except Exception as e:
    print(f"  database.py FAIL: {e}")
    errors.append(str(e))

try:
    from alerts import log_event, logger
    print("  alerts.py OK")
except Exception as e:
    print(f"  alerts.py FAIL: {e}")
    errors.append(str(e))

# Test 2: Model
print("\n[2/8] Testing BERT-Tiny model...")
ml = classify_message("Test message")
assert ml["label"] in ["HAM", "SPAM"], f'Bad label: {ml["label"]}'
assert 0 <= ml["confidence"] <= 1, f'Bad confidence: {ml["confidence"]}'
print(f'  Model OK: {ml["label"]} ({ml["confidence"]:.4f})')

# Test 3: Config values
print("\n[3/8] Testing config...")
assert MODEL_NAME == "mrm8488/bert-tiny-finetuned-sms-spam-detection"
assert len(SUSPICIOUS_KEYWORDS) > 0
assert RISK_THRESHOLDS["CRITICAL"] == 80
assert RISK_WEIGHTS["ml_spam"] == 70
print(f"  Config OK: {len(SUSPICIOUS_KEYWORDS)} keywords, thresholds correct")

# Test 4: Risk engine
print("\n[4/8] Testing risk engine...")
r1 = calculate_risk("URGENT! http://evil.com verify bank", {"label": "SPAM", "confidence": 0.95})
assert r1["risk_score"] > 50, f'Expected high score, got {r1["risk_score"]}'
assert r1["severity"] in ["HIGH", "CRITICAL"], f'Expected HIGH/CRITICAL, got {r1["severity"]}'
print(f'  Spam msg OK: score={r1["risk_score"]} severity={r1["severity"]} action={r1["action"]}')

r2 = calculate_risk("Lunch tomorrow?", {"label": "HAM", "confidence": 0.95})
assert r2["risk_score"] == 0, f'Expected 0, got {r2["risk_score"]}'
assert r2["severity"] == "LOW"
assert r2["action"] == "ALLOW"
print(f'  Clean msg OK: score={r2["risk_score"]} severity={r2["severity"]} action={r2["action"]}')

r3 = calculate_risk("Free prize! Winner! Claim at http://scam.com click now", {"label": "SPAM", "confidence": 0.88})
assert r3["risk_score"] >= 60, f'Expected HIGH+, got {r3["risk_score"]}'
print(f'  Mixed msg OK: score={r3["risk_score"]} severity={r3["severity"]}')

# Test 5: URL extraction
print("\n[5/8] Testing URL extraction...")
urls = extract_urls("Visit http://evil.com and https://phish.org/test")
assert len(urls) == 2, f"Expected 2 URLs, got {len(urls)}"
print(f"  URL extraction OK: found {len(urls)} URLs")

urls2 = extract_urls("No URLs here")
assert len(urls2) == 0
print("  No-URL msg OK: found 0 URLs")

# Test 6: Database
print("\n[6/8] Testing database...")
init_db()
eid = insert_event("+919999999999", "Test spam", r1)
assert eid > 0, f"Bad event ID: {eid}"
print(f"  Insert OK: event #{eid}")

events = get_all_events()
assert len(events) == 1
print(f"  Get all OK: {len(events)} events")

event = get_event_by_id(eid)
assert event is not None
assert event["sender"] == "+919999999999"
assert event["risk_score"] == r1["risk_score"]
print(f'  Get by ID OK: sender={event["sender"]} score={event["risk_score"]}')

stats = get_stats()
assert stats["total"] == 1
print(f'  Stats OK: total={stats["total"]} spam={stats["spam_detected"]} quarantine={stats["quarantined"]}')

# Test 7: Alerts + Quarantine
print("\n[7/8] Testing alerts & quarantine...")
log_event(eid, "+919999999999", r1)
qfile = os.path.join("..", "quarantine", f"event_{eid}.txt")
qfile2 = os.path.join("quarantine", f"event_{eid}.txt")
found = os.path.exists(qfile) or os.path.exists(qfile2)
assert found, f"Quarantine file not found"
print(f"  Quarantine file OK")

log_path = os.path.join("..", "logs", "security.log")
log_path2 = os.path.join("logs", "security.log")
assert os.path.exists(log_path) or os.path.exists(log_path2), "Log file not found"
print("  Log file OK: logs/security.log")

# Test 8: Flask app
print("\n[8/8] Testing Flask app...")
from app import app
with app.test_client() as c:
    r = c.get("/")
    assert r.status_code == 200
    print("  GET / OK: 200")

    r = c.get("/dashboard")
    assert r.status_code == 200
    print("  GET /dashboard OK: 200")

    r = c.get("/event/1")
    assert r.status_code == 200
    print("  GET /event/1 OK: 200")

    r = c.get("/event/9999")
    assert r.status_code == 404
    print("  GET /event/9999 OK: 404 (correct)")

    r = c.get("/api/stats")
    assert r.status_code == 200
    print("  GET /api/stats OK: 200")

    r = c.get("/api/events")
    assert r.status_code == 200
    print("  GET /api/events OK: 200")

    r = c.post("/api/analyze", json={"sender": "+911111111111", "message": "Test from bug check"})
    assert r.status_code == 200
    data = r.get_json()
    assert "event_id" in data
    assert "risk_score" in data
    assert "severity" in data
    print(f'  POST /api/analyze OK: id={data["event_id"]} score={data["risk_score"]} sev={data["severity"]}')

    r = c.post("/api/analyze", json={})
    assert r.status_code == 400
    print("  POST /api/analyze (no msg) OK: 400 (correct)")

    r = c.post("/api/analyze", json={"message": "SPAM test http://evil.com URGENT verify winner prize claim"})
    assert r.status_code == 200
    data2 = r.get_json()
    print(f'  POST /api/analyze (spam) OK: score={data2["risk_score"]} sev={data2["severity"]} action={data2["action"]}')

print("\n" + "=" * 60)
if errors:
    print(f"  {len(errors)} ERRORS FOUND:")
    for e in errors:
        print(f"    - {e}")
else:
    print("  ALL 8 TESTS PASSED - 0 BUGS FOUND")
print("=" * 60)
