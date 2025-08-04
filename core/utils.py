import time
from contextlib import contextmanager
import traceback

@contextmanager
def rollback_on_failure(worksheet, description: str = "таблица"):
    """
    Контекстный менеджер для защиты от частично записанных изменений в Google Таблице.
    Если внутри блока возникает ошибка — восстанавливает таблицу в исходное состояние.
    """
    try:
        original_data = retry_until_success(worksheet.get_all_values)
        yield
    except Exception as e:
        print(f"[rollback] ⚠️ Ошибка при работе с {description}: {e}")
        print("[rollback] 🔁 Откат изменений...")

        try:
            retry_until_success(worksheet.clear)
            retry_until_success(worksheet.update, [original_data[0]] + original_data[1:])
            print("[rollback] 🟡 Таблица восстановлена.")
        except Exception as rollback_error:
            print("[rollback] ❌ Не удалось восстановить таблицу:")
            traceback.print_exc()
        raise  # пробрасываем исходную ошибку дальше


def retry_until_success(func, *args, **kwargs):
    # Выполняет функцию, пока не завершится без исключения.
    delay = 1
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[retry] Ошибка: {e}. Повтор через {delay} сек...")
            time.sleep(delay)
            delay = min(delay * 2, 60)  # Экспоненциальный рост паузы (до 60 сек)