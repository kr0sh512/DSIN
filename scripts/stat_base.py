import pandas as pd
from core.auth import GoogleAuth
from core.sheet_tools import SheetWrapper
from core.config import Config
from datetime import datetime


def run():
    """Точка входа для CLI"""
    auth = GoogleAuth()
    drive = auth.get_drive_service()

    # 1. Чтение базы ВМК
    sheet_bdns = auth.get_gspread_client().open_by_key(Config.BASE_DSIN_CMC)
    data_budg = pd.DataFrame(sheet_bdns.get_worksheet(0).get_all_records())
    data_cont = pd.DataFrame(sheet_bdns.get_worksheet(1).get_all_records())
    data_bdns = pd.concat([data_budg, data_cont], ignore_index=True)

    data_bdns = data_bdns[["Студенческий", "Курс", "Срок действия", "Статус"]]
    data_bdns = data_bdns.rename(columns={
        "Студенческий": "Номер студенческого",
        "Срок действия": "Истечение документов",
    })
    data_bdns["Статус"] = data_bdns["Статус"].replace(
        ["", "Ок"], ["В обработке", "Все в порядке"]
    )

    # 2. Чтение ответов на форму
    sheet_answers = SheetWrapper(Config.FORM_RESPONSES_ID)
    df_form = sheet_answers.get_dataframe()
    df_form = df_form[df_form["Номер студенческого билета"] != ""]
    df_form = df_form[~df_form["Номер студенческого билета"].isin(data_bdns["Номер студенческого"])]
    df_form = df_form[["Номер студенческого билета", "Курс", "Статус"]]
    df_form = df_form.rename(columns={"Номер студенческого билета": "Номер студенческого"})
    df_form["Статус"] = df_form["Статус"].replace(
        ["Внести", "Продлить", "", "Ошибка"], ["В обработке"] * 4
    )

    # 3. Объединение
    final_df = pd.concat([data_bdns, df_form], ignore_index=True)

    # 4. Создание новой таблицы
    file_metadata = {
        "name": f"Объединённая база {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents": [Config.OPK_FOLDER_ID]
    }

    new_sheet = drive.files().create(body=file_metadata, fields="id").execute()
    new_sheet_id = new_sheet["id"]

    SheetWrapper(new_sheet_id).update_from_dataframe(final_df)

    print(f"Готово! Создана таблица: https://docs.google.com/spreadsheets/d/{new_sheet_id}")
