from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import SessionPasswordNeededError
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
from extractors import extract_event_info
from models import Event
import hashlib
import json
from datetime import datetime
import os

# Каналы Telegram (без @)
CHANNELS = [
    "HSEafisha", "hse_live", "studsupport_hse", "hsebusinessclub",
    "hse_science", "studsciencehse", "nbhse", "hse_library", "scilaunch", "deadlinewasyesterdayy",
    "CSiBP", "dataculturehse", "spbhse", "hsealumnichannel", "hsecareer"
]

def generate_id(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

async def fetch_messages(client, channel, limit=50):
    messages_data = []
    try:
        entity = await client.get_entity(channel)
        offset_id = 0

        while True:
            history = await client(GetHistoryRequest(
                peer=entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break

            for message in history.messages:
                if not message.message:
                    continue
                messages_data.append((channel, message))

            offset_id = history.messages[-1].id
            break  # только первая порция сообщений

    except Exception as e:
        print(f"❌ Ошибка при получении сообщений из @{channel}: {e}")
    return messages_data

async def main():
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
        messages = await fetch_messages(client, channel)

        for chan, message in messages:
            text = message.message.strip()
            event_info = extract_event_info(text)

            event = Event(
                event_id=generate_id(text),
                source="telegram",
                channel_name=f"@{chan}",
                post_date=message.date,
                event_name=event_info.get("event_name", ""),
                description=event_info.get("description", ""),
                event_date=event_info.get("event_date"),
                location=event_info.get("location"),
                campus=event_info.get("campus"),
                category=event_info.get("category"),
                url=f"https://t.me/{chan}/{message.id}",
                raw_text=text,
                tag=event_info.get("tag", "")
            )

            # Преобразуем datetime → ISO строку
            event_dict = event.dict()
            for k in ["post_date", "event_date"]:
                if isinstance(event_dict.get(k), datetime):
                    event_dict[k] = event_dict[k].isoformat()
            all_events.append(event_dict)

    os.makedirs("data", exist_ok=True)
    with open("data/telegram_events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Telegram: собрано {len(all_events)} мероприятий.")
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
