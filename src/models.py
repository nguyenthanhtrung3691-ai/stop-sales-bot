from dataclasses import dataclass
from datetime import date, datetime

# Định dạng ngày trong Sheet: ngày/tháng/năm (vd 05/10/2026 = 5 tháng 10)
DATE_FORMAT = "%d/%m/%Y"


@dataclass
class StopSaleRequest:
    row: int
    hotel_id: str
    room_type: str
    start_date: date
    end_date: date


def _parse_date(value, label):
    try:
        return datetime.strptime(str(value).strip(), DATE_FORMAT).date()
    except ValueError:
        raise ValueError(f"{label} sai dinh dang (can dd/mm/yyyy): '{value}'")


def parse_request(record):
    """Convert one Sheet row into a StopSaleRequest, or raise ValueError."""
    hotel_id = str(record.get("Hotel ID", "")).strip()
    room_type = str(record.get("Room Type", "")).strip()
    if not hotel_id:
        raise ValueError("thieu Hotel ID")
    if not room_type:
        raise ValueError("thieu Room Type")

    start = _parse_date(record.get("Start Date", ""), "Start Date")
    end = _parse_date(record.get("End Date", ""), "End Date")
    if start > end:
        raise ValueError("Start Date lon hon End Date")

    return StopSaleRequest(record["row"], hotel_id, room_type, start, end)