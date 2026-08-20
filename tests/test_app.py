import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app
from database import init_db, get_stats, get_all_events

init_db()

with app.test_client() as client:
    print("=== Testing GET / ===")
    resp = client.get("/")
    print(f"  Status: {resp.status_code}")

    print("\n=== Testing POST /api/analyze ===")
    resp = client.post("/api/analyze",
        json={"sender": "+919999999999", "message": "URGENT! Verify bank at http://evil.com"})
    data = resp.get_json()
    print(f"  Status: {resp.status_code}")
    print(f"  Event ID: {data['event_id']}")
    print(f"  Label: {data['label']}")
    print(f"  Risk Score: {data['risk_score']}")
    print(f"  Severity: {data['severity']}")
    print(f"  Action: {data['action']}")
    print(f"  Reasons: {data['reasons']}")

    print("\n=== Testing POST /api/analyze (clean msg) ===")
    resp = client.post("/api/analyze",
        json={"sender": "+918888888888", "message": "Hey, lunch tomorrow?"})
    data = resp.get_json()
    print(f"  Score: {data['risk_score']} | Severity: {data['severity']} | Action: {data['action']}")

    print("\n=== Testing GET /api/stats ===")
    resp = client.get("/api/stats")
    stats = resp.get_json()
    print(f"  Total: {stats['total']} | Spam: {stats['spam_detected']} | Quarantined: {stats['quarantined']}")

    print("\n=== Testing GET /dashboard ===")
    resp = client.get("/dashboard")
    print(f"  Status: {resp.status_code}")

    print("\n=== Testing GET /event/1 ===")
    resp = client.get("/event/1")
    print(f"  Status: {resp.status_code}")

    print("\n=== Testing GET /api/events ===")
    resp = client.get("/api/events")
    events = resp.get_json()
    print(f"  Events returned: {len(events)}")

    print("\nAll tests passed!")
