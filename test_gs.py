import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.google_sheets import GoogleSheetsService
import gspread

url = "https://docs.google.com/spreadsheets/d/1_bKLZEmmVmLDTrPRq6o1g4T543WUAbeolSeN6q2qx5Q/edit"
sheet_id = "1_bKLZEmmVmLDTrPRq6o1g4T543WUAbeolSeN6q2qx5Q"

try:
    print("Connecting...")
    service = GoogleSheetsService()
    service.connect()
    
    print(f"Opening sheet {sheet_id}...")
    spreadsheet = service.client.open_by_key(sheet_id)
    print(spreadsheet.title)
except Exception as e:
    import traceback
    traceback.print_exc()
