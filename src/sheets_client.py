import os

import gspread
from dotenv import load_dotenv

load_dotenv()

READY = "Ready to Process"
COLUMNS = ["Hotel ID", "Room Type", "Start Date", "End Date", "Status"]


def connect():
    """Open the worksheet using the Service Account credentials."""
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials/service-account.json")
    client = gspread.service_account(filename=creds_path)
    sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"])
    return sheet.worksheet(os.getenv("WORKSHEET_NAME", "Sheet1"))


def get_ready_rows(ws):
    """Return rows whose Status is 'Ready to Process', with their sheet row number."""
    records = ws.get_all_records(numericise_ignore=["all"])  # row 1 = header
    rows = []
    for i, record in enumerate(records, start=2):
        if str(record.get("Status", "")).strip() == READY:
            rows.append({"row": i, **record})
    return rows


def write_status(ws, row, status, message=""):
    """Write Success / Failed (+ optional error message) back to the Status column."""
    col = COLUMNS.index("Status") + 1
    ws.update_cell(row, col, f"{status}: {message}" if message else status)