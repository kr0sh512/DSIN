# Скрипт для сравнения таблиц от ОПК и нашей собственной

import pandas as pd
from core.auth import GoogleAuth
from core.sheet_tools import SheetWrapper
from core.config import Config


VMK_COLUMNS = [
    "Фамилия", "Имя", "Отчество", "Студенческий", "Профсоюзный",
    "Форма", "Направление", "Курс", "Счёт", "Адрес", "Категория", "Срок действия"
]


def find_opk_sheet_id(auth: GoogleAuth, folder_id: str, sheet_name: str = "Копия базы ОПК") -> str:
    query = f"name = '{sheet_name}' and mimeType = 'application/vnd.google-apps.spreadsheet' and '{folder_id}' in parents"
    response = auth.get_drive_service().files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = response.get("files", [])
    if not files:
        raise FileNotFoundError(f"Таблица '{sheet_name}' не найдена в папке {folder_id}")
    return files[0]["id"]


def compare_data(df_opk: pd.DataFrame, df_vmk: pd.DataFrame) -> list[str]:
    output = []
    column_map = {
        "Студ. билет": "Студенческий",
        "Профбилет": "Профсоюзный",
        "бюдж\\контр": "Форма",
        "Счет": "Счёт",
        "Справки": "Срок действия"
    }

    df_opk = df_opk.rename(columns=column_map).fillna("")
    df_vmk = df_vmk.fillna("")

    df_opk_selected = df_opk[VMK_COLUMNS]
    df_vmk_selected = df_vmk[VMK_COLUMNS]

    if len(df_opk_selected) != len(df_vmk_selected):
        output.append(f"Разное количество строк\nОПК: {len(df_opk_selected)}\nВМК: {len(df_vmk_selected)}\n")

    mismatches = []
    for idx, opk_row in df_opk_selected.iterrows():
        vmk_rows = df_vmk_selected[
            (df_vmk_selected["Фамилия"] == opk_row["Фамилия"]) &
            (df_vmk_selected["Имя"] == opk_row["Имя"])
        ]
        if vmk_rows.empty:
            output.append(f"\nСтрока {opk_row['Фамилия']} {opk_row['Имя']} отсутствует в базе ВМК.")
            continue

        vmk_row = vmk_rows.iloc[0]
        for column in VMK_COLUMNS:
            if opk_row[column] != vmk_row[column]:
                mismatches.append({
                    "Фамилия": opk_row["Фамилия"],
                    "Имя": opk_row["Имя"],
                    "Столбец": column,
                    "Значение ОПК": opk_row[column],
                    "Значение ВМК": vmk_row[column]
                })

    if mismatches:
        output.append("\n\n\nРасхождения:")
        for i, mismatch in enumerate(mismatches, start=1):
            output.append(
                f"\n{i}. {mismatch['Фамилия']} {mismatch['Имя']}, Столбец '{mismatch['Столбец']}': "
                f"ОПК('{mismatch['Значение ОПК']}') != ВМК('{mismatch['Значение ВМК']}')"
            )
    else:
        output.append("Все данные совпадают.")

    return output


def create_report(output: list[str], folder_id: str, title: str = "Отчет о различиях с базой ОПК") -> str:
    auth = GoogleAuth()
    docs = auth.get_docs_service()
    drive = auth.get_drive_service()

    document = docs.documents().create(body={"title": title}).execute()
    document_id = document["documentId"]

    requests = []
    current_index = 1
    for line in output:
        requests.append({
            "insertText": {
                "location": {"index": current_index},
                "text": line + "\n"
            }
        })

        if "Столбец" in line:
            try:
                start = line.index("Столбец") + current_index
                end = start + line[start - current_index:].index(":")
                requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": start, "endIndex": end},
                        "textStyle": {
                            "foregroundColor": {"color": {"rgbColor": {"red": 1.0}}}
                        },
                        "fields": "foregroundColor"
                    }
                })
            except ValueError:
                pass

        current_index += len(line) + 1

    docs.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
    drive.files().update(fileId=document_id, addParents=folder_id).execute()
    return f"https://docs.google.com/document/d/{document_id}"


def run():
    auth = GoogleAuth()

    vmk_sheet = SheetWrapper(Config.SPREADSHEET_ID_VMK)
    opk_sheet_id = find_opk_sheet_id(auth, Config.FOLDER_ID_OPK)
    opk_sheet = SheetWrapper(opk_sheet_id)

    df_vmk = vmk_sheet.get_dataframe()
    df_opk = opk_sheet.get_dataframe()

    output = compare_data(df_opk, df_vmk)
    report_url = create_report(output, Config.FOLDER_ID_OPK)

    print(f"Отчет создан: {report_url}")