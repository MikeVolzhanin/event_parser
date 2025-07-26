import requests
import hashlib
import json
from datetime import datetime
from extractors import extract_event_info
from models import Event
from config import VK_TOKEN

VK_API_VERSION = "5.131"
VK_GROUPS = [
    "nbhse",
    "ovvr_hsespb",
    "hsebusinessclub"
]


def generate_id(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def get_wall_posts(domain: str, count: int = 20):
    url = "https://api.vk.com/method/wall.get"
    params = {
        "access_token": VK_TOKEN,
        "v": VK_API_VERSION,
        "domain": domain,
        "count": count,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "error" in data:
        print(f"❌ Ошибка VK API ({domain}): {data['error']['error_msg']}")
        return []

    return data["response"]["items"]


def parse_vk():
    all_events = []

    for group in VK_GROUPS:
        posts = get_wall_posts(group)
        for post in posts:
            text = post.get("text", "").strip()
            if not text:
                continue

            event_info = extract_event_info(text)
            post_date = datetime.fromtimestamp(post["date"])

            post_url = f"https://vk.com/{group}?w=wall{post['owner_id']}_{post['id']}"

            event = Event(
                event_id=generate_id(text),
                source="vk",
                channel_name=group,
                post_date=post_date,
                event_name=event_info.get("event_name", ""),
                description=event_info.get("description", ""),
                event_date=event_info.get("event_date"),
                location=event_info.get("location"),
                campus=event_info.get("campus"),
                category=event_info.get("category"),
                url=post_url,
                raw_text=text,
                tag=event_info.get("tag", "")
            )

            event_dict = event.dict()

            # Преобразуем datetime → ISO формат
            for key in ["post_date", "event_date"]:
                if isinstance(event_dict.get(key), datetime):
                    event_dict[key] = event_dict[key].isoformat()

            all_events.append(event_dict)

    with open("data/vk_events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print(f"✅ VK: собрано {len(all_events)} мероприятий.")


if __name__ == "__main__":
    parse_vk()
