import os
from dotenv import load_dotenv
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText

# Load environment variables from .env file or GitHub secrets
load_dotenv()
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
NOTIFICATION_EMAILS = os.getenv('NOTIFICATION_EMAILS').split(',')

def run_indiana_crawler():
    # Placeholder for Indiana crawler implementation
    pass

def check_new_rfps(current_rfps):
    # Placeholder to check for new RFPs against Google Sheets history
    pass

def append_rfps_to_sheet(new_rfps):
    # Append new RFPs to Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    for rfp in new_rfps:
        sheet.append_row([rfp])

def send_email_notification(new_rfps):
    # Send email notifications for new RFPs
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        for email in NOTIFICATION_EMAILS:
            msg = MIMEText(f"New RFPs:\n{new_rfps}")
            msg['Subject'] = 'New RFP Notifications'
            msg['From'] = GMAIL_ADDRESS
            msg['To'] = email
            server.sendmail(GMAIL_ADDRESS, email, msg.as_string())

def main():
    current_rfps = run_indiana_crawler()
    new_rfps = check_new_rfps(current_rfps)
    if new_rfps:
        append_rfps_to_sheet(new_rfps)
        send_email_notification(new_rfps)

if __name__ == '__main__':
    main()