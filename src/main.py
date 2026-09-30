from sheets_client import connect, get_ready_rows


def main():
    ws = connect()
    rows = get_ready_rows(ws)
    print(f"Found {len(rows)} row(s) ready to process:")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()