import os
import json
from telebot import TeleBot, types
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import requests
from io import BytesIO

TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не установлена!")

bot = TeleBot(TOKEN)

USERS_FILE = "users.json"

# --------------------- Работа с пользователями ---------------------
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

users = load_json(USERS_FILE)

# --------------------- Команды ---------------------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
        "Привет! 🦈 Shark 4.1 — бот для генерации презентаций с картинками и описаниями.\n"
        "Используй /generate чтобы создать презентацию.\n"
        "Список команд: /help")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    chat_id = message.chat.id
    help_text = (
        "/start - приветствие\n"
        "/generate - создать презентацию\n"
        "/help - список команд"
    )
    bot.send_message(chat_id, help_text)

# --------------------- Генерация презентации ---------------------
@bot.message_handler(commands=['generate'])
def generate(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Напиши тему презентации (например 'Космос').")
    bot.register_next_step_handler(message, ask_slides)

def ask_slides(message):
    chat_id = message.chat.id
    topic = message.text.strip()
    if not topic:
        bot.send_message(chat_id, "Ошибка: введи тему презентации.")
        return
    users[chat_id] = {"topic": topic}
    save_json(USERS_FILE, users)

    # Кнопки с количеством слайдов
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    buttons = [types.InlineKeyboardButton(str(i), callback_data=f"slides_{i}") for i in range(1, 11)]
    keyboard.add(*buttons)
    bot.send_message(chat_id, "Выбери количество слайдов (1-10):", reply_markup=keyboard)

# --------------------- Обработка выбора слайдов ---------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("slides_"))
def slides_chosen(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    slide_count = int(call.data.replace("slides_", ""))
    users[chat_id]["slides"] = slide_count
    save_json(USERS_FILE, users)

    # Кнопки выбора стиля
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Dark", callback_data="style_dark"))
    keyboard.add(types.InlineKeyboardButton("Light", callback_data="style_light"))
    keyboard.add(types.InlineKeyboardButton("Minimal", callback_data="style_minimal"))
    keyboard.add(types.InlineKeyboardButton("Cyberpunk", callback_data="style_cyberpunk"))
    bot.send_message(chat_id, "Выбери стиль презентации:", reply_markup=keyboard)

# --------------------- Генерация PPTX с картинками и описанием ---------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("style_"))
def style_chosen(call):
    bot.answer_callback_query(call.id, text="Стиль выбран!")
    chat_id = call.message.chat.id
    style = call.data.replace("style_", "")
    users[chat_id]["style"] = style
    save_json(USERS_FILE, users)

    topic = users[chat_id]["topic"]
    slide_count = users[chat_id]["slides"]

    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # Цвета по стилю
    if style == "dark":
        bg_color = RGBColor(20, 20, 20)
        font_color = RGBColor(255, 255, 255)
    elif style == "light":
        bg_color = RGBColor(255, 255, 255)
        font_color = RGBColor(0, 0, 0)
    elif style == "minimal":
        bg_color = RGBColor(240, 240, 240)
        font_color = RGBColor(30, 30, 30)
    else:  # cyberpunk
        bg_color = RGBColor(0, 0, 0)
        font_color = RGBColor(255, 0, 255)

    # Контент с текстом и картинками
    content_examples = [
        ("Луна", "Луна — это естественный спутник Земли.", "https://upload.wikimedia.org/wikipedia/commons/9/99/Moon.jpg"),
        ("Солнце", "Солнце — это звезда, вокруг которой вращается Земля.", "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sun_white.jpg"),
        ("Марс", "Марс — четвёртая планета от Солнца.", "https://upload.wikimedia.org/wikipedia/commons/0/02/OSIRIS_Mars_true_color.jpg"),
        ("Космонавт", "Космонавт — человек, который путешествует в космос.", "https://upload.wikimedia.org/wikipedia/commons/d/d3/Astronaut-EVA.jpg"),
        ("Телескоп", "Телескоп позволяет наблюдать далекие объекты во Вселенной.", "https://upload.wikimedia.org/wikipedia/commons/e/ef/HST-SM4.jpeg")
    ]

    for i in range(slide_count):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        title, desc, img_url = content_examples[i % len(content_examples)]

        # Прямоугольник под текст
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1), Inches(7), Inches(4))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        text_frame = shape.text_frame
        text_frame.text = title
        p = text_frame.add_paragraph()
        p.text = desc
        p.font.size = Pt(24)
        p.font.color.rgb = font_color

        # Добавим изображение с таймаутом
        try:
            response = requests.get(img_url, timeout=5)
            response.raise_for_status()
            img_stream = BytesIO(response.content)
            slide.shapes.add_picture(img_stream, Inches(8), Inches(1), width=Inches(7), height=Inches(4))
        except Exception as e:
            print(f"Ошибка загрузки картинки: {e}")

    os.makedirs("presentations", exist_ok=True)
    output_path = f"presentations/{chat_id}_{topic}.pptx"
    prs.save(output_path)

    bot.send_message(chat_id, f"Готово! Презентация создана: {topic}.pptx")
    with open(output_path, "rb") as f:
        bot.send_document(chat_id, f)

# --------------------- Запуск бота безопасно ---------------------
print("Shark 4.1 бот запущен...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
