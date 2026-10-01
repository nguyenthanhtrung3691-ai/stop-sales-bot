import argparse

from logger import get_logger
from models import parse_request
from sheets_client import connect, get_ready_rows, write_status

log = get_logger()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Chi doc va kiem tra, khong ghi gi len Sheet")
    args = parser.parse_args()

    ws = connect()
    rows = get_ready_rows(ws)
    log.info("Found %d row(s) ready to process", len(rows))

    for record in rows:
        try:
            req = parse_request(record)
        except ValueError as e:
            log.error("Row %s invalid: %s", record["row"], e)
            if not args.dry_run:
                write_status(ws, record["row"], "Failed", str(e))
            continue

        log.info("Row %s OK: %s | %s | %s -> %s",
                 req.row, req.hotel_id, req.room_type, req.start_date, req.end_date)
        # TODO: goi colinker_bot de chinh allotment (lam o buoc sau)


if __name__ == "__main__":
    main()