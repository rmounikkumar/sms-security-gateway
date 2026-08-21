import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

print("--- Function Call Chain Test ---")

from config import MODEL_NAME, DATABASE_PATH, SUSPICIOUS_KEYWORDS, RISK_THRESHOLDS, RISK_WEIGHTS, LOG_PATH, QUARANTINE_PATH
print("[OK] config.py: 6 imports")

from detector import classify_message, get_classifier, LABEL_MAP
ml = classify_message("test")
print("[OK] detector.py: classify_message -> " + str(ml))

from risk_engine import calculate_risk, extract_urls
risk = calculate_risk("http://evil.com URGENT verify", ml)
print("[OK] risk_engine.py: calculate_risk -> score=" + str(risk["risk_score"]) + " sev=" + risk["severity"])

from database import init_db, insert_event, get_all_events, get_event_by_id, get_stats
init_db()
eid = insert_event("+91000000000", "chain test", risk)
event = get_event_by_id(eid)
events = get_all_events()
stats = get_stats()
print("[OK] database.py: insert=" + str(eid) + " get=" + str(event is not None) + " list=" + str(len(events)))

from alerts import log_event
log_event(eid, "+91000000000", risk)
print("[OK] alerts.py: log_event")

from app import app
with app.test_client() as c:
    r = c.post("/api/analyze", json={"sender": "+91000000001", "message": "chain test message"})
    data = r.get_json()
    print("[OK] app.py: /api/analyze -> event_id=" + str(data["event_id"]) + " score=" + str(data["risk_score"]))
    r2 = c.get("/dashboard")
    r3 = c.get("/event/" + str(data["event_id"]))
    r4 = c.get("/api/stats")
    r5 = c.get("/api/events")
    print("[OK] app.py: /dashboard=" + str(r2.status_code) + " /event=" + str(r3.status_code) + " /stats=" + str(r4.status_code) + " /events=" + str(r5.status_code))

print()
print("=== ALL FUNCTION CALLS WORKING ===")
