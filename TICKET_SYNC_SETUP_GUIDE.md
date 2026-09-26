# Ticket Sync Setup Guide - Simple Explanation

## What You're Trying To Do

You want to **copy tickets** from one site to another:

```
┌─────────────────┐                    ┌─────────────────┐
│  MEDSERVICE     │                    │   TBOINDIA      │
│  (Source Site)  │  ──────────────>   │ (Current Site)  │
│                 │   Copy Tickets     │                 │
│  Has tickets    │                    │  Gets copies    │
└─────────────────┘                    └─────────────────┘
```

## Why You're Getting 401 Error

The error means: **"I don't have permission to access medservice site"**

It's like trying to enter a building without the right key card.

## What You Need

To connect two sites, you need **3 things**:

1. **URL** - Where is medservice? (like an address)
2. **API Key** - Username (like a key card)
3. **API Secret** - Password (the secret code)

## Step-by-Step Fix

### Step 1: Check What You Have Now

Run this command:
```bash
bench --site tboindia execute customer_support.check_sync_config.check
```

This will show you what's currently configured.

You'll probably see something like:
```
Site URL: http://127.0.0.1:8000
API Key: 06822d3cf66fe76...
API Secret: SET (24 chars)
```

**The problem:** The URL `http://127.0.0.1:8000` is pointing to ITSELF (tboindia), not to medservice!

---

### Step 2: Find Out Where Medservice Is

**Option A:** If medservice is on the SAME computer but different port:

You need to start medservice on a different port. Open a NEW terminal window:

```bash
cd /Users/nahala/frappe-bench
bench --site medservice serve --port 8001
```

Keep this window open! Now medservice is running at: `http://127.0.0.1:8001`

**Option B:** If medservice is on a DIFFERENT computer:

Find out its URL, like:
- `http://192.168.1.50:8000` (local network)
- `https://medservice.mycompany.com` (internet)

---

### Step 3: Get the Keys from Medservice

You need to create an API Key and Secret **ON THE MEDSERVICE SITE**.

#### Method 1: Via Browser (Easiest)

1. Open medservice in your browser:
   - If local: `http://127.0.0.1:8001`
   - If remote: whatever URL medservice uses

2. Login to medservice

3. Go to: **User** → Click on **Administrator**

4. Scroll down to **"API Access"** section

5. Click **"Generate Keys"** button

6. You'll see:
   ```
   API Key: abc123def456
   API Secret: xyz789uvw012
   ```

7. **COPY BOTH!** Write them down! The secret won't show again!

#### Method 2: Via Command (if you prefer)

```bash
bench --site medservice execute customer_support.generate_api_credentials.generate
```

This will print the API Key and Secret. Copy them!

---

### Step 4: Update Configuration on tboindia

Now go back to tboindia and tell it how to connect to medservice.

#### Method 1: Via Browser (Easiest)

1. Open tboindia: `http://127.0.0.1:8000`

2. In the search bar, type: **"Ticket Sync Source"**

3. Click on **"Medservice"** (or whatever the name is)

4. Update these fields:
   ```
   Site Name: Medservice (any friendly name)
   Site URL: http://127.0.0.1:8001 (or wherever medservice is)
   API Key: [paste the key from Step 3]
   API Secret: [paste the secret from Step 3]
   Enabled: ✓ (check this box)
   ```

5. Click **Save**

#### Method 2: Via Command

```bash
bench --site tboindia console
```

Then type:
```python
import frappe

# Get the sync configuration
doc = frappe.get_doc("Ticket Sync Source", "Medservice")

# Update it with the RIGHT information
doc.site_url = "http://127.0.0.1:8001"  # Change this to where medservice is!
doc.api_key = "PUT_YOUR_API_KEY_HERE"
doc.set_value("api_secret", "PUT_YOUR_API_SECRET_HERE")
doc.enabled = 1
doc.save()

frappe.db.commit()
print("Updated!")
```

Press Ctrl+D to exit the console.

---

### Step 5: Test It

Run this command to test if it works:

```bash
bench --site tboindia execute customer_support.diagnose_sync.diagnose
```

**If it works**, you'll see:
```
✓ Connection and authentication working!
  Authenticated as: Administrator
```

**If it still fails**, you'll see:
```
✗ Authentication FAILED (401)
  → Regenerate API Key/Secret on source site
```

If it fails, go back to Step 3 and generate NEW keys.

---

### Step 6: Sync Tickets

Once Step 5 works, run the actual sync:

```bash
bench --site tboindia execute customer_support.customer_support.sync_tickets.sync_remote_tickets
```

**Success looks like:**
```
[{"site": "medservice", "created": 5, "updated": 0, "status": "ok"}]
```

This means it copied 5 tickets from medservice!

**Failure looks like:**
```
[{"site": "medservice", "status": "error", "error": "401 Client Error..."}]
```

This means the keys are still wrong.

---

## Quick Troubleshooting

### Problem: "Cannot connect to site"
**Fix:** Make sure medservice is running! Check Step 2.

### Problem: "401 Unauthorized"
**Fix:** The API Key/Secret are wrong. Go back to Step 3 and generate new ones.

### Problem: "Site URL is wrong"
**Fix:** Make sure the URL doesn't end with `/app`. Should be:
- ✅ `http://127.0.0.1:8001`
- ❌ `http://127.0.0.1:8001/app`

---

## Summary Checklist

- [ ] I know where medservice is (URL or port)
- [ ] Medservice is running and accessible
- [ ] I generated API Key + Secret on medservice
- [ ] I updated the Ticket Sync Source on tboindia with:
  - [ ] Correct URL
  - [ ] API Key
  - [ ] API Secret
- [ ] I tested with `diagnose_sync.diagnose` and it says ✓
- [ ] I ran the sync and it worked!

---

## Still Confused?

Run these commands in order and send me the output:

```bash
# 1. Check what's configured now
bench --site tboindia execute customer_support.check_sync_config.check

# 2. Test the connection
bench --site tboindia execute customer_support.diagnose_sync.diagnose
```

Send me what you see, and I'll tell you exactly what's wrong!
