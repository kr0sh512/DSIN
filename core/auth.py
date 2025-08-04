# авторизация в Google API

# Пример использования:
'''
from core.auth import GoogleAuth

auth = GoogleAuth()
gc = auth.get_gspread_client()
sheet = gc.open_by_key("SOME_SPREADSHEET_ID")
'''

import gspread
import pygsheets
from googleapiclient.discovery import build
from google.oauth2 import service_account
from core.config import Config
from core.utils import retry_until_success


class GoogleAuth:
    def __init__(self):
        self._credentials = service_account.Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS_PATH,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/documents",
            ]
        )

        # Инициализация клиентов с защитой от сбоев
        self.gc_gspread = retry_until_success(gspread.authorize, self._credentials)
        self.gc_pygsheets = retry_until_success(pygsheets.authorize, service_file=Config.GOOGLE_CREDENTIALS_PATH)
        self.drive_service = retry_until_success(build, "drive", "v3", credentials=self._credentials)
        self.sheets_service = retry_until_success(build, "sheets", "v4", credentials=self._credentials)
        self.docs_service = retry_until_success(build, "docs", "v1", credentials=self._credentials)

    def get_gspread_client(self):
        return self.gc_gspread

    def get_pygsheets_client(self):
        return self.gc_pygsheets

    def get_drive_service(self):
        return self.drive_service

    def get_sheets_service(self):
        return self.sheets_service

    def get_docs_service(self):
        return self.docs_service
