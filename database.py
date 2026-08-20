import sqlite3
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            sender TEXT,
            message TEXT,
            ml_label TEXT,
            ml_confidence REAL,
            risk_score INTEGER,
            severity TEXT,
            action TEXT,
            reasons TEXT,
            urls TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_event(sender, message, risk_result):
    conn = get_connection()
    conn.execute(
        """INSERT INTO security_events
           (sender, message, ml_label, ml_confidence, risk_score, severity, action, reasons, urls)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            sender,
            message,
            risk_result["ml_label"],
            risk_result["ml_confidence"],
            risk_result["risk_score"],
            risk_result["severity"],
            risk_result["action"],
            "\n".join(risk_result["reasons"]),
            "\n".join(risk_result["urls_found"]),
        ),
    )
    conn.commit()
    event_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return event_id


def get_all_events(limit=50, offset=0):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM security_events ORDER BY id DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_event_by_id(event_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM security_events WHERE id = ?", (event_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM security_events").fetchone()[0]
    spam = conn.execute("SELECT COUNT(*) FROM security_events WHERE ml_label = 'SPAM'").fetchone()[0]
    quarantine = conn.execute("SELECT COUNT(*) FROM security_events WHERE action = 'QUARANTINE'").fetchone()[0]
    high = conn.execute("SELECT COUNT(*) FROM security_events WHERE severity IN ('HIGH','CRITICAL')").fetchone()[0]
    severity_dist = conn.execute(
        "SELECT severity, COUNT(*) as count FROM security_events GROUP BY severity"
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "spam_detected": spam,
        "quarantined": quarantine,
        "high_risk": high,
        "severity_distribution": {row["severity"]: row["count"] for row in severity_dist},
    }
