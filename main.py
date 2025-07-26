import json
import os
from telegram_parser import run_telegram_parser
from vk_parser import run_vk_parser


def show_menu():
    print("\n" + "=" * 40)
    print("🎛️  Меню парсера мероприятий")
    print("=" * 40)
    print("1. Парсить только Telegram")
    print("2. Парсить только VK")
    print("3. Парсить всё (Telegram + VK)")
    print("0. Выход")
    print("=" * 40)

def main():
    default_limit = 30  # Лимит постов по умолчанию

    while True:
        show_menu()
        choice = input("Выберите действие (0-3): ").strip()

        if choice == "0":
            print("Завершение работы...")
            break

        elif choice == "1":
            print("\n🔍 Запуск парсера Telegram")
            limit = int(input(f"Лимит постов (по умолчанию {default_limit}): ") or default_limit)
            run_telegram_parser(limit)

        elif choice == "2":
            print("\n🔍 Запуск парсера VK")
            limit = int(input(f"Лимит постов (по умолчанию {default_limit}): ") or default_limit)
            run_vk_parser(limit)

        elif choice == "3":
            print("\n🔍 Запуск всех парсеров")
            limit = int(input(f"Лимит постов (по умолчанию {default_limit}): ") or default_limit)

            print("\nПарсим Telegram...")
            run_telegram_parser(limit)

            print("\nПарсим VK...")
            run_vk_parser(limit)

        else:
            print("❌ Неверный ввод, попробуйте снова")

if __name__ == "__main__":
    main()