import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.google_sheets import GoogleSheetsService
from backend.services.creator_filter import filter_creators
from pprint import pprint

url = "https://docs.google.com/spreadsheets/d/1_bKLZEmmVmLDTrPRq6o1g4T543WUAbeoiSeN6q2qx5Q/edit"

payload = {
    "target_niches": ["beauty", "fashion", "ugc"],
    "brand_type": "Test",
    "max_budget": 5000,
    "deliverables": 1,
    "creator_categories": [],
}

try:
    service = GoogleSheetsService()
    service.connect()
    creators = service.fetch_creators(url)
    logs = service.fetch_outreach_log(url)
    
    suitable = filter_creators(creators, payload, logs)
    
    with open("creators_filtered.txt", "w", encoding="utf-8") as f:
        pprint(suitable, stream=f)
    print(f"Dump successful: {len(suitable)} suitable creators found.")
except Exception as e:
    print("Error:", e)
