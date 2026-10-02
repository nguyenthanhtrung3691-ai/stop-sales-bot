import os

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(os.environ["COLINKER_URL"])
    input("Dang nhap (ca OTP) trong trinh duyet, thay trang Colinker roi nhan Enter o day: ")
    context.storage_state(path="credentials/colinker_state.json")
    browser.close()