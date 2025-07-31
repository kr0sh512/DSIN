import json
from typing import List, Tuple
import yagmail
from core.auth import GoogleAuth
from core.sheet_tools import SheetWrapper
from core.config import Config


def load_emails(sheet: SheetWrapper, column_name: str) -> List[Tuple[int, str]]:
    df = sheet.get_dataframe()
    if column_name not in df.columns:
        raise ValueError(f"Колонка '{column_name}' не найдена в таблице.")
    emails = df[column_name].fillna("").tolist()
    return [(i + 2, email) for i, email in enumerate(emails)]  # +2: заголовок + 0-index


def send_emails(email_data: List[Tuple[int, str]], subject: str, body: str,
                sent_emails_path: str, invalid_rows_path: str):
    yag = yagmail.SMTP(Config.EMAIL_ADDRESS, Config.EMAIL_KEY, host=Config.EMAIL_HOST, port=Config.EMAIL_PORT)
    sent_emails = []
    invalid_rows = []

    for row_number, email in email_data:
        if '@' in email:
            yag.send(to=email, subject=subject, contents=body)
            sent_emails.append(email)
            print(f"[✔] Письмо отправлено на {email} (строка {row_number})")
        else:
            invalid_rows.append(row_number)
            print(f"[✘] Неверный email в строке {row_number}: {email}")

    with open(sent_emails_path, "w") as f:
        json.dump(sent_emails, f)
    with open(invalid_rows_path, "w") as f:
        json.dump(invalid_rows, f)


def run():
    """Точка входа для CLI"""
    # Загрузка шаблона письма из внешнего JSON
    with open("email_template.json", "r", encoding="utf-8") as f:
        template = json.load(f)
    subject = template.get("subject", "Без темы")
    body = template.get("body", "")

    # Загрузка email-колонки из Google Sheets
    sheet = SheetWrapper(Config.BASE_DSIN_CMC)
    email_column = "Почта"  # настрой по нужному заголовку
    emails = load_emails(sheet, email_column)

    # Отправка
    send_emails(
        email_data=emails,
        subject=subject,
        body=body,
        sent_emails_path="sent_emails.json",
        invalid_rows_path="invalid_rows.json"
    )
