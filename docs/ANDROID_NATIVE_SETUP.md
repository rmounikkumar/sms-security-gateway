# Run SMS Security Gateway Directly on Android

## What You Need
- Android phone (4GB+ RAM recommended)
- Internet connection
- 2-3 GB free storage (for PyTorch + BERT model)

## Total Setup Time: 15-20 minutes

---

## Step 1: Install Termux from F-Droid

1. Open your phone browser
2. Go to: **https://f-droid.org/**
3. Download and install **F-Droid** APK
4. Open F-Droid app
5. Search: **Termux** -> Install
6. Search: **Termux:API** -> Install

**IMPORTANT:** Do NOT install Termux from Play Store (it's outdated)

---

## Step 2: Open Termux and Run Setup

Open Termux, paste this ONE command and press Enter:

```bash
pkg update -y && pkg upgrade -y && pkg install python git -y && pip install flask transformers torch && git clone https://github.com/rmounikkumar/sms-security-gateway.git && cd sms-security-gateway && mkdir -p data quarantine logs && python -c "from transformers import pipeline; pipeline('text-classification', model='mrm8488/bert-tiny-finetuned-sms-spam-detection')"
```

Wait 15-20 minutes for everything to download and install.

---

## Step 3: Start the Server

After setup completes, run:

```bash
cd ~/sms-security-gateway
python app.py
```

You'll see:
```
 * Running on http://0.0.0.0:5000
```

---

## Step 4: Open Dashboard on Your Phone

Open Chrome/Firefox on your phone and go to:

```
http://localhost:5000
```

That's it! The full project is running on your phone.

---

## Step 5: Analyze Messages

1. Tap **Analyze** in the navigation
2. Enter a sender number and message
3. Tap **Analyze Message**
4. See the threat assessment result
5. Check **Dashboard** for all analyzed events

---

## What's Running on Your Phone

```
Your Android Phone
|
|-- Termux (Linux terminal)
|   |-- Python 3
|   |-- Flask web server (port 5000)
|   |-- BERT-Tiny ML model (~17MB)
|   |-- PyTorch runtime (~200MB)
|   |-- SQLite database
|   +-- Web dashboard
|
|-- Phone Browser
    |-- http://localhost:5000 (Analyze page)
    |-- http://localhost:5000/dashboard (SOC dashboard)
    +-- http://localhost:5000/event/1 (Event detail)
```

---

## Optional: Forward Real SMS

To forward incoming SMS to the gateway automatically:

### Install Termux:API (already done in Step 1)

### Create SMS forwarder:
```bash
nano ~/sms-forwarder.py
```

Paste this code:
```python
import subprocess, json, time, urllib.request, os

GATEWAY_URL = "http://localhost:5000/api/analyze"
LAST_ID_FILE = os.path.expanduser("~/.sms_last_id")

def get_latest_sms():
    try:
        r = subprocess.run(["termux-sms-list", "-l", "1"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            msgs = json.loads(r.stdout)
            return msgs[0] if msgs else None
    except: pass
    return None

def main():
    print("SMS Forwarder started. Listening...")
    last_id = -1
    try:
        with open(LAST_ID_FILE) as f: last_id = int(f.read().strip())
    except: pass

    while True:
        sms = get_latest_sms()
        if sms:
            mid = sms.get("id", 0)
            if mid > last_id:
                sender = sms.get("number", "unknown")
                body = sms.get("body", "")
                print(f"Forwarding SMS from {sender}")
                try:
                    data = json.dumps({"sender": sender, "message": body}).encode()
                    req = urllib.request.Request(GATEWAY_URL, data=data, headers={"Content-Type": "application/json"})
                    urllib.request.urlopen(req, timeout=10)
                    print("Forwarded OK")
                except Exception as e:
                    print(f"Error: {e}")
                with open(LAST_ID_FILE, "w") as f: f.write(str(mid))
                last_id = mid
        time.sleep(5)

if __name__ == "__main__":
    main()
```

Save: Ctrl+X, Y, Enter

### Run in background:
```bash
pkg install tmux -y
tmux new -s sms
python ~/sms-forwarder.py
# Detach: Ctrl+B, then D
```

### Grant permissions:
- Android Settings -> Apps -> Termux:API -> Permissions -> Enable SMS, Phone
- Settings -> Apps -> Termux:API -> Battery -> Unrestricted

### Reattach later:
```bash
tmux attach -t sms
```

---

## Keep Server Running in Background

```bash
# Start server in tmux session
tmux new -s server
cd ~/sms-security-gateway
python app.py
# Detach: Ctrl+B, then D

# Reattach later
tmux attach -t server
```

---

## Stop Everything

```bash
# Stop server
tmux kill-session -t server

# Stop SMS forwarder
tmux kill-session -t sms
```

---

## Troubleshooting

### "No space left on device"
- PyTorch needs ~1.5GB storage
- Free up space or use a phone with more storage

### "Out of memory"
- Close other apps
- Android kills background apps - use tmux
- Some phones have 4GB RAM limit

### Server works but localhost won't load
- Make sure you're typing `http://localhost:5000`
- NOT `https://localhost:5000`

### Model download is slow
- First run downloads BERT model (~17MB)
- Subsequent runs use cached version
