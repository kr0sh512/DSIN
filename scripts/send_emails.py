import json
from typing import List, Tuple
import yagmail
from core.auth import GoogleAuth
from core.sheet_tools import SheetWrapper
from core.config import Config
from core.utils import retry_until_success  # 🔁 добавлен retry


def load_emails(sheet: SheetWrapper, column_name: str) -> List[Tuple[int, str]]:
    df = retry_until_success(sheet.get_dataframe)
    if column_name not in df.columns:
        raise ValueError(f"Колонка '{column_name}' не найдена в таблице.")
    emails = df[column_name].fillna("").tolist()
    return [(i + 2, email) for i, email in enumerate(emails)]  # +2: заголовок + 0-index


def send_emails(email_data: List[Tuple[int, str]], subject: str, body: str,
                sent_emails_path: str, invalid_rows_path: str):
    yag = yagmail.SMTP(
        user=Config.EMAIL_ADDRESS,
        password=Config.EMAIL_KEY,
        host=Config.EMAIL_HOST,
        port=int(Config.EMAIL_PORT)
    )
    sent_emails = []
    invalid_rows = []

    for row_number, email in email_data:
        if '@' not in email:
            invalid_rows.append(row_number)
            print(f"[✘] Неверный email в строке {row_number}: {email}")
            continue

        try:
            retry_until_success(yag.send, to=email, subject=subject, contents=body)
            sent_emails.append(email)
            print(f"[✔] Письмо отправлено на {email} (строка {row_number})")
        except Exception as e:
            print(f"[⚠] Ошибка отправки на {email} (строка {row_number}): {e}")
            invalid_rows.append(row_number)

    with open(sent_emails_path, "w", encoding="utf-8") as f:
        json.dump(sent_emails, f, ensure_ascii=False, indent=2)
    with open(invalid_rows_path, "w", encoding="utf-8") as f:
        json.dump(invalid_rows, f, ensure_ascii=False, indent=2)


def run():
    """Точка входа для CLI"""
    try:
        with open("email_template.json", "r", encoding="utf-8") as f:
            template = json.load(f)
    except FileNotFoundError:
        print("[✘] Не найден файл email_template.json.")
        return

    subject = template.get("subject", "Без темы")
    body = template.get("body", "")

    sheet = SheetWrapper(Config.BASE_DSIN_CMC)
    email_column = "Почта"  # настрой по нужному заголовку
    emails = load_emails(sheet, email_column)

    send_emails(
        email_data=emails,
        subject=subject,
        body=body,
        sent_emails_path="sent_emails.json",
        invalid_rows_path="invalid_rows.json"
    )
