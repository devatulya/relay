---
description: Show help and available commands for the Influenze Relay project
---

Display the following help information to the user in a well-formatted markdown response:

---

## 🚀 Influenze Relay — Help & Commands

**Influenze Relay** is an AI-powered WhatsApp outreach tool for influencer marketing. It reads creator data from Google Sheets, filters eligible creators, and sends personalized WhatsApp messages automatically.

---

### ▶️ Running the App

| Command | Description |
|---|---|
| `python run.py` | Start the Flask backend server on port 5000 |
| `python main.py` | Run the orchestrator entry point |
| `pytest tests/` | Run all tests |

---

### 📁 Project Structure

| Path | Purpose |
|---|---|
| `run.py` | App entry point — starts Flask on port 5000 |
| `main.py` | Orchestrator stub |
| `app.py` | Root-level Flask app |
| `backend/app.py` | Main Flask backend with all routes |
| `backend/services/creator_filter.py` | Filters creators by niche, age, category |
| `backend/services/google_sheets.py` | Reads/writes Google Sheets data |
| `backend/services/message_builder.py` | Builds personalized WhatsApp messages |
| `backend/services/pricing.py` | Calculates outreach price (min of budget vs rate) |
| `backend/automation/whatsapp_sender.py` | Sends WhatsApp messages via WhatsApp Web |
| `backend/credentials.json` | Google Sheets API credentials (keep secret!) |
| `templates/` | All HTML frontend pages |
| `tests/` | Pytest test suite |

---

### 🌐 Frontend Pages

| Page | File | Purpose |
|---|---|---|
| Welcome | `templates/welcome.html` | Landing page |
| WhatsApp Check | `templates/whatsapp_check.html` | QR login / session check |
| Campaign Form | `templates/form.html` | Brand input form |
| Progress | `templates/progress.html` | Live outreach progress |
| Summary | `templates/summary.html` | Completion summary |
| Profile | `templates/profile.html` | User profile |
| Help | `templates/help.html` | In-app help page |
| Docs | `templates/docs.html` | Documentation |

---

### ⚙️ User Flow

1. **Welcome** → Click "Let's Get Started"
2. **WhatsApp Check** → Scan QR code if not logged in
3. **Form** → Enter brand name, niche, age range, budget, category, message, Google Sheet link
4. **Outreach Starts** → System filters creators and sends messages (1 per 40 seconds)
5. **Progress** → Watch live progress
6. **Summary** → View results and log

---

### 🔑 Creator Eligibility Rules

- Niche must match
- Age must be in specified range
- Category must NOT be "Bad"
- Creator must NOT have been contacted for the same brand before

**Priority order:** Good → Average → Closest rate to budget

---

### 💰 Pricing Rule

`Outreach Price = min(brand_budget, creator_rate)`

---

### 📋 Available Workflows (Slash Commands)

| Command | Description |
|---|---|
| `/gsd:help` | Show this help page |

---

### 🛠️ Setup Requirements

1. Install dependencies: `pip install -r requirements.txt`
2. Place `credentials.json` in `backend/` (Google Sheets API key)
3. Ensure WhatsApp Web session is active in `wa_session/`
4. Run: `python run.py`
