# Android Tasker SMS Gateway Setup Guide

## Prerequisites
- Android phone with SIM card
- Tasker app installed (free trial from Play Store, or full version)
- Phone and PC on the same WiFi network
- Flask server running on PC (`python app.py`)

---

## Step 1: Find Your PC's IP Address

On your PC, the IP is: **10.118.128.211**

The API endpoint will be: `http://10.118.128.211:5000/api/analyze`

---

## Step 2: Install Tasker

1. Open Google Play Store on your Android phone
2. Search for "Tasker" (by joaomgcd)
3. Install it (free trial available, or buy full version ~$3.49)
4. Open Tasker and grant all requested permissions
5. When asked about "Notification Access" -> Enable it
6. When asked about "Battery Optimization" -> Set to "Don't optimize"

---

## Step 3: Create the Profile (Trigger)

A Profile in Tasker = "When something happens, do this task"

1. Open Tasker
2. Tap the **PROFILES** tab (bottom left)
3. Tap the **+** button (bottom right)
4. Select **Event**
5. Select **Phone**
6. Select **Received Text**
7. Configure:
   - Type: **Any**
   - Sender: (leave blank = any sender)
   - Message: (leave blank = any message)
8. Tap the back arrow (top left) to save

---

## Step 4: Create the Task (Action)

1. After saving the Profile, Tasker will ask "New Task"
2. Name it: **Forward SMS to Gateway**
3. Tap the **+** button to add an action

### Action 1: HTTP Request

4. Select **Net**
5. Select **HTTP Request**
6. Configure:
   - Method: **POST**
   - URL: `http://10.118.128.211:5000/api/analyze`
   - Headers: Tap the edit icon (pencil) and enter:
     ```
     Content-Type: application/json
     ```
   - Body: Tap the edit icon (pencil) and enter this exactly:
     ```
     {"sender": "%sender", "message": "%smsbodies"}
     ```
   - Timeout: **10 seconds**
7. Tap the back arrow to save

### Action 2: Flash (Optional - shows notification)

8. Tap **+** again
9. Select **Alert**
10. Select **Flash**
11. Message: Enter:
    ```
    SMS Gateway: Forwarded from %sender
    ```
12. Tap back to save

### Action 3: Play Sound (Optional - for CRITICAL events)

13. Tap **+** again
14. Select **Alert**
15. Select **Beep** (or **Music Play**)
16. Duration: **1 second**
17. Priority: **5** (high)

### Save the Task
18. Tap the back arrow (top left) until you're back to the Profiles tab
19. Make sure the profile toggle is **ON** (green)

---

## Step 5: Test It

1. Make sure your PC is running: `python app.py`
2. Make sure your phone is on the same WiFi as your PC
3. Send an SMS to your phone (from another phone or use a friend's number)
4. Wait 5-10 seconds
5. Check the dashboard: `http://10.118.128.211:5000/dashboard`
6. The message should appear in the events table

---

## Troubleshooting

### "Connection refused" or timeout
- Make sure `python app.py` is running on your PC
- Make sure both devices are on the same WiFi
- Check Windows Firewall: Allow Python on port 5000
  - Open Windows Defender Firewall
  - Advanced Settings -> Inbound Rules -> New Rule
  - Port -> TCP 5000 -> Allow -> Finish

### Tasker not triggering
- Check Tasker is enabled (look for the icon in notification bar)
- Go to Android Settings -> Apps -> Tasker -> Battery -> "Unrestricted"
- Go to Android Settings -> Apps -> Tasker -> "Allow auto-start"

### Tasker shows "HTTP Request" error
- Test the API manually first using a browser on your phone:
  Open: `http://10.118.128.211:5000/api/stats`
  If it loads, the connection works

### SMS not received by Tasker
- Go to Android Settings -> Apps -> Tasker -> Permissions
- Enable: SMS, Phone, Notifications
- Some phones (Xiaomi, Huawei, Samsung) have extra battery savers:
  - Settings -> Apps -> Tasker -> Battery -> "Don't optimize"
  - Settings -> Battery -> App battery saver -> Tasker -> "No restrictions"

---

## Variables Reference

Tasker uses these variables for SMS:
- `%sender` = Phone number of sender
- `%smsbodies` = Full text of the SMS message
- `%smsdate` = Date when SMS was received
- `%smsstatus` = SMS status (complete, pending, etc.)
- `%smsproto` = SMS protocol (e.g., "sms")

---

## Advanced: Only Forward Spam Suspects

If you want to filter and only forward suspicious messages:

1. Open the Task "Forward SMS to Gateway"
2. Before the HTTP Request action, add:
   - Task -> If
   - Condition: `%smsbodies` **~R** `urgent|verify|bank|winner|prize|free|claim|click|otp|password|suspend`
   - This only forwards messages containing suspicious keywords
   - Add the HTTP Request and Flash actions inside this If block

---

## API Response Example

When Tasker forwards an SMS, the API responds with JSON like:
```json
{
  "event_id": 5,
  "label": "SPAM",
  "confidence": 0.92,
  "risk_score": 85,
  "severity": "CRITICAL",
  "action": "QUARANTINE",
  "reasons": [
    "BERT classified as spam (+64pts)",
    "URL detected (+15pts)",
    "Suspicious keyword: bank (+5pts)"
  ],
  "urls_found": ["http://evil-bank.com"]
}
```

This is stored in your database and visible on the dashboard automatically.
