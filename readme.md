# Парсер мероприятий из Telegram и VK

## 📝 О проекте

Парсер собирает актуальные мероприятия из заданных Telegram-каналов и VK-групп, сохраняя результаты в удобном JSON-формате. Поддерживает:

- Авторизацию в Telegram через API
- Парсинг VK через официальный API
- Гибкую настройку источников
- Сохранение результатов с уникальными ID
## Установка

```bash
git clone https://github.com/MikeVolzhanin/event_parser.git
cd event_parser
pip install -r requirements.txt
```

## Настройка

1. Создайте `.env` файл:
    ```bash 
    cp .env.example .env 
    ```
2. Заполните данные.
    ```
   # Данные Telegram API (получить на my.telegram.org)
    TELEGRAM_API_ID=ваш_api_id
    TELEGRAM_API_HASH=ваш_api_hash

    # Ваш номер телефона для авторизации в Telegram
    TELEGRAM_PHONE=+79991234567

    # Токен VK API (инструкция по получению: vk.com/dev/authcode_flow_user) || можно через vk apps получить
    VK_TOKEN=ваш_vk_token
   ```
3. Запуск
    ```bash
   python main.py
   ```