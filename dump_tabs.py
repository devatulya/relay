import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.google_sheets import GoogleSheetsService
import gspread

url = "https://docs.google.com/spreadsheets/d/1_bKLZEmmVmLDTrPRq6o1g4T543WUAbeoiSeN6q2qx5Q/edit"

try:
    service = GoogleSheetsService()
    service.connect()
    sheet = service.client.open_by_url(url)
    worksheets = sheet.worksheets()
    with open("tabs.txt", "w") as f:
        for ws in worksheets:
            f.write(ws.title + "\n")
    print("Tabs dumped successfully.")
except Exception as e:
    print("Error:", e)
