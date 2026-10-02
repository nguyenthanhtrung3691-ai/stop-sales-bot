# Stop Sales Bot

Semi-automation bot that reads Stop Sale requests from **Google Sheets** and closes the matching room types on **Colinker** using **Playwright** (Python).

![Project Architecture](architecture.png)

## Status

- Working: reading the Sheet, validating rows, writing results back, logging.
- In testing: the Colinker steps (hotel search, room selection, date range). Always run with `--no-save` first and check the screenshots before saving for real.

## How it works

1. The team enters a request in Google Sheets (columns below) and sets `Status` to `Ready to Process`.
2. The operator runs the bot on their machine.
3. The bot validates each row, opens Colinker with a saved login session, finds the hotel by ID, selects the room type, and sets the date range and the "closed" status.
4. The bot writes `Success` or `Failed: <reason>` back to the Sheet and saves a screenshot when a row fails.

## Sheet format

| Hotel ID | Room Type | Start Date | End Date | Status |
|----------|-----------|------------|----------|--------|
| 133574732 | Premium Double Room | 10/12/2026 | 12/12/2026 | Ready to Process |

- Dates use `dd/mm/yyyy`.
- `Room Type` must match the room name on Colinker exactly.
- `Status`: `Ready to Process` -> `Success` or `Failed: <reason>`.

## Setup (Windows, PowerShell)

```powershell
git clone https://github.com/nguyenthanhtrung3691-ai/stop-sales-bot.git
cd stop-sales-bot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

1. **Google access:** create a Google Cloud project, enable *Google Sheets API* and *Google Drive API*, create a Service Account, download its JSON key as `credentials/service-account.json`, and share the Sheet with the Service Account email (Editor).
2. **Config:** copy `.env.example` to `.env` and fill in your Sheet ID, worksheet name and Colinker URL.
3. **Colinker login (OTP):** run `python login_once.py`, log in manually (including the OTP), wait until the Colinker menu appears, then press Enter. The session is saved to `credentials/colinker_state.json`. Repeat when the session expires.

## Usage

```powershell
python src\main.py --dry-run    # read and validate the Sheet only
python src\main.py --no-save    # go through Colinker without clicking Save (test mode)
python src\main.py              # real run: saves changes on Colinker
```

## Project structure

```text
stop-sales-bot/
├── src/
│   ├── main.py              # entry point
│   ├── sheets_client.py     # read queued rows, write back status
│   ├── colinker_bot.py      # Playwright steps on Colinker
│   ├── models.py            # row validation
│   └── logger.py            # logging
├── login_once.py            # save the Colinker login session
├── requirements.txt
├── .env.example
└── README.md
```

## Security

- Never commit `.env`, `credentials/`, `logs/` or `screenshots/` (already in `.gitignore`).
- `credentials/colinker_state.json` is a login session: treat it like a password.
- Use a dedicated bot account on Colinker when possible.

## Known limitations

- The Colinker session expires and must be refreshed manually with `login_once.py`.
- Playwright selectors may need updating when the Colinker UI changes.
- Requests are still copied into the Sheet manually.
