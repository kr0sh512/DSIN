# файл для безопасного извлечения переменных среды и проверки их на корректность

import os
from dotenv import load_dotenv

# Загружаем .env из корня проекта
load_dotenv()

class Config:
    # Google API
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

    # Таблицы
    SPREADSHEET_ID_VMK = os.getenv("SPREADSHEET_ID_VMK")
    FOLDER_ID_OPK = os.getenv("FOLDER_ID_OPK")

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
