# Termux + Python SMS Gateway Setup Guide (FREE)

## Prerequisites
- Android phone with SIM card
- Termux app installed (from F-Droid, NOT Play Store)
- Termux:API plugin installed (from F-Droid)
- Phone and PC on the same WiFi network
- Flask server running on PC

---

## Step 1: Install Apps (All FREE)

### Install from F-Droid (NOT Google Play Store)

1. Install **F-Droid** first:
   - Open browser on phone
   - Go to: https://f-droid.org/
   - Download and install F-Droid APK
   - Enable "Install from unknown sources" if prompted

2. Open F-Droid, search and install:
   - **Termux** (terminal emulator)
   - **Termux:API** (gives access to SMS, calls, etc.)
   - **Termux:Widget** (optional, for home screen shortcut)

3. DO NOT install Termux from Google Play Store (it's outdated and broken)

---

## Step 2: Setup Termux

Open Termux and run these commands one by one:

```bash
# Update package list
pkg update && pkg upgrade -y

# Install Python
pkg install python -y

# Install required Python packages
pip install requests

# Install Termux API tools
pkg install termux-api -y

# Grant SMS permission when prompted
# (Termux will ask for SMS access automatically)
```

---

## Step 3: Create the SMS Forwarder Script

```bash
# Create the script file
nano ~/sms_forwarder.py
```

Paste this code:

```python
#!/usr/bin/env python3
import subprocess
import json
import time
import sys

# ============ CONFIGURATION ============
GATEWAY_URL = "http://10.118.128.211:5000/api/analyze"
CHECK_INTERVAL = 5  # seconds between checks
LAST_ID_FILE = "/data/data/com.termux/files/home/.sms_last_id"
# =======================================

import urllib.request

def get_latest_sms():
    """Read latest SMS using termux-sms-list"""
    try:
        result = subprocess.run(
            ["termux-sms-list", "-l", "1"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            messages = json.loads(result.stdout)
            return messages[0] if messages else None
    except Exception as e:
        print(f"Error reading SMS: {e}")
    return None

def send_to_gateway(sender, message):
    """Forward SMS to the security gateway API"""
    try:
        payload = json.dumps({
            "sender": sender,
            "message": message
        }).encode("utf-8")

        req = urllib.request.Request(
            GATEWAY_URL,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode("utf-8"))

        severity = result.get("severity", "UNKNOWN")
        risk_score = result.get("risk_score", 0)
        action = result.get("action", "UNKNOWN")

        print(f"[FORWARDED] {sender}: Score={risk_score} | {severity} | {action}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to send: {e}")
        return False

def get_last_processed_id():
    """Read last processed SMS ID"""
    try:
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return -1

def save_last_processed_id(msg_id):
    """Save last processed SMS ID"""
    try:
        with open(LAST_ID_FILE, "w") as f:
            f.write(str(msg_id))
    except:
        pass

def main():
    print("=" * 50)
    print("  SMS Security Gateway - Forwarder")
    print(f"  Gateway: {GATEWAY_URL}")
    print(f"  Check interval: {CHECK_INTERVAL}s")
    print("=" * 50)
    print("Listening for incoming SMS...\n")

    last_id = get_last_processed_id()

    while True:
        sms = get_latest_sms()

        if sms:
            msg_id = sms.get("id", 0)
            sender = sms.get("number", "unknown")
            body = sms.get("body", "")

            if msg_id > last_id:
                print(f"[NEW SMS] From: {sender}")
                print(f"  Message: {body[:80]}...")
                send_to_gateway(sender, body)
                save_last_processed_id(msg_id)
                last_id = msg_id
                print()

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[STOPPED] SMS Forwarder stopped.")
```

Press **Ctrl+X**, then **Y**, then **Enter** to save.

---

## Step 4: Grant Permissions

```bash
# Test that termux-api works
termux-sms-list -l 1

# If it asks for permission, allow it
# If it returns an empty list [], that's fine - just means no recent SMS

# Test sending (optional - sends an SMS to your own number)
# termux-sms-send -n YOUR_NUMBER "Test message"
```

---

## Step 5: Run the Forwarder

```bash
python ~/sms_forwarder.py
```

You should see:
```
==================================================
  SMS Security Gateway - Forwarder
  Gateway: http://10.118.128.211:5000/api/analyze
  Check interval: 5s
==================================================
Listening for incoming SMS...
```

---

## Step 6: Test It

1. Make sure your PC is running: `python app.py`
2. Send an SMS to your phone from another phone
3. Watch the Termux terminal - you should see:
   ```
   [NEW SMS] From: +919999999999
     Message: Hello, testing the SMS gateway...
   [FORWARDED] +919999999999: Score=0 | LOW | ALLOW
   ```
4. Check dashboard: `http://10.118.128.211:5000/dashboard`

---

## Step 7: Run in Background (Optional)

To keep it running when Termux is minimized:

```bash
# Install tmux
pkg install tmux -y

# Start a tmux session
tmux new -s sms

# Run the forwarder
python ~/sms_forwarder.py

# Detach: Press Ctrl+B, then D
# Reattach: tmux attach -t sms
```

---

## Troubleshooting

### "Permission denied" for termux-sms-list
- Open Android Settings -> Apps -> Termux -> Permissions
- Enable: SMS, Phone, Storage
- Some phones: Settings -> Privacy -> Permission manager -> SMS -> Termux -> Allow

### "Connection refused" error
- PC firewall blocking port 5000
- Run on PC (as Admin): `netsh advfirewall firewall add rule name="SMS5000" dir=in action=allow protocol=tcp localport=5000`
- Or check PC and phone are on same WiFi

### Script doesn't detect new SMS
- The script checks every 5 seconds for the latest SMS
- It tracks IDs to avoid re-forwarding
- If no new SMS arrives, it stays silent

### Phone goes to sleep and stops
- Disable battery optimization for Termux:
  Settings -> Apps -> Termux -> Battery -> Unrestricted
- Keep Termux open in a tmux session

### termux-sms-list returns empty
- Make sure Termux:API is installed (separate app from Termux)
- Make sure SMS permission is granted

---

## Files on Phone
```
/data/data/com.termux/files/home/
|-- sms_forwarder.py    The forwarder script
|-- .sms_last_id        Tracks last processed SMS ID
```

---

## Stop the Forwarder
Press **Ctrl+C** in Termux to stop.
