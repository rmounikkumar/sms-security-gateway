# AI-Based SMS Threat Detection & Security Monitoring System

A defensive cybersecurity platform that uses **BERT-Tiny** machine learning to identify potentially malicious SMS messages, combines ML predictions with rule-based security indicators to calculate risk scores, quarantines high-risk messages, and presents alerts through a SOC-style dashboard.

---

## Table of Contents

- [About The Project](#about-the-project)
- [Problems It Solves](#problems-it-solves)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Installation](#installation)
  - [Option A: Run on PC](#option-a-run-on-windowslinuxmac-pc)
  - [Option B: Run Directly on Android](#option-b-run-directly-on-android-no-pc-required)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Risk Engine Explained](#risk-engine-explained)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)

---

## About The Project

This project is an **AI-Powered SMS Security Gateway** that turns a Hugging Face spam classification model into a full defensive security product. Instead of simply running a classifier and printing "spam" or "ham", this system:

1. Classifies messages using a fine-tuned BERT-Tiny model
2. Extracts suspicious URLs from message text
3. Detects urgency/scam keywords
4. Calculates a composite risk score (0-100)
5. Makes security decisions: ALLOW, REVIEW, or QUARANTINE
6. Logs every event to an SQLite database
7. Stores quarantined messages as evidence files
8. Displays everything through a SOC-style monitoring dashboard

### ML Model

- **Model:** `mrm8488/bert-tiny-finetuned-sms-spam-detection`
- **Parameters:** ~4.39M (lightweight, fast inference)
- **Validation Accuracy:** 0.98 on SMS spam dataset
- **Labels:** HAM (legitimate) / SPAM (malicious)
- **Runtime:** Hugging Face Transformers pipeline

---

## Problems It Solves

### 1. SMS Spam & Phishing Detection
- Identifies spam messages using AI-powered classification
- Detects phishing attempts that try to steal credentials or personal data
- Catches scam messages promising fake prizes, lottery wins, or urgent bank alerts

### 2. Automated Threat Triage
- Manually reviewing every SMS is impossible at scale
- The system automatically classifies and scores every incoming message
- Security teams can focus on HIGH/CRITICAL events instead of reading every message

### 3. False Positive Mitigation
- BERT-Tiny alone may misclassify some messages
- The multi-signal risk engine (ML + URL + keywords) compensates for ML weaknesses
- Example: Even when BERT says "HAM", a message with suspicious URLs and urgency keywords still gets flagged

### 4. Incident Evidence Collection
- Every analyzed message is stored in SQLite with full metadata
- Quarantined messages are saved as text files for forensic review
- Security logs provide an audit trail for compliance and investigation

### 5. Real-Time Security Visibility
- SOC teams need dashboards, not raw data
- The dashboard shows total messages analyzed, spam detected, quarantined count, and severity distribution
- Individual events can be drilled into for full threat assessment details

### 6. Explainability
- Instead of just "SPAM - 98%", the system shows WHY it made its decision
- Each risk factor is broken down with point values
- Analysts can see exactly which signals contributed to the risk score

---

## Key Features

| Feature | Description |
|---------|-------------|
| BERT-Tiny ML Classification | AI-powered SMS spam detection using fine-tuned transformer model |
| Multi-Signal Risk Engine | Combines ML output + URL detection + keyword analysis into 0-100 score |
| 4-Level Severity System | LOW (0-29), MEDIUM (30-59), HIGH (60-79), CRITICAL (80-100) |
| Automated Actions | ALLOW (pass through), REVIEW (flag for analyst), QUARANTINE (block & store) |
| SQLite Event Database | Every analyzed message stored with full metadata and risk breakdown |
| Quarantine System | CRITICAL messages saved as evidence files in `/quarantine/` |
| Security Logging | Structured log file with severity-appropriate log levels |
| Web Dashboard | SOC-style monitoring with stats, severity bars, and event table |
| REST API | JSON API for integration with Android clients, simulators, or other systems |
| Explainable AI | Every decision includes a breakdown of risk factors with point values |
| URL Extraction | Automatically detects and extracts URLs from message text |
| Sender Tracking | Tracks sender phone numbers across multiple messages |
| Responsive UI | Dark-themed dashboard works on desktop and mobile |

---

## Architecture

```
User Input (sender + message)
        |
        v
+------------------+
|   BERT-Tiny ML   |  <-- mrm8488/bert-tiny-finetuned-sms-spam-detection
|   Classifier     |      Hugging Face Transformers
+--------+---------+
         |
         v  {label: HAM/SPAM, confidence: 0.xx}
+------------------+
|   Risk Engine    |
|                  |
|  ML Score (0-70) |
|  URL Check (0-15)|
|  Keywords (0-35) |
+--------+---------+
         |
         v  {risk_score, severity, action, reasons}
    +---------+---------+
    |         |         |
    v         v         v
 Database  Alerts  Quarantine
 SQLite    Log     Files
    |
    v
 Web Dashboard / API Response
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| ML Engine | `mrm8488/bert-tiny-finetuned-sms-spam-detection` |
| ML Runtime | Hugging Face Transformers |
| Deep Learning | PyTorch |
| Backend | Python 3 + Flask |
| Database | SQLite3 |
| Frontend | HTML5 / CSS3 / JavaScript |
| Styling | Custom dark-theme CSS (SOC-style) |
| Logging | Python `logging` module |

---

## Project Structure

```
sms-defense/
|
|-- app.py                    Flask application & API routes
|-- detector.py               BERT-Tiny ML classifier (loads model once)
|-- risk_engine.py            Risk scoring engine (URL + keywords + ML)
|-- database.py               SQLite CRUD operations & stats
|-- alerts.py                 Security logging & quarantine system
|-- config.py                 Central configuration (model, thresholds, keywords)
|
|-- templates/
|   |-- index.html            Message input form (Analyze page)
|   |-- dashboard.html        SOC-style monitoring dashboard
|   +-- event.html            Single event detail view
|
|-- static/
|   +-- style.css             Dark-theme dashboard styling (398 lines)
|
|-- data/
|   +-- security_events.db    SQLite database (auto-created on first run)
|
|-- quarantine/               Quarantined message evidence files
|
|-- logs/
|   +-- security.log          Security event log file
|
|-- tests/
|   |-- test_detector.py      ML detector unit tests
|   |-- test_risk.py          Risk engine unit tests
|   |-- test_db.py            Database unit tests
|   +-- test_app.py           Full integration tests
|
+-- requirements.txt          Python dependencies
```

---

## How It Works

### Step 1: Message Input
User enters a sender phone number and SMS message through the web form or REST API.

### Step 2: ML Classification
The BERT-Tiny model classifies the message as HAM or SPAM with a confidence score.

### Step 3: Multi-Signal Risk Scoring
The risk engine combines three signals:
- **ML Signal (0-70 points):** If BERT says SPAM, score = confidence * 70
- **URL Signal (0-15 points):** If any URL is detected in the message
- **Keyword Signal (0-5 each):** Each suspicious keyword match adds points (17 keywords defined)

### Step 4: Severity & Action
Based on the total risk score:
| Score | Severity | Action |
|-------|----------|--------|
| 0-29 | LOW | ALLOW |
| 30-59 | MEDIUM | REVIEW |
| 60-79 | HIGH | REVIEW |
| 80-100 | CRITICAL | QUARANTINE |

### Step 5: Storage & Logging
- Event saved to SQLite database with full metadata
- Log entry written to `security.log` with appropriate severity level
- If QUARANTINE, message saved as evidence file in `/quarantine/`

### Step 6: Dashboard & Response
- Web dashboard displays stats, severity distribution, and recent events
- API returns full analysis results as JSON

---

## Installation

### Option A: Run on Windows/Linux/Mac (PC)

**Prerequisites:** Python 3.9+, pip

```bash
git clone https://github.com/rmounikkumar/sms-security-gateway.git
cd sms-security-gateway
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`

---

### Option B: Run Directly on Android (No PC Required)

Run the entire project on your Android phone using Termux. No PC needed after setup.

#### Step 1: Install Termux from F-Droid

1. Open your phone browser
2. Go to **https://f-droid.org/**
3. Download and install **F-Droid** APK
4. Open F-Droid -> Search **Termux** -> Install
5. Also install **Termux:API** (for SMS forwarding)

> **Do NOT install Termux from Play Store** (it's outdated and broken)

#### Step 2: Install Termux:API Permissions

```
Android Settings -> Apps -> Termux:API -> Permissions -> Enable SMS, Phone
Android Settings -> Apps -> Termux:API -> Battery -> Unrestricted
Android Settings -> Apps -> Termux -> Battery -> Unrestricted
```

#### Step 3: Setup Project in Termux

Open Termux and paste this **one command** (takes 15-20 min):

```bash
pkg update -y && pkg upgrade -y && pkg install python git -y && pip install flask transformers numpy && git clone https://github.com/rmounikkumar/sms-security-gateway.git && cd sms-security-gateway && mkdir -p data quarantine logs && python app.py
```

> On Android, the detector automatically uses a **rule-based fallback** (URL + keyword analysis). On PC with PyTorch/ONNX installed, the full **BERT-Tiny ML model** runs. The risk engine works on both.

#### Step 4: Download BERT-Tiny Model

```bash
cd ~/sms-security-gateway
python -c "from transformers import pipeline; pipeline('text-classification', model='mrm8488/bert-tiny-finetuned-sms-spam-detection')"
```

#### Step 5: Start the Server

```bash
python app.py
```

You'll see:
```
 * Running on http://0.0.0.0:5000
```

#### Step 6: Open on Your Phone

Open Chrome/Firefox on your phone:
```
http://localhost:5000
```

**Done!** The full project with BERT-Tiny ML model, risk engine, database, and dashboard is running on your Android phone.

#### Step 7 (Optional): Forward Real SMS

Create an auto-forwarder so incoming SMS are analyzed automatically:

```bash
nano ~/sms_forwarder.py
```

Paste this code:

```python
import subprocess, json, time, urllib.request, os

GATEWAY = "http://localhost:5000/api/analyze"
LAST_ID = os.path.expanduser("~/.sms_id")

def get_sms():
    try:
        r = subprocess.run(["termux-sms-list", "-l", "1"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            m = json.loads(r.stdout)
            return m[0] if m else None
    except: pass
    return None

def main():
    last = -1
    try:
        with open(LAST_ID) as f: last = int(f.read().strip())
    except: pass
    print("Listening for SMS...")
    while True:
        sms = get_sms()
        if sms and sms.get("id", 0) > last:
            s, b = sms.get("number", "?"), sms.get("body", "")
            print(f"SMS from {s}: {b[:50]}")
            try:
                d = json.dumps({"sender": s, "message": b}).encode()
                urllib.request.urlopen(urllib.request.Request(GATEWAY, d, {"Content-Type": "application/json"}), timeout=10)
                print("Forwarded OK")
            except Exception as e: print(f"Error: {e}")
            with open(LAST_ID, "w") as f: f.write(str(sms["id"]))
            last = sms["id"]
        time.sleep(5)

if __name__ == "__main__": main()
```

Press `Ctrl+X`, `Y`, `Enter` to save.

Run it:
```bash
python ~/sms_forwarder.py
```

Now every incoming SMS is automatically analyzed and stored.

#### Keep Running in Background

```bash
# Install tmux
pkg install tmux -y

# Start server in a session
tmux new -s server
python app.py
# Press Ctrl+B, then D to detach

# Start SMS forwarder in another session
tmux new -s sms
python ~/sms_forwarder.py
# Press Ctrl+B, then D to detach

# Reattach later
tmux attach -t server
tmux attach -t sms
```

#### Storage Requirements

| Component | Size |
|-----------|------|
| Python + Termux | ~50MB |
| Transformers | ~50MB |
| NumPy | ~15MB |
| Your project | ~50KB |
| **Total** | **~115MB** |

---

## Usage

### Web Interface

1. Open `http://localhost:5000` in your browser
2. Enter a sender number and SMS message
3. Click **Analyze Message**
4. View the threat assessment result
5. Navigate to **Dashboard** to see all analyzed events

### REST API

**Analyze a message:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"sender": "+919999999999", "message": "URGENT! Verify your bank at http://evil.com"}'
```

**Response:**
```json
{
  "event_id": 1,
  "label": "HAM",
  "confidence": 0.79,
  "risk_score": 30,
  "severity": "MEDIUM",
  "action": "REVIEW",
  "reasons": [
    "BERT classified as ham (+0pts)",
    "URL detected (+15pts)",
    "Suspicious keyword: urgent (+5pts)",
    "Suspicious keyword: verify (+5pts)",
    "Suspicious keyword: bank (+5pts)"
  ],
  "urls_found": ["http://evil.com"]
}
```

**Get dashboard stats:**
```bash
curl http://localhost:5000/api/stats
```

**Get all events:**
```bash
curl http://localhost:5000/api/events?limit=10
```

---

## Risk Engine Explained

### Scoring Breakdown

| Signal | Points | Trigger |
|--------|--------|---------|
| BERT SPAM classification | 0-70 | confidence * 70 (only if label = SPAM) |
| URL detected | +15 | Any http/https/www URL in message |
| Suspicious keyword | +5 each | Match from 17 predefined keywords |

### Suspicious Keywords
```
urgent, verify, account suspended, click now, winner, prize, claim,
password, otp, free, congratulations, limited time, act now, bank,
confirm, unlock, expir
```

### Example Assessment

**Message:** `"URGENT! Your bank account has been suspended. Verify at http://evil-bank.com"`

| Signal | Points | Reason |
|--------|--------|--------|
| BERT SPAM (0.96 conf) | +67 | confidence * 70 |
| URL detected | +15 | http://evil-bank.com |
| "urgent" | +5 | keyword match |
| "verify" | +5 | keyword match |
| "bank" | +5 | keyword match |
| **Total** | **97** | **CRITICAL -> QUARANTINE** |

---

## Future Enhancements

- [ ] Android SMS gateway integration (real-time SMS monitoring)
- [ ] Feedback/retraining loop (human analyst corrections)
- [ ] Domain reputation checking for detected URLs
- [ ] Telegram/Discord alerting for CRITICAL events
- [ ] Docker deployment support
- [ ] Network monitoring integration (Wireshark)
- [ ] Host security audit integration (Lynis)
- [ ] CSV/JSON report export
- [ ] Sender reputation scoring across multiple messages
- [ ] Message frequency analysis

---

## Disclaimer

This is a **defensive security educational project**. The BERT-Tiny model provides an SMS spam classification signal. The risk engine combines this with additional indicators for better accuracy. This system is not a replacement for production-grade security infrastructure.

---

## License

Educational / Academic use.
