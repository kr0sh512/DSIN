# файл для безопасного извлечения переменных среды и проверки их на корректность

import os
from dotenv import load_dotenv

# Загружаем .env из корня проекта
load_dotenv()

class Config:
    # Google API
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

    # Таблицы
    BASE_DSIN_CMC = os.getenv("BASE_DSIN_CMC")
    OPK_FOLDER_ID = os.getenv("OPK_FOLDER_ID")
    SPREADSHEET_ID_COURSE_HEADS = os.getenv("SPREADSHEET_ID_COURSE_HEADS")
    FORM_RESPONSES_ID = os.getenv("FORM_RESPONSES_ID")

    # Email
    EMAIL_ADDRESS = os.getenv("EMAIL_EMAIL")
    EMAIL_KEY = os.getenv("EMAIL_KEY")
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = os.getenv("EMAIL_PORT")

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    @classmethod
    def check(cls):
        missing = [var for var in dir(cls) if var.isupper() and getattr(cls, var) is None]
        if missing:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

# Пример вызова проверки:
# Config.check()
