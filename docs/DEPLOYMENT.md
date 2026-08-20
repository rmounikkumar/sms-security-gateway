# Deployment Guide - Free Public URL

Get a public URL like `https://sms-gateway.onrender.com` that works from anywhere in the world.

---

## Option 1: Render.com (FREE - Recommended)

### Step 1: Create GitHub Account
1. Go to https://github.com
2. Sign up for free

### Step 2: Install Git
```
Download from: https://git-scm.com/download/win
```

### Step 3: Push Code to GitHub

Open terminal in project folder and run:

```bash
cd "D:\span dection\sms-defense"

git init
git add .
git commit -m "SMS Security Gateway - Initial commit"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/sms-security-gateway.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy on Render

1. Go to https://render.com
2. Sign up with your GitHub account
3. Click **New +** -> **Web Service**
4. Connect your GitHub repo: `sms-security-gateway`
5. Configure:
   - **Name:** `sms-security-gateway`
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
   - **Instance Type:** Free
6. Click **Create Web Service**
7. Wait 5-10 minutes for first build
8. Your URL: `https://sms-security-gateway.onrender.com`

---

## Option 2: Railway.app ($5 free credit/month)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **New Project** -> **Deploy from GitHub repo**
4. Select your repo
5. Railway auto-detects Python and deploys
6. Go to Settings -> Networking -> Generate Domain
7. Your URL: `https://sms-security-gateway.up.railway.app`

---

## Option 3: PythonAnywhere (FREE - Easiest)

1. Go to https://www.pythonanywhere.com
2. Sign up for free
3. Go to **Dashboard** -> **Files**
4. Upload all project files
5. Go to **Dashboard** -> **Web**
6. Click **Add new web app**
7. Select **Flask** -> Python 3.x
8. Edit the WSGI file to point to your app.py
9. Click **Reload**
10. Your URL: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Update Your Phone After Deployment

Once deployed, update the Automate flow:

Old URL: `http://10.118.128.211:5000/api/analyze`
New URL: `https://sms-security-gateway.onrender.com/api/analyze`

Now your phone forwards SMS to the cloud - works from ANY WiFi, not just home network!

---

## How It All Connects

```
Phone (Automate/Tasker)
        |
        | HTTPS POST (any network)
        v
Render.com Cloud (https://sms-security-gateway.onrender.com)
        |
        v
Flask App + BERT-Tiny + SQLite + Dashboard
        |
        v
Anyone can view: https://sms-security-gateway.onrender.com/dashboard
```
