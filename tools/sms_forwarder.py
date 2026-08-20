#!/usr/bin/env python3
"""
SMS Security Gateway - Android Forwarder
Reads incoming SMS via Termux API and forwards to the security gateway.

Setup:
  1. Install Termux + Termux:API from F-Droid
  2. Run: pkg install python termux-api
  3. Run: pip install requests
  4. Run: python sms_forwarder.py
"""
import subprocess
import json
import time
import urllib.request
import os

# ============ CONFIGURATION ============
# Change this to your PC's IP address
GATEWAY_URL = "http://10.118.128.211:5000/api/analyze"
CHECK_INTERVAL = 5
LAST_ID_FILE = os.path.expanduser("~/.sms_last_id")
# =======================================


def get_latest_sms():
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
        reasons = result.get("reasons", [])

        color = {"LOW": "\033[92m", "MEDIUM": "\033[93m", "HIGH": "\033[91m", "CRITICAL": "\033[95m"}.get(severity, "")
        reset = "\033[0m"

        print(f"  {color}[FORWARDED]{reset} Score={risk_score}/100 | {severity} | {action}")
        for r in reasons:
            print(f"    - {r}")
        return True

    except urllib.error.URLError as e:
        print(f"  [ERROR] Cannot reach gateway: {e}")
        print(f"  Make sure python app.py is running on your PC")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def get_last_processed_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return -1


def save_last_processed_id(msg_id):
    try:
        with open(LAST_ID_FILE, "w") as f:
            f.write(str(msg_id))
    except:
        pass


def main():
    print("=" * 55)
    print("  SMS Security Gateway - Android Forwarder")
    print(f"  Gateway : {GATEWAY_URL}")
    print(f"  Interval: {CHECK_INTERVAL}s")
    print("=" * 55)

    last_id = get_last_processed_id()
    print("Listening for incoming SMS... (Ctrl+C to stop)\n")

    while True:
        sms = get_latest_sms()

        if sms:
            msg_id = sms.get("id", 0)
            sender = sms.get("number", "unknown")
            body = sms.get("body", "")

            if msg_id > last_id:
                print(f"[NEW SMS] From: {sender}")
                print(f"  Text: {body[:100]}")
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
