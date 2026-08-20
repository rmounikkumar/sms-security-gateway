import os
from flask import Flask, render_template, request, jsonify
from detector import classify_message
from risk_engine import calculate_risk
from database import init_db, insert_event, get_all_events, get_event_by_id, get_stats
from alerts import log_event

app = Flask(__name__)

init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    stats = get_stats()
    events = get_all_events(limit=20)
    return render_template("dashboard.html", stats=stats, events=events)


@app.route("/event/<int:event_id>")
def event_detail(event_id):
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404
    return render_template("event.html", event=event)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    sender = data.get("sender", "unknown")
    message = data["message"]

    ml_result = classify_message(message)
    risk_result = calculate_risk(message, ml_result)

    event_id = insert_event(sender, message, risk_result)
    log_event(event_id, sender, risk_result)

    return jsonify({
        "event_id": event_id,
        "label": risk_result["ml_label"],
        "confidence": risk_result["ml_confidence"],
        "risk_score": risk_result["risk_score"],
        "severity": risk_result["severity"],
        "action": risk_result["action"],
        "reasons": risk_result["reasons"],
        "urls_found": risk_result["urls_found"],
    })


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/events")
def api_events():
    limit = request.args.get("limit", 50, type=int)
    events = get_all_events(limit=limit)
    return jsonify(events)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
