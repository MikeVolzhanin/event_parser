import os

import requests
import hashlib
import json
from datetime import datetime
from typing import List, Dict
from config import VK_TOKEN

VK_API_VERSION = "5.131"
VK_GROUPS = [
    "nbhse",
    "ovvr_hsespb",
    "hsebusinessclub"
]

def generate_id(text_or_url: str) -> str:
    return hashlib.md5(text_or_url.encode("utf-8")).hexdigest()

def get_wall_posts(domain: str, offset: int = 0, count: int = 100) -> List[Dict]:
    url = "https://api.vk.com/method/wall.get"
    params = {
        "access_token": VK_TOKEN,
        "v": VK_API_VERSION,
        "domain": domain,
        "count": count,
        "offset": offset
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print(f"❌ Ошибка VK API ({domain}): {data['error']['error_msg']}")
            return []

        return data["response"]["items"]

    except Exception as e:
        print(f"❌ Ошибка при запросе к VK API ({domain}): {str(e)}")
        return []

def parse_vk_group(group: str, limit: int = 50) -> List[Dict]:
    """Парсит указанную группу VK"""
    valid_events = []
    offset = 0

    while len(valid_events) < limit:
        posts = get_wall_posts(group, offset=offset)
        if not posts:
            break

        for post in posts:
            text = post.get("text", "").strip()
            if not text:
                continue

            post_url = f"https://vk.com/{group}?w=wall{post['owner_id']}_{post['id']}"
            event = {
                "event_id": generate_id(post_url),
                "source": "vk",
                "channel_name": group,
                "post_date": datetime.fromtimestamp(post["date"]).isoformat(),
                "url": post_url,
                "raw_text": text
            }
            valid_events.append(event)

            if len(valid_events) >= limit:
                break

        offset += 100

    return valid_events

def run_vk_parser(limit: int = 50) -> List[Dict]:
    """Основная функция для запуска парсера VK"""
    all_events = []

    for group in VK_GROUPS:
        print(f"📥 Парсим группу: {group}...")
        events = parse_vk_group(group, limit)
        all_events.extend(events)

    # Сохраняем результат
    os.makedirs("data", exist_ok=True)
    with open("data/vk_events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print(f"\n✅ VK: собрано {len(all_events)} мероприятий.")
    return all_events

if __name__ == "__main__":
    limit = int(input("🔢 Сколько мероприятий парсить из каждой группы? "))
    run_vk_parser(limit)