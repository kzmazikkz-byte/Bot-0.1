import telebot
from telebot import types
from pptx import Presentation
from pptx.util import Inches, Pt
import requests
import os
import random
import openai
from io import BytesIO
from PIL import Image

TOKEN = os.environ["TOKEN"]
OPENAI_KEY = os.environ["OPENAI_KEY"]

openai.api_key = OPENAI_KEY
bot = telebot.TeleBot(TOKEN)

user_data = {}

# Старт
@bot.message_handler(commands=['start'])
def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🦈 Создать презентацию")
    kb.add("✏ Редактировать слайды")
    bot.send_message(message.chat.id, "Привет! Я Shark AI v4. Создаю профессиональные презентации с ИИ.", reply_markup=kb)

# Создание презентации
@bot.message_handler(func=lambda m: m.text=="🦈 Создать презентацию")
def create_presentation(message):
    msg = bot.send_message(message.chat.id, "Введите тему презентации:")
    bot.register_next_step_handler(msg, choose_style)

def choose_style(message):
    user_data[message.chat.id] = {"topic": message.text}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🌙 Dark", "☀ Light", "💜 Neon")
    msg = bot.send_message(message.chat.id, "Выберите стиль презентации:", reply_markup=kb)
    bot.register_next_step_handler(msg, choose_slides)

def choose_slides(message):
    user_data[message.chat.id]["style"] = message.text
    msg = bot.send_message(message.chat.id, "Сколько слайдов? (1-10)")
    bot.register_next_step_handler(msg, generate_presentation)

def generate_presentation(message):
    count = int(message.text)
    topic = user_data[message.chat.id]["topic"]
    style = user_data[message.chat.id]["style"]
    
    bot.send_message(message.chat.id, "⚡ Генерация презентации ИИ...")
    
    # Создаем текст для слайдов через OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":f"Сделай презентацию на тему '{topic}' из {count} слайдов. Дай текст для каждого слайда."}]
    )
    
    slides_text = response.choices[0].message.content.split("\n")
    
    prs = Presentation()
    
    for i in range(count):
        slide_layout = prs.slide_layouts[5]
        slide = prs.slides.add_slide(slide_layout)
        
        # Заголовок
        title = slide.shapes.title
        title.text = f"{topic} – слайд {i+1}"
        
        # Текст
        body = slide.placeholders[1]
        body.text = slides_text[i] if i < len(slides_text) else topic
        
        # Картинка
        try:
            img_url = f"https://source.unsplash.com/800x600/?{topic}"
            img_data = requests.get(img_url).content
            img_stream = BytesIO(img_data)
            img = Image.open(img_stream)
            img.save(f"temp{i}.png")
            slide.shapes.add_picture(f"temp{i}.png", Inches(6), Inches(2), height=Inches(3))
        except:
            pass
    
    file_name = f"shark_v4_{random.randint(1000,9999)}.pptx"
    prs.save(file_name)
    
    bot.send_document(message.chat.id, open(file_name, "rb"))

bot.infinity_polling()
