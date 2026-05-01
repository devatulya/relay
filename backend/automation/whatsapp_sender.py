from playwright.async_api import async_playwright
import asyncio
import random
from backend.utils.logger import logger
import urllib.parse
import time

class WhatsAppBot:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def launch(self, headless=False):
        """
        Launches the browser and opens WhatsApp Web (Async).
        """
        try:
            self.playwright = await async_playwright().start()
            # User data dir to persist session
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir="wa_session",
                channel="chrome", 
                headless=headless,
                no_viewport=True,
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
            )
            self.page = self.context.pages[0]
            await self.page.goto("https://web.whatsapp.com")
            
            logger.info("WhatsApp Web opened.")
            return True
        except Exception as e:
            logger.error(f"Failed to launch WhatsApp: {e}")
            if self.playwright:
                await self.playwright.stop()
            raise e

    async def is_logged_in(self):
        """
        Checks if WhatsApp is logged in (Async).
        """
        try:
            logger.info("Checking login status...")
            selectors = ["#pane-side", "#side", "div[data-testid='chat-list-search']"]
            
            for selector in selectors:
                try:
                    await self.page.wait_for_selector(selector, state="visible", timeout=5000)
                    logger.info(f"WhatsApp is logged in (found {selector}).")
                    return True
                except:
                    continue
            
            if await self.page.is_visible("canvas"):
                logger.info("QR Code detected. Not logged in.")
                return False
                
            try:
                await self.page.wait_for_selector("#pane-side", state="visible", timeout=10000)
                logger.info("WhatsApp is logged in (found #pane-side after wait).")
                return True
            except:
                pass
                
            logger.error("Login check failed. Could not find sidebar and no QR code.")
            return False
            
        except Exception as e:
            logger.error(f"Login check failed or timed out: {e}")
            return False

    async def send_message(self, phone, message, stop_check=None):
        """
        Sends a message (Async).
        """
        try:
            logger.info(f"Preparing to send to {phone}")
            phone = str(phone).replace("+", "").strip()
            encoded_msg = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
            
            await self.page.goto(url)
            
            logger.info("Waiting for chat to load...")
            # Try generic selector first, then specific
            textbox_selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][data-tab="6"]', # Sometimes seen
                'div[contenteditable="true"]'
            ]
            
            textbox = None
            for selector in textbox_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    textbox = self.page.locator(selector).first
                    if await textbox.is_visible():
                        break
                except:
                    continue
            
            if not textbox:
                # Last ditch check for invalid number
                if await self.page.is_visible("text=Phone number shared via url is invalid"):
                     logger.error(f"Invalid phone number: {phone}")
                     return "Invalid Number"
                else:
                     raise Exception("Chat failed to load (no textbox found)")

            # Focus and ensure we are ready
            await textbox.click()
            
            await asyncio.sleep(2)
            await self.page.keyboard.press("Enter")
            logger.info("Message sent (pressed Enter).")
            
            if stop_check and stop_check():
                return "Stopped"

            wait_time = random.randint(35, 200)
            logger.info(f"Waiting {wait_time}s safe delay (interruptible)...")
            # Break delay into 1s chunks
            for _ in range(wait_time):
                if stop_check and stop_check():
                    logger.warning("Stop detected during delay! Breaking sleep.")
                    return "Stopped"
                await asyncio.sleep(1)
            
            return "Sent"
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return "Failed"

    async def close(self):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed.")
