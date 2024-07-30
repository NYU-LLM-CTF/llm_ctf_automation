from .tool_modules import *
from playwright.async_api import async_playwright
# from tarsier import Tarsier, GoogleVisionOCRService
import asyncio
class OpenBrowserTool(Tool):
    NAME = "Open_Browser"
    def __init__(self, challenge: "CTFChallenge"):
        super().__init__()
        self.challenge = challenge
    
    # def load_google_cloud_credentials(json_file_path):
    #     with open(json_file_path) as f:
    #         credentials = json.load(f)
    #     return credentials

    async def __call__(self, url: Annotated[str, "URL to open"]):
        """
        Open a browser to the specified URL and return the page object.
        """
   #add tarsier stuff
        #google_cloud_credentials = self.load_google_cloud_credentials('~/.google_service/google_service_acc_key.json')
    # Setup Tarsier
        #ocr_service = GoogleVisionOCRService(google_cloud_credentials)
        #tarsier = Tarsier(ocr_service)
        #tag_to_xpath = {}
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            try:
                page = await browser.new_page()
                await page.goto(url)
                page_content = await page.content()
            finally:
                await browser.close()
        
        return {"page_content": page_content}
