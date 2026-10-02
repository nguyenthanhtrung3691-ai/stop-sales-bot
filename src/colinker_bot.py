import os
import re
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from logger import get_logger

load_dotenv()
log = get_logger()

STATE_FILE = "credentials/colinker_state.json"
STATUS_CLOSED = "N"  # gia tri dropdown "batch-room-status-type" = dong ban (Stop Sale)


class SessionExpired(Exception):
    """Phien dang nhap het han, can chay lai login_once.py."""


class ColinkerBot:
    def __init__(self):
        self.headless = os.getenv("HEADLESS", "true").lower() == "true"
        self.url = os.environ["COLINKER_URL"]

    def __enter__(self):
        if not Path(STATE_FILE).exists():
            raise SessionExpired("Chua co phien dang nhap. Chay: python login_once.py")
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(storage_state=STATE_FILE)
        self.page = self.context.new_page()
        self.page.set_default_timeout(30000)
        try:
            self._check_logged_in()
        except Exception:
            self.__exit__()
            raise
        return self

    def __exit__(self, *exc):
        self.browser.close()
        self._pw.stop()

    def _check_logged_in(self):
        self.page.goto(self.url)
        try:
            self.page.get_by_role("link", name="Hotel", exact=True).wait_for(timeout=15000)
        except Exception:
            raise SessionExpired("Phien dang nhap het han. Chay lai: python login_once.py")

    def process(self, req, save=True):
        """Dong ban (Stop Sale) phong req.room_type cua req.hotel_id tu start_date den end_date."""
        page = self.page
        page.goto(self.url)
        page.get_by_role("link", name="Hotel", exact=True).click()

        # 1. Tim khach san theo Hotel ID
        page.get_by_label("Hotel Hotelid Hotel note").select_option("2")
        page.locator("#txtKeyword2").fill(req.hotel_id)
        page.get_by_role("button", name="Search").click()

        # 2. Cho danh sach loc xong: chi con DUNG 1 khach san (1 link "Room")
        table = page.locator("#ppTabHotelData")
        room_links = table.get_by_role("link", name="Room", exact=True)
        n = -1
        for _ in range(60):  # toi da khoang 30 giay
            n = room_links.count()
            if n == 1:
                break
            page.wait_for_timeout(500)
        if n != 1:
            raise ValueError(f"Tim ID {req.hotel_id} ra {n} khach san (can dung 1)")

        # An toan: dong con lai phai chua dung ma khach san
        if table.get_by_text(f"({req.hotel_id})").count() == 0:
            raise ValueError(f"Dong ket qua khong chua ma khach san {req.hotel_id}")

        # 3. Mo tab Room cua khach san do
        room_links.first.click()
        try:
            page.get_by_text(f"({req.hotel_id})").first.wait_for(timeout=15000)
        except Exception:
            raise ValueError(f"Khong mo duoc trang phong cua khach san {req.hotel_id}")
        page.wait_for_load_state("networkidle")
        self.screenshot(f"row{req.row}_hotel")

        # 4. Chon loai phong (ten phai khop chinh xac voi Colinker)
        page.get_by_role("checkbox", name=req.room_type, exact=True).check()

        # 5. Doi trang thai
        page.get_by_role("link", name="Change status").click()
        self._set_dates(req)
        page.locator('select[name="batch-room-status-type"]').select_option(STATUS_CLOSED)

        if save:
            page.locator("#batchSaveBtn").click()
            page.get_by_role("button", name="Complete").click()

    def _set_dates(self, req):
        page = self.page
        start = req.start_date.strftime("%Y-%m-%d")
        end = req.end_date.strftime("%Y-%m-%d")
        expected = f"{start} - {end}"
        box = page.locator('input[name="fromToDate"]').first

        # Cach 1: go truc tiep vao o ngay
        box.click()
        box.press("Control+A")
        box.type(expected, delay=30)
        box.press("Enter")
        page.wait_for_timeout(500)
        if self._dates_ok(box, expected):
            return

        # Cach 2: bam chon tren lich
        box.click()
        self._pick_day(req.start_date)
        self._pick_day(req.end_date)
        page.wait_for_timeout(500)
        if not self._dates_ok(box, expected):
            raise ValueError(
                f"Khong chon duoc ngay. Dang hien '{box.input_value()}', can '{expected}'"
            )

    @staticmethod
    def _dates_ok(box, expected):
        current = re.sub(r"\s+", " ", box.input_value().strip())
        return current == expected

    def _pick_day(self, d):
        cal = self.page.locator(".daterangepicker:visible").first
        cal.locator("select.monthselect").first.select_option(str(d.month - 1))
        cal.locator("select.yearselect").first.select_option(str(d.year))
        cal.locator(".left td.available:not(.off)").get_by_text(str(d.day), exact=True).first.click()

    def screenshot(self, name):
        Path("screenshots").mkdir(exist_ok=True)
        path = f"screenshots/{name}.png"
        self.page.screenshot(path=path, full_page=True)
        return path