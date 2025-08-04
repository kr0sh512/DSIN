from core.auth import GoogleAuth
from core.config import Config
from core.utils import retry_until_success, rollback_on_failure  # 🛡️ добавлен откат при ошибке
from gspread_formatting import set_column_width
import gspread


def format_course_sheet(worksheet: gspread.Worksheet, rows_num: int):
    """Применяет форматирование: заголовки, выпадающие списки, чередование цветов."""
    retry_until_success(worksheet.update_cell, 1, 7, 'Статус')
    retry_until_success(worksheet.update_cell, 1, 8, 'Комментарий')

    set_column_width(worksheet, 'A:G', 120)

    # Выпадающий список со статусами
    data_validation_rule = {
        "condition": {
            "type": "ONE_OF_LIST",
            "values": [
                {"userEnteredValue": "закрылся"},
                {"userEnteredValue": "задолж."},
                {"userEnteredValue": "академ."},
                {"userEnteredValue": "отчислен"}
            ]
        },
        "showCustomUi": True,
        "strict": True
    }

    request = {
        "setDataValidation": {
            "range": {
                "sheetId": worksheet.id,
                "startRowIndex": 1,
                "endRowIndex": rows_num + 1,
                "startColumnIndex": 6,
                "endColumnIndex": 7
            },
            "rule": data_validation_rule
        }
    }

    retry_until_success(worksheet.spreadsheet.batch_update, {"requests": [request]})

    # Чередование цветов
    start_row = 1
    end_row = rows_num + 1
    requests = []

    for row in range(start_row, end_row + 1):
        if row % 2 == 0:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": 0,
                        "endColumnIndex": worksheet.col_count
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 1.0,
                                "green": 1.0,
                                "blue": 0.9
                            }
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })

    if requests:
        retry_until_success(worksheet.spreadsheet.batch_update, {"requests": requests})


def run():
    """Точка входа для CLI"""
    auth = GoogleAuth()
    gc = auth.get_gspread_client()

    spreadsheet = retry_until_success(gc.open_by_key, Config.SPREADSHEET_ID_COURSE_HEADS)
    worksheet = spreadsheet.sheet1
    rows_num = len(retry_until_success(worksheet.get_all_values)) - 1

    with rollback_on_failure(worksheet, description="таблица начальников курсов"):
        format_course_sheet(worksheet, rows_num)

    print("Форматирование таблицы начальников курсов завершено.")
