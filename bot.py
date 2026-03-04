import telebot
import os
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from PIL import Image

TOKEN = os.environ["TOKEN"]
bot = telebot.TeleBot(TOKEN)

# Файлы для хранения пользователей
USERS_FILE = "users.json"

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

# --- Telegram команды ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет! 🦈 Я Shark — бот для генерации презентаций.\n"
                     "Используй /generate чтобы создать презентацию.")

# Генерация презентации
@bot.message_handler(commands=['generate'])
def generate(message):
    chat_id = message.chat.id
    msg = ("Опиши презентацию в формате:\n"
           "тема; стиль; количество слайдов\n\n"
           "Пример: Космос;Dark;5")
    bot.send_message(chat_id, msg)
    bot.register_next_step_handler(message, create_presentation)

# Создание презентации
def create_presentation(message):
    chat_id = message.chat.id
    try:
        topic, style, slide_count = message.text.split(";")
        slide_count = int(slide_count)
    except:
        bot.send_message(chat_id, "Ошибка формата. Попробуй снова /generate")
        return

    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # Цвета по стилю
    if style.lower() == "dark":
        bg_color = RGBColor(20, 20, 20)
        font_color = RGBColor(255, 255, 255)
    else:
        bg_color = RGBColor(255, 255, 255)
        font_color = RGBColor(0, 0, 0)

    # Генерация слайдов
    for i in range(1, slide_count + 1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # пустой слайд
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1), Inches(14), Inches(1.5))
        shape.fill.solid()
        shape.fill.fore_color.rgb = font_color
        text_frame = shape.text_frame
        text_frame.text = f"{topic} — Слайд {i}"
        text_frame.paragraphs[0].font.size = Pt(40)
        text_frame.paragraphs[0].font.color.rgb = bg_color
        text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Добавляем пример изображения
        img_path = os.path.join("assets", "example.png")
        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, Inches(5), Inches(3), width=Inches(6))

    # Сохраняем PPTX
    output_path = os.path.join("presentations", f"{chat_id}_{topic}.pptx")
    prs.save(output_path)

    bot.send_message(chat_id, f"Готово! Презентация создана: {topic}.pptx")
    with open(output_path, "rb") as f:
        bot.send_document(chat_id, f)

    # Можно добавить генерацию превью JPG/PNG
    bot.send_message(chat_id, "Превью слайдов пока в разработке, но скоро будет!")

# --- Запуск бота ---
print("Shark бот запущен...")
bot.infinity_polling()
