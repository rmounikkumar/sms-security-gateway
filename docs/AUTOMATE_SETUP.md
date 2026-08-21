# Automate SMS Forwarder Setup Guide

## What is Automate?
Free Android app that connects blocks to create automation flows.
No coding required - just drag and connect blocks.

## Download
Play Store -> Search "Automate" by "Simple Apps" -> Install (FREE)

---

## Flow to Create

```
[Flow beginning] -> [SMS received] -> [HTTP request]
```

---

## Step-by-Step Instructions

### 1. Open Automate app

### 2. Create new flow
- Tap **+** button (bottom right)
- Blank canvas appears

### 3. Add "SMS received" block
- Tap **+** (bottom center)
- Tap **TRIGGERS** tab (top)
- Scroll to **"SMS received"**
- Tap it -> Blue block appears on canvas

### 4. Add "HTTP request" block
- Tap **+** (bottom center)
- Tap **ACTIONS** tab (top)
- Scroll to **"HTTP request"**
- Tap it -> Green block appears on canvas

### 5. Connect all three blocks
- Tap and hold the **bottom dot** of "Flow beginning"
- Drag to the **top dot** of "SMS received"
- Tap and hold the **bottom dot** of "SMS received"
- Drag to the **top dot** of "HTTP request"

Result: A connected chain of 3 blocks

### 6. Configure HTTP request
Tap the green "HTTP request" block. Fill in:

| Field | Value |
|-------|-------|
| Method | `POST` |
| URL | `http://10.118.128.211:5000/api/analyze` |
| Content Type | `application/json` |
| Content Body | `{"sender": {phone_number}, "message": {text}}` |

**For Content Body:**
1. Tap the Content Body field
2. Select **text** type
3. Type: `{"sender": `
4. Tap the **{x} variable button** near keyboard
5. Select **phone_number** from list
6. Type: `, "message": `
7. Tap **{x}** again
8. Select **text** from list
9. Type: `}`

### 7. Start the flow
- Tap **Play button** (triangle, bottom right)
- Allow all permissions (SMS, Phone, Internet)
- Green checkmarks appear on blocks = working!

### 8. Test
- Ask someone to send you an SMS
- Check dashboard at: `http://localhost:5000/dashboard`

---

## Troubleshooting

### "Flow won't start"
- Settings -> Apps -> Automate -> Permissions -> Enable SMS, Phone
- Settings -> Apps -> Automate -> Battery -> Unrestricted

### "Flow runs but no events on dashboard"
- Make sure PC is running `python app.py`
- Make sure phone and PC are on same WiFi
- Check PC IP: run `ipconfig` in terminal, look for IPv4 Address
- Test connection: open phone browser -> go to `http://YOUR_PC_IP:5000/api/stats`

### "HTTP request block has no Body field"
- Make sure Method is set to **POST** (not GET)
- Body field only appears when POST is selected

### "Variables {phone_number} and {text} not working"
- Type them as plain text: `{"sender": {phone_number}, "message": {text}}`
- OR use variable picker ({x} button) to insert them

### "Can't find HTTP request in actions"
- Make sure you tap **ACTIONS** tab (not TRIGGERS)
- Scroll down - it's usually in the middle of the list
- Search: type "http" in the search box at top
