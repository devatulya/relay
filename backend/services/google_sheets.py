import gspread
from google.oauth2.service_account import Credentials
from backend.utils.logger import logger
import os
import json

# Scopes required for gspread v6+
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

class GoogleSheetsService:
    def __init__(self, credentials_file="credentials.json"):
        self.credentials_file = credentials_file
        self.client = None
        
    def connect(self):
        """
        Connects to Google Sheets using service account credentials.
        Tries environment variable GOOGLE_SHEETS_CREDS_JSON first, then fallback to file.
        """
        try:
            creds_json = os.getenv("GOOGLE_SHEETS_CREDS_JSON")
            
            if creds_json:
                logger.info("Loading Google credentials from environment variable...")
                creds_dict = json.loads(creds_json)
                self.client = gspread.service_account_from_dict(creds_dict, scopes=SCOPES)
            else:
                # Resolve relative to THIS file's directory (backend/services/) -> up one level -> backend/
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                creds_path = os.path.join(base_dir, self.credentials_file)
                
                if not os.path.exists(creds_path):
                    creds_path = self.credentials_file
                    
                if not os.path.exists(creds_path):
                    logger.error(f"Credentials file not found at {creds_path} and GOOGLE_SHEETS_CREDS_JSON not set.")
                    raise FileNotFoundError("Credentials not found (Checked ENV and JSON file)")
                
                logger.info(f"Loading Google credentials from file: {creds_path}")
                self.client = gspread.service_account(filename=creds_path, scopes=SCOPES)
            
            logger.info("Connected to Google Sheets API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise e

    def fetch_creators(self, sheet_url):
        """
        Fetches all records from 'Creators' sheet.
        """
        try:
            sheet = self.client.open_by_url(sheet_url)
            worksheet = sheet.worksheet("Creators")
            
            # Robust mapping to handle duplicate empty headers
            data = worksheet.get_all_values()
            if not data: return []
            headers = data[0]
            records = []
            for row in data[1:]:
                record = {}
                for i, h in enumerate(headers):
                    if h.strip(): # Ignore empty columns
                        record[h.strip()] = row[i] if i < len(row) else ""
                records.append(record)
                
            logger.info(f"Fetched {len(records)} creators")
            return records
        except Exception as e:
            logger.error(f"Error fetching creators: {e}")
            raise e

    def fetch_outreach_log(self, sheet_url):
        """
        Fetches all records from 'Outreach_Log' sheet.
        """
        try:
            sheet = self.client.open_by_url(sheet_url)
            try:
                worksheet = sheet.worksheet("Outreach_Log")
                data = worksheet.get_all_values()
                if not data: return []
                headers = data[0]
                records = []
                for row in data[1:]:
                    record = {}
                    for i, h in enumerate(headers):
                        if h.strip():
                            record[h.strip()] = row[i] if i < len(row) else ""
                    records.append(record)
                return records
            except gspread.exceptions.WorksheetNotFound:
                # If logs sheet doesn't exist, return empty list (or create it - but strict rules say just read/write)
                logger.warning("Outreach_Log sheet not found.")
                return []
        except Exception as e:
            logger.error(f"Error fetching outreach logs: {e}")
            raise e

    def log_outreach(self, sheet_url, log_data):
        """
        Appends a row to 'Outreach_Log'.
        log_data: {Name, Brand, Date, Status}
        """
        try:
            sheet = self.client.open_by_url(sheet_url)
            try:
                worksheet = sheet.worksheet("Outreach_Log")
            except gspread.exceptions.WorksheetNotFound:
                worksheet = sheet.add_worksheet(title="Outreach_Log", rows=1000, cols=4)
                worksheet.append_row(["Name", "Brand", "Date", "Status"])
            
            row = [
                log_data.get("Name"),
                log_data.get("Brand"),
                log_data.get("Date"),
                log_data.get("Status")
            ]
            worksheet.append_row(row)
            logger.info(f"Logged outreach for {log_data.get('Name')}")
        except Exception as e:
            logger.error(f"Error logging outreach: {e}")
            raise e

    def update_last_contacted(self, sheet_url, creator_name, date_str):
        """
        Updates 'Last Contacted' column for a specific creator in 'Creators' sheet.
        Note context: This is tricky with get_all_records logic unless we know row index.
        Optimization: We will search for the cell.
        """
        try:
            sheet = self.client.open_by_url(sheet_url)
            worksheet = sheet.worksheet("Creators")
            
            # Find the cell with creator name
            cell = worksheet.find(creator_name)
            if cell:
                # Assuming 'Last Contacted' is a specific column. We need to find the column index.
                # Headers are in row 1.
                header_row = worksheet.row_values(1)
                try:
                    col_idx = header_row.index("Last Contacted") + 1
                    worksheet.update_cell(cell.row, col_idx, date_str)
                    logger.info(f"Updated Last Contacted for {creator_name}")
                except ValueError:
                    logger.error("'Last Contacted' column not found.")
            else:
                logger.warning(f"Creator {creator_name} not found for update.")
                
        except Exception as e:
            logger.error(f"Error updating last contacted: {e}")
            # Non-critical enough to not crash the whole run? Requirement says "Stop safely on ANY error".
            # So we raise.
            raise e
