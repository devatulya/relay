


**Create a Product Requirement Document (PRD) for a web-based internal tool called “Influenze Relay”.**

## Product Purpose

Influenze Relay is an internal AI-powered outreach tool used by an influencer marketing agency to automatically send the first WhatsApp message to suitable creators based on brand requirements.

The tool must reduce manual effort in:

* Searching creators
* Checking eligibility
* Sending WhatsApp outreach one-by-one

After the first message is sent, humans handle all further communication.

---

## Core Concept

The system should:

1. Take brand requirements from a web interface
2. Read creator data from a Google Sheet (live database)
3. Apply strict filtering rules
4. Calculate correct outreach payment
5. Send WhatsApp messages one-by-one with 40-second delay
6. Log all activity back to Google Sheet

---

## User Flow

1. Welcome screen → “Let’s Get Started”
2. WhatsApp Web session check (QR login if needed)
3. Brand input form:

   * Brand name
   * Required niche
   * Age range
   * Budget
   * Allowed category
   * Outreach message
   * Google Sheet link
4. Start outreach
5. Live progress screen
6. Completion summary

---

## Creator Selection Rules

A creator is eligible only if:

* Niche matches
* Age in range
* Category is not “Bad”
* Not contacted earlier for same brand

Priority:

* Good category first
* Average next
* Rates closest to budget

---

## Pricing Logic

Final outreach price shown in message = minimum of (brand budget, creator rate)

---

## WhatsApp Rules

* Use personal WhatsApp Web
* One message every 40 seconds
* Human-like behavior
* Stop if WhatsApp logs out

---

## Data Structure (Google Sheet)

Sheet: Creators

* Name | Niche | Age | Category | Rate | WhatsApp | Last Contacted

Sheet: Outreach_Log

* Name | Brand | Date | Status

---

## Success Criteria

* Founders can use via website
* No code needed to run
* Messages sent safely
* Data stays in Google Sheets

---

