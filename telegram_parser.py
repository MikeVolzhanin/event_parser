import hashlib
import json
import os
import asyncio
from typing import List, Dict

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import SessionPasswordNeededError

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE

# Каналы Telegram (без @)
CHANNELS = [
    "HSEafisha", "hse_live", "studsupport_hse", "hsebusinessclub",
    "hse_science", "studsciencehse", "nbhse", "hse_library", "scilaunch",
    "deadlinewasyesterdayy", "CSiBP", "dataculturehse", "spbhse",
    "hsealumnichannel", "hsecareer"
]

def generate_id(text_or_url: str) -> str:
    return hashlib.md5(text_or_url.encode("utf-8")).hexdigest()

async def fetch_messages(client: TelegramClient, channel: str, target_valid_events: int = 50) -> List:
    messages_data = []
    valid_count = 0
    offset_id = 0

    try:
        entity = await client.get_entity(channel)
        while valid_count < target_valid_events:
            history = await client(GetHistoryRequest(
                peer=entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0
            ))

            if not history.messages:
                break

            for message in history.messages:
                offset_id = message.id
                if not message.message:
                    continue

                messages_data.append((channel, message))
                valid_count += 1

                if valid_count >= target_valid_events:
                    break

    except Exception as e:
        print(f"❌ Ошибка при получении сообщений из @{channel}: {e}")

    return messages_data

async def parse_telegram(limit: int = 50) -> List[Dict]:
    """Основная функция парсера Telegram"""
    client = TelegramClient("anon", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(TELEGRAM_PHONE)
        try:
            code = input("Введите код из Telegram: ")
            await client.sign_in(phone=TELEGRAM_PHONE, code=code)
        except SessionPasswordNeededError:
            password = input("Введите двухфакторный пароль: ")
            await client.sign_in(password=password)

    all_events = []

    for channel in CHANNELS:
        print(f"📥 Парсим @{channel}...")
        messages = await fetch_messages(client, channel, target_valid_events=limit)

        for chan, message in messages:
            text = message.message.strip()
            post_url = f"https://t.me/{chan}/{message.id}"

            event = {
                "event_id": generate_id(post_url),
                "source": "telegram",
                "channel_name": f"@{chan}",
                "post_date": message.date.isoformat(),
                "url": post_url,
                "raw_text": text
            }
            all_events.append(event)

    os.makedirs("data", exist_ok=True)
    with open("data/telegram_events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Telegram: собрано {len(all_events)} мероприятий.")

    await client.disconnect()
    return all_events

def run_telegram_parser(limit: int = 50):
    """Синхронная обёртка для запуска асинхронного парсера"""
    return asyncio.run(parse_telegram(limit))

if __name__ == "__main__":
    limit = int(input("🔢 Сколько постов парсить из каждого канала? "))
    results = run_telegram_parser(limit)
    print(f"\n✅ Telegram: собрано {len(results)} мероприятий.")
