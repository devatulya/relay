import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.google_sheets import GoogleSheetsService
import gspread

service = GoogleSheetsService()
service.connect()

print("Listing all spreadsheets accessible by the service account:")
try:
    # Use Drive API to list files
    client = service.client
    files = client.openall()
    if not files:
        print("No spreadsheets found! Service account has access to 0 sheets.")
    for f in files:
        print(f"Title: {f.title}, ID: {f.id}")
except Exception as e:
    import traceback
    traceback.print_exc()
