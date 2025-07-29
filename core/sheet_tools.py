# Файлик для упрощения работы с гугл таблицами с помощью pandas

import pandas as pd
from core.auth import GoogleAuth


class SheetWrapper:
    #инициализация и получение доступа к таблице
    def __init__(self, spreadsheet_id: str, worksheet_index: int = 0):
        self.auth = GoogleAuth()
        self.gc = self.auth.get_gspread_client()
        self.sheet = self.gc.open_by_key(spreadsheet_id).get_worksheet(worksheet_index)

    #считывание таблицы
    def get_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.sheet.get_all_records())

    #обновляем содержимое листа (удаляем старое и вносим все с нуля)
    def update_from_dataframe(self, df: pd.DataFrame):
        self.sheet.clear()
        self.sheet.update([df.columns.values.tolist()] + df.values.tolist())

    #поиск строки по значению
    def find_rows_by_value(self, column_name: str, value) -> pd.DataFrame:
        df = self.get_dataframe()
        return df[df[column_name] == value]

    #очистка листа (а вдруг придется заметать следы)
    def clear(self):
        self.sheet.clear()
