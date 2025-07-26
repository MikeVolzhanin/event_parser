import re
from dateparser import parse as parse_date

def extract_event_info(text: str) -> dict:
    # Название: первая строка или что-то "событийное"
    lines = text.strip().split("\n")
    first_line = lines[0].strip()
    event_name = first_line if len(first_line) < 100 else first_line[:100]

    # Дата: распознаём первую встречающуюся дату
    event_date = parse_date_from_text(text)

    # Локация: ищем по паттерну
    location = extract_location(text)

    # Категория (по ключевым словам)
    category = extract_category(text)

    # Кампус (по упоминаниям города)
    campus = extract_campus(text)

    # Тег: Наука, Внеучебка, Другое
    tag = extract_tag(text)

    return {
        "event_name": event_name,
        "description": text[:500],
        "event_date": event_date,
        "location": location,
        "category": category,
        "campus": campus,
        "tag": tag
    }

def parse_date_from_text(text: str):
    # Ищем дату с помощью dateparser
    date = parse_date(text, languages=["ru"])
    return date

def extract_location(text: str):
    # Ищем фразы типа улиц, корпусов, аудиторий, городов
    location_keywords = r"(Москва|Питер|Санкт-Петербург|Нижний Новгород|Пермь|ул\.|улица|корпус|ауд\.|аудитория|кампус|Холл|центр|дворец|библиотека)[^\n.,]*"
    match = re.search(location_keywords, text, flags=re.IGNORECASE)
    return match.group(0).strip() if match else None

def extract_category(text: str):
    categories = {
        "концерт": "concert",
        "лекция": "lecture",
        "выставка": "exhibition",
        "фестиваль": "festival",
        "мастер-класс": "workshop",
        "собрание": "meetup",
        "встреча": "meetup",
        "хакатон": "hackathon",
        "семинар": "seminar",
        "школа": "school",
        "форум": "forum",
        "экскурсия": "excursion"
    }

    lower_text = text.lower()
    for keyword, tag in categories.items():
        if keyword in lower_text:
            return tag
    return "other"

def extract_campus(text: str):
    if "Москва" in text or "Moscow" in text:
        return "Москва"
    elif "Санкт-Петербург" in text or "Питер" in text or "spb" in text.lower():
        return "Санкт-Петербург"
    elif "Нижний Новгород" in text or "Нижний" in text:
        return "Нижний Новгород"
    elif "Пермь" in text:
        return "Пермь"
    return None

def extract_tag(text: str):
    lower = text.lower()
    if any(x in lower for x in ["наука", "исследован", "исследования", "технолог", "лаборатория", "научн"]):
        return "Наука"
    if any(x in lower for x in ["концерт", "театр", "вечеринка", "внеучеб", "мероприятие", "встреча", "игра", "выходной"]):
        return "Внеучебка"
    return "Другое"
