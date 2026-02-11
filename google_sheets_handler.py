import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsHandler:
    def __init__(self, creds_json):
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'])
        self.client = gspread.authorize(self.creds)

    def open_sheet(self, sheet_name):
        return self.client.open(sheet_name)

    def get_worksheet(self, sheet_name, worksheet_name):
        sheet = self.open_sheet(sheet_name)
        return sheet.worksheet(worksheet_name)

    def read_data(self, sheet_name, worksheet_name):
        worksheet = self.get_worksheet(sheet_name, worksheet_name)
        return worksheet.get_all_records()

    def append_data(self, sheet_name, worksheet_name, data):
        worksheet = self.get_worksheet(sheet_name, worksheet_name)
        worksheet.append_row(data)