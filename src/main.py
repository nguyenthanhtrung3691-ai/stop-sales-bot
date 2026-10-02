import argparse

from colinker_bot import ColinkerBot, SessionExpired
from logger import get_logger
from models import parse_request
from sheets_client import connect, get_ready_rows, write_status

log = get_logger()


def process_one(bot, ws, req, args):
    try:
        bot.process(req, save=not args.no_save)
    except Exception as e:
        shot = bot.screenshot(f"row{req.row}")
        msg = f"{type(e).__name__}: {e}".splitlines()[0][:200]
        log.error("Row %s failed: %s (anh: %s)", req.row, msg, shot)
        if not args.no_save:
            write_status(ws, req.row, "Failed", msg)
        return
    if args.no_save:
        log.info("Row %s: chay den buoc cuoi (KHONG luu)", req.row)
        bot.screenshot(f"row{req.row}_no_save")
    else:
        write_status(ws, req.row, "Success")
        log.info("Row %s: Success", req.row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Chi doc va kiem tra Sheet, khong mo Colinker")
    parser.add_argument("--no-save", action="store_true",
                        help="Thao tac tren Colinker nhung KHONG bam Save va KHONG ghi Sheet (de thu)")
    args = parser.parse_args()

    ws = connect()
    records = get_ready_rows(ws)
    log.info("Found %d row(s) ready to process", len(records))

    valid = []
    for record in records:
        try:
            valid.append(parse_request(record))
        except ValueError as e:
            log.error("Row %s invalid: %s", record["row"], e)
            if not (args.dry_run or args.no_save):
                write_status(ws, record["row"], "Failed", str(e))

    if args.dry_run:
        for req in valid:
            log.info("Row %s OK: %s | %s | %s -> %s",
                     req.row, req.hotel_id, req.room_type, req.start_date, req.end_date)
        return
    if not valid:
        return

    try:
        with ColinkerBot() as bot:
            for req in valid:
                process_one(bot, ws, req, args)
    except SessionExpired as e:
        log.error("%s", e)


if __name__ == "__main__":
    main()