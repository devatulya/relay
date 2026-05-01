from backend.services.google_sheets import GoogleSheetsService
from backend.services.creator_filter import filter_creators
from backend.services.pricing import calculate_final_price
from backend.services.message_builder import build_message
from backend.automation.whatsapp_sender import WhatsAppBot
from backend.utils.logger import logger
from datetime import datetime
import time
import random
import asyncio

class OutreachOrchestrator:
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        self.whatsapp_bot = None
        
        # State Tracking
        self.status = "idle" # idle, running, completed, stopped, error
        self.total_creators = 0
        self.sent_count = 0
        self.current_target = None
        self.logs = [] # List of strings/dicts for frontend logs
        self.stop_requested = False
        self.start_time = None
        self.end_time = None
        self.results = [] # Detailed results for final export

    async def start_outreach(self, payload):
        """
        Main execution flow (Async).
        """
        try:
            logger.info("Starting outreach process...")
            
            self.status = "running"
            self.logs = [] # Clear previous logs
            self.sent_count = 0 

            
            # 1. Validate Payload
            required_keys = ["google_sheet_url"]
            for key in required_keys:
                if not payload.get(key):
                    raise ValueError(f"Missing required key: {key}")

            self.add_log("INFO", "Validating payload... OK")

            # 2. Connect to Sheets
            self.add_log("INFO", "Connecting to Google Sheets...")
            self.sheets_service.connect()
            
            # 3. Fetch Creators & Logs
            sheet_url = payload["google_sheet_url"]
            self.add_log("INFO", f"Fetching creators from {sheet_url}...")
            creators = self.sheets_service.fetch_creators(sheet_url)
            logs = self.sheets_service.fetch_outreach_log(sheet_url)
            
            # 4. Filter Creators
            self.add_log("INFO", "Filtering creators...")
            suitable_creators = filter_creators(creators, payload, logs)
            logger.info(f"Found {len(suitable_creators)} suitable creators after filtering.")
            self.add_log("INFO", f"Found {len(suitable_creators)} suitable creators.")
            
            if not suitable_creators:
                self.add_log("WARNING", "No creators found. Stopping.")
                logger.info("No suitable creators found. Here are all creators parsed:")
                logger.info(creators[:3])  # dump top 3 to see what was parsed
                self.status = "completed"
                return {"status": "completed", "message": "No suitable creators found."}

            # 5. Pass all suitable creators to the preview UI
            creators_to_contact = suitable_creators
            self.total_creators = len(creators_to_contact)
            
            # 6. We no longer launch WhatsApp here, just render messages to return
            results = []

            # 7. Iterate and generate message
            for i, creator in enumerate(creators_to_contact):
                try:
                    name = creator.get("Name")
                    phone = creator.get("cleaned_phone", str(creator.get("Number", creator.get("WhatsApp", ""))))
                    rate = creator.get("Price", creator.get("Rate", 0))
                    
                    self.current_target = name
                    self.add_log("PENDING", f"Preparing message for {name}...")

                    # Determine final rate to use in message from the filter
                    final_price = creator.get('final_message_rate', rate)
                    
                    # Build Message using exact template mapping
                    message_template = payload.get("message_template", payload.get("outreach_message", ""))
                    message = build_message(
                        template=message_template, 
                        final_price=final_price,
                        brand_type=payload.get("brand_type", ""),
                        deliverables=payload.get("deliverables", 1),
                        product_value=payload.get("product_value", 0),
                        product_retainable=payload.get("product_retainable", "Yes"),
                        creator_name=name,
                        creator_niche=creator.get("Niche", "")
                    )
                    
                    # Store generated message
                    results.append({
                        "creator_name": name,
                        "niche": creator.get("Niche", ""),
                        "final_price": final_price,
                        "phone": phone,
                        "ig_link": creator.get("IG Link", ""),
                        "final_message": message
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing creator {creator.get('Name')}: {e}")
                    self.add_log("ERROR", f"Error with {creator.get('Name')}: {str(e)}")
                    self.status = "error"
                    raise e
                    
            self.add_log("INFO", f"Generation complete. Rendered {len(results)} messages.")
            self.status = "completed"
            return {"status": "completed", "results": results}

        except Exception as e:
            logger.error(f"Orchestrator failed: {e}")
            self.add_log("CRITICAL", f"Process failed: {str(e)}")
            self.status = "error"
            raise e
            
    async def execute_outreach(self, payload):
        """
        Executes the messaging loop using the exact creator list passed from the preview page.
        """
        try:
            logger.info("Starting execution phase...")
            self.status = "running"
            self.sent_count = 0
            self.stop_requested = False
            self.start_time = time.time()
            self.end_time = None
            self.results = []
            
            next_break_at = random.randint(15, 20)
            
            creators_to_contact = payload.get("creators", [])
            sheet_url = payload.get("google_sheet_url")
            brand_name = payload.get("brand_name", "Unknown Brand")
            
            self.total_creators = len(creators_to_contact)
            
            if not creators_to_contact:
                self.add_log("WARNING", "No creators provided for execution. Stopping.")
                self.status = "completed"
                self.end_time = time.time()
                return
                
            self.add_log("INFO", f"Connecting back to Google Sheets...")
            self.sheets_service.connect()
            
            # Start WhatsApp if not started
            state = await self.check_connection(launch_browser=True)
            if state != "connected":
                raise Exception("WhatsApp is not connected! Please scan QR code in the browser first.")
                
            for i, creator in enumerate(creators_to_contact):
                # Check for stop request
                if self.stop_requested:
                    self.add_log("WARNING", "Emergency stop received. Halting campaign...")
                    self.status = "stopped"
                    break

                try:
                    name = creator.get("creator_name")
                    phone = creator.get("phone")
                    message = creator.get("final_message")
                    ig_link = creator.get("ig_link", "")
                    
                    self.current_target = name
                    self.add_log("PENDING", f"Sending to {name} ({phone})...")
                    
                    phone_str = str(phone)
                    phone_digits = ''.join(c for c in phone_str if c.isdigit() or c == '+')
                    
                    status = "Failed"
                    if len(phone_digits) < 8:
                        self.add_log("WARNING", f"Skipping {name}: Invalid phone number '{phone}'")
                    else:
                        # Pass stop_check to allow interrupting the 40s sleep
                        status = await self.whatsapp_bot.send_message(
                            phone_digits, 
                            message, 
                            stop_check=lambda: self.stop_requested
                        )
                    
                    if status == "Stopped":
                        self.add_log("WARNING", f"Campaign stopped before sending to {name}")
                        self.status = "stopped"
                        break

                    sent_success = (status == "Sent")
                    if sent_success:
                        self.sent_count += 1
                        self.add_log("SUCCESS", f"Message sent to {name}")
                        
                        # Log to Google Sheet
                        try:
                            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_data = {
                                "Name": name,
                                "Brand": brand_name,
                                "Date": date_str,
                                "Status": "Sent"
                            }
                            self.sheets_service.log_outreach(sheet_url, log_data)
                            self.sheets_service.update_last_contacted(sheet_url, name, date_str)
                        except Exception as sheet_err:
                            self.add_log("WARNING", f"Failed to log {name} to sheet: {sheet_err}")
                            
                        # Long random break logic to prevent ban
                        if self.sent_count >= next_break_at:
                            long_pause = random.randint(600, 900) # 10 to 15 minutes
                            self.add_log("INFO", f"Taking a random long break for {long_pause // 60} minutes and {long_pause % 60} seconds to avoid detection...")
                            for _ in range(long_pause):
                                if self.stop_requested:
                                    break
                                await asyncio.sleep(1)
                            
                            next_break_at += random.randint(15, 20)
                    
                    # Store for export
                    self.results.append({
                        "name": name,
                        "number": phone,
                        "ig_link": ig_link,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "sent": "Yes" if sent_success else "No"
                    })
                            
                except Exception as e:
                    self.add_log("ERROR", f"Failed to send to {creator.get('creator_name')}: {e}")
                    # Continue to the next creator instead of stopping the whole process
                    continue
            
            if self.status != "stopped":
                self.add_log("INFO", f"Execution complete. Sent {self.sent_count} messages.")
                self.status = "completed"
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            self.add_log("CRITICAL", f"Execution failed: {str(e)}")
            self.status = "error"
            raise e
        finally:
            self.end_time = time.time()

    def stop(self):
        """
        Request the current outreach to stop.
        """
        self.stop_requested = True
        logger.warning("Stop request received by Orchestrator.")

    async def check_connection(self, launch_browser=True):
        """
        Just opens the browser to check login (Async).
        """
        try:
            # Reuse existing bot if available
            if self.whatsapp_bot:
                 logger.info("Found existing bot instance.")
                 try:
                     # Simple check if page is accessible
                     if self.whatsapp_bot.page and not self.whatsapp_bot.page.is_closed():
                        try:
                            title = await self.whatsapp_bot.page.title()
                            logger.info(f"Bot page is active. Title: {title}")
                        except Exception:
                            logger.warning("Bot page unresponsive during title check.")
                            self.whatsapp_bot = None
                     else:
                        logger.warning("Bot page reported closed.")
                        self.whatsapp_bot = None
                 except Exception as e:
                     logger.warning(f"Bot connection lost (forcing reset). Error: {e}")
                     self.whatsapp_bot = None

            if not self.whatsapp_bot:
                logger.info(f"No active bot. Launch param: {launch_browser}")
                if launch_browser:
                    self.whatsapp_bot = WhatsAppBot()
                    await self.whatsapp_bot.launch(headless=False)
                else:
                    return "not_connected"
            
            logger.info("Checking login status via bot...")
            status = await self.whatsapp_bot.is_logged_in()
            logger.info(f"Bot returned logged_in status: {status}")
            return "connected" if status else "not_connected"
        except Exception as e:
            logger.error(f"Connection check error: {e}")
    def add_log(self, level, message):
        """
        Adds a log entry to the in-memory state.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })
        # Keep logs manageable
        if len(self.logs) > 50:
            self.logs.pop(0)

    def get_status(self):
        """
        Returns the current state.
        """
        duration = 0
        if self.start_time:
            end = self.end_time if self.end_time else time.time()
            duration = int(end - self.start_time)
            
        return {
            "status": self.status,
            "total_creators": self.total_creators,
            "sent_count": self.sent_count,
            "current_target": self.current_target,
            "duration": duration,
            "logs": self.logs,
            "results": self.results
        }

