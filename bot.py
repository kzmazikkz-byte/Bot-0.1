import telebot
from telebot import types
from pptx import Presentation
from pptx.util import Inches
import requests
import os
import random
import openai

TOKEN = os.environ["TOKEN"]
OPENAI_KEY = os.environ["OPENAI_KEY"]

openai.api_key = OPENAI_KEY

bot = telebot.TeleBot(TOKEN)

user_data = {}

# старт
@bot.message_handler(commands=['start'])
def start(message):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🦈 Создать презентацию")

    bot.send_message(
        message.chat.id,
        "🦈 Shark AI\n\nЯ создаю профессиональные презентации с помощью ИИ.",
        reply_markup=kb
    )

# создать
@bot.message_handler(func=lambda m: m.text == "🦈 Создать презентацию")
def topic(message):

    msg = bot.send_message(message.chat.id,"📚 Напишите тему презентации")
    bot.register_next_step_handler(msg,style)

def style(message):

    user_data[message.chat.id] = {"topic":message.text}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🌙 Dark","☀ Light","💜 Neon")

    msg = bot.send_message(message.chat.id,"🎨 Выберите стиль")
    bot.register_next_step_handler(msg,slides)

def slides(message):

    user_data[message.chat.id]["style"] = message.text

    msg = bot.send_message(message.chat.id,"📑 Сколько слайдов? (1-10)")
    bot.register_next_step_handler(msg,generate)

def generate(message):

    count = int(message.text)

    topic = user_data[message.chat.id]["topic"]

    bot.send_message(message.chat.id,"⚡ ИИ генерирует презентацию...")

    # запрос к ИИ
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"user","content":f"Сделай структуру презентации на тему {topic} из {count} слайдов"}
        ]
    )

    text = response.choices[0].message.content

    slides_text = text.split("\n")

    prs = Presentation()

    for i in range(count):

        slide_layout = prs.slide_layouts[5]
        slide = prs.slides.add_slide(slide_layout)

        title = slide.shapes.title
        title.text = f"{topic} {i+1}"

        body = slide.placeholders[1]
        body.text = slides_text[i] if i < len(slides_text) else topic

        try:

            img_url = f"https://source.unsplash.com/800x600/?{topic}"
            img = requests.get(img_url).content

            img_name = f"img{i}.jpg"

            with open(img_name,"wb") as f:
                f.write(img)

            slide.shapes.add_picture(
                img_name,
                Inches(6),
                Inches(2),
                height=Inches(3)
            )

        except:
            pass

    file = f"shark_{random.randint(1000,9999)}.pptx"

    prs.save(file)

    bot.send_document(message.chat.id,open(file,"rb"))

bot.infinity_polling()
