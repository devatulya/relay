import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.google_sheets import GoogleSheetsService

service = GoogleSheetsService()
service.connect()
files = service.client.openall()
with open("sheets.txt", "w") as f:
    for file in files:
        f.write(f"{file.title}: {file.id}\n")
