# CS2 Helper Bot 🎮

Telegram-бот для гравців CS2. Розкиди гранат, рекомендації закупу, збереження CFG.

## Функції

- 🗺 Розкиди (smokes, flashes, molotovs) для 7 карт: Mirage, Inferno, Dust2, Nuke, Anubis, Ancient, Vertigo
- 📍 Навігація по позиціях і варіантах
- 💰 Рекомендації закупу залежно від ситуації і грошей
- 🎮 Збереження особистого CFG (sens, FOV, viewmodel та ін.)
- 🌐 Підтримка UA / EN

## Встановлення

### 1. Клонуй репозиторій

```bash
git clone https://github.com/YOUR_USERNAME/cs2-helper-bot.git
cd cs2-helper-bot
```

### 2. Встанови залежності

```bash
pip install -r requirements.txt
```

### 3. Налаштуй `.env`

Скопіюй `.env.example` в `.env` і встав токен бота:

```bash
cp .env.example .env
```

```env
BOT_TOKEN=your_telegram_bot_token_here
```

Токен отримати у [@BotFather](https://t.me/BotFather).

### 4. Запусти

```bash
python cs2_main.py
```

## Структура

```
cs2-helper-bot/
├── cs2_main.py       # Основний файл бота
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Дані розкидів

Розкиди взяті з [csnades.app](https://csnades.app). Фото підтягуються з їхнього CDN.

## Ліцензія

MIT
