import os
import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import gspread
import smtplib
from email.mime.text import MIMEText
from crawlers.indiana_crawler import IndianaCrawler

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_JSON_PATH = os.getenv("CREDENTIALS_JSON", "credentials.json")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # should be an app password
NOTIFICATION_EMAILS = [e.strip() for e in os.getenv("NOTIFICATION_EMAILS", "").split(",") if e.strip()]

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def gsheets_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_JSON_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_existing_event_ids(sheet):
    try:
        records = sheet.get_all_records()
        ids = set()
        for r in records:
            # Accept several possible column names
            for key in ("event_id", "Event ID", "EventId", "id"):
                if key in r and r[key]:
                    ids.add(str(r[key]).strip())
        return ids
    except Exception:
        # fallback: read first column values
        try:
            vals = sheet.col_values(2)  # assume event_id is column 2
            return set(vals[1:])  # skip header
        except Exception:
            return set()

def append_rfps(sheet, items):
    # Ensure header exists
    header = ["title", "event_id", "agency", "description", "due_date", "url", "contact_email", "discovered_at"]
    try:
        current_header = sheet.row_values(1)
        if not current_header or len(current_header) < 3:
            sheet.insert_row(header, 1)
    except Exception:
        pass

    for it in items:
        row = [
            it.get("title", ""),
            it.get("event_id", ""),
            it.get("agency", ""),
            it.get("description", ""),
            it.get("due_date", ""),
            it.get("url", ""),
            it.get("contact_email", ""),
            datetime.datetime.utcnow().isoformat(),
        ]
        sheet.append_row(row)

def send_digest_email(new_items):
    if not GMAIL_ADDRESS or not GMAIL_PASSWORD or not NOTIFICATION_EMAILS:
        print("Email settings not configured; skipping email.")
        return
    body_lines = []
    for it in new_items:
        body_lines.append(f"- {it.get('title')} ({it.get('event_id')})")
        body_lines.append(f"  URL: {it.get('url')}")
        if it.get("due_date"):
            body_lines.append(f"  Due: {it.get('due_date')}")
        if it.get("contact_email"):
            body_lines.append(f"  Contact: {it.get('contact_email')}")
        body_lines.append("")
    body = "New RFPs discovered:\n\n" + "\n".join(body_lines)

    msg = MIMEText(body)
    msg["Subject"] = f"[RFP-Aggregator] {len(new_items)} new RFP(s) found"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = ", ".join(NOTIFICATION_EMAILS)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, NOTIFICATION_EMAILS, msg.as_string())

def main():
    print("Starting Indiana crawler...")
    crawler = IndianaCrawler()
    items = crawler.run()
    if not items:
        print("No items found.")
        return

    print(f"Found {len(items)} items; connecting to Google Sheets...")
    client = gsheets_client()
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    existing_ids = get_existing_event_ids(sheet)
    new_items = []
    for it in items:
        eid = it.get("event_id") or it.get("url")
        if not eid or str(eid).strip() not in existing_ids:
            new_items.append(it)

    if new_items:
        print(f"{len(new_items)} new items — appending to sheet and sending notifications.")
        append_rfps(sheet, new_items)
        send_digest_email(new_items)
    else:
        print("No new items to add.")

if __name__ == "__main__":
    main()
