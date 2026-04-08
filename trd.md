
**Create a Technical Requirement Document (TRD) for building “Influenze Relay” using Python, Playwright, Flask, and Google Sheets API inside Antigravity IDE.**

---

## Architecture

Layers:

1. Flask Web App (UI + form handling)
2. Python Logic Layer (filtering, pricing, message building)
3. Google Sheets API (live creator database + logging)
4. Playwright (WhatsApp Web automation)
5. Runner process on local machine (always logged into WhatsApp)

---

## Folder Structure

```
influenze-relay/
│
├── app.py (Flask server)
├── main.py (orchestrator)
│
├── core/
│   ├── sheet_reader.py
│   ├── filter_logic.py
│   ├── pricing.py
│   ├── message_builder.py
│
├── automation/
│   └── whatsapp_sender.py
│
├── templates/
│   ├── welcome.html
│   ├── whatsapp_check.html
│   ├── form.html
│   ├── progress.html
│
└── requirements.txt
```

---

## Functional Flow

1. Flask form saves brand input
2. `sheet_reader.py` pulls creators from Google Sheet
3. `filter_logic.py` filters creators
4. `pricing.py` computes final price
5. `message_builder.py` prepares final message
6. `whatsapp_sender.py` opens WhatsApp Web and sends message
7. After sending, log to Google Sheet

---

## Key Constraints

* Do not use WhatsApp API
* Must use WhatsApp Web via Playwright
* Maintain 40-second delay
* Stop on any error
* Skip creators already contacted

---

## Execution Mode

* Flask runs as web dashboard
* main.py runs outreach when form is submitted
* System runs on a machine where WhatsApp Web is logged in

---

## Required Libraries

* flask
* playwright
* pandas
* gspread
* oauth2client
* time

---

## Output

A working internal web tool where founders can:

* Open website
* Enter brand details
* Start outreach
* See progress
* System sends messages automatically

---

