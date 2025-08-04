"""
main_cli.py — единая точка запуска скриптов из ./scripts

Примеры:
    python main_cli.py list
    python main_cli.py bases_diff
    python main_cli.py send_emails --silent
"""

import argparse
import importlib
import pkgutil
import inspect
import sys
import traceback  # для отображения ошибок
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent / "scripts"


def discover_scripts():
    """Возвращает словарь {имя_скрипта: модуль_путь_для_importlib}."""
    scripts = {}
    for module_info in pkgutil.iter_modules([str(SCRIPTS_DIR)]):
        name = module_info.name
        scripts[name] = f"scripts.{name}"
    return scripts


def load_and_run(module_name: str, forward_args: list[str]):
    """Импортирует модуль, ищет функцию run() и выполняет её."""
    try:
        mod = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        sys.exit(f"❌ Модуль {module_name} не найден: {exc}")

    if not hasattr(mod, "run") or not inspect.isfunction(mod.run):
        sys.exit(f"❌ В {module_name} нет функции run().")

    try:
        mod.run(*forward_args)
    except Exception as e:
        print(f"❌ Ошибка при выполнении {module_name}: {e}")
        traceback.print_exc()
        sys.exit(1)


def main():
    scripts = discover_scripts()

    parser = argparse.ArgumentParser(
        description="CLI-лаунчер DSIN",
        usage="python main_cli.py {list|<script>} [args]"
    )
    parser.add_argument(
        "command",
        help="list  — показать доступные скрипты; "
             "<script> — имя скрипта для запуска"
    )
    parser.add_argument("rest", nargs=argparse.REMAINDER,
                        help="аргументы, передаваемые скрипту")

    args = parser.parse_args()

    if args.command == "list":
        print("Доступные скрипты:")
        for s in sorted(scripts):
            print(f"  • {s}")
        return

    if args.command not in scripts:
        sys.exit(f"❌ Скрипт '{args.command}' не найден. "
                 "Используйте 'list' для списка.")

    load_and_run(scripts[args.command], args.rest)


if __name__ == "__main__":
    main()
