import telebot
import os
import json
import random

# Токен берём из Environment Variable, менять в коде не нужно
TOKEN = os.environ["TOKEN"]
bot = telebot.TeleBot(TOKEN)

# Файлы для хранения игроков и лобби
PLAYERS_FILE = "players.json"
LOBBIES_FILE = "lobbies.json"

# Загрузка данных
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

players = load_json(PLAYERS_FILE)
lobbies = load_json(LOBBIES_FILE)

# --- Команды бота ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Это Standoff-бот с автоматическим лобби и голосовым чатом 🚀\n\nИспользуй /register для регистрации.")

# Регистрация
@bot.message_handler(commands=['register'])
def register(message):
    chat_id = message.chat.id
    for p in players:
        if p["chat_id"] == chat_id:
            bot.send_message(chat_id, "Ты уже зарегистрирован!")
            return
    players.append({
        "chat_id": chat_id,
        "nick": None,
        "rank": None,
        "game_id": None,
        "hours": None
    })
    save_json(PLAYERS_FILE, players)
    bot.send_message(chat_id, "Ты зарегистрирован! Используй /setprofile чтобы добавить ник, звание и игровые данные.")

# Настройка профиля
@bot.message_handler(commands=['setprofile'])
def setprofile(message):
    chat_id = message.chat.id
    msg = "Отправь данные в формате:\nник;звание;игровой_id;часы\nПример: Player1;Gold;123456;120"
    bot.send_message(chat_id, msg)
    bot.register_next_step_handler(message, save_profile)

def save_profile(message):
    chat_id = message.chat.id
    text = message.text
    try:
        nick, rank, game_id, hours = text.split(";")
        hours = int(hours)
        if hours < 100:
            bot.send_message(chat_id, "На аккаунте должно быть минимум 100 часов, регистрация невозможна.")
            return
        for p in players:
            if p["chat_id"] == chat_id:
                p["nick"] = nick
                p["rank"] = rank
                p["game_id"] = game_id
                p["hours"] = hours
        save_json(PLAYERS_FILE, players)
        bot.send_message(chat_id, f"Профиль обновлён!\nНик: {nick}\nЗвание: {rank}\nЧасы: {hours}")
    except:
        bot.send_message(chat_id, "Ошибка формата. Попробуй снова /setprofile")

# Найти лобби
@bot.message_handler(commands=['find_lobby'])
def find_lobby(message):
    chat_id = message.chat.id
    player = next((p for p in players if p["chat_id"] == chat_id), None)
    if not player or not player["nick"]:
        bot.send_message(chat_id, "Сначала настрой профиль через /setprofile")
        return

    # Сначала ищем лобби для ММ (5 игроков)
    lobby = next((l for l in lobbies if l["mode"]=="MM" and len(l["players"])<5), None)
    if not lobby:
        # Создаём новое лобби
        lobby = {"id": random.randint(1000,9999), "mode":"MM", "players":[chat_id]}
        lobbies.append(lobby)
        save_json(LOBBIES_FILE, lobbies)
        bot.send_message(chat_id, f"Создано новое лобби {lobby['id']} для ММ. Ждём остальных игроков...")
    else:
        lobby["players"].append(chat_id)
        save_json(LOBBIES_FILE, lobbies)
        bot.send_message(chat_id, f"Ты добавлен в лобби {lobby['id']} для ММ!")

    # Проверка на полный лобби
    if len(lobby["players"]) == 5:
        players_mentions = [f"<a href='tg://user?id={p}'>игрок</a>" for p in lobby["players"]]
        text = "Лобби заполнено! Можете начать игру!\nИгроки: " + ", ".join(players_mentions)
        for p in lobby["players"]:
            bot.send_message(p, text, parse_mode="HTML")
            # Генерируем ссылку на голосовой чат Telegram
            bot.send_message(p, f"Ссылка на голосовой чат: https://t.me/joinchat/XXXXXXX")  # тут можно будет вставить динамическую ссылку

# --- Запуск бота ---
print("Бот запущен...")
bot.infinity_polling()
