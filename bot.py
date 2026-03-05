import telebot
from telebot import types
from pptx import Presentation
from pptx.util import Inches
import os
import requests
import random

TOKEN = os.environ["TOKEN"]

bot = telebot.TeleBot(TOKEN)

users = {}

# старт
@bot.message_handler(commands=['start'])
def start(message):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🦈 Создать презентацию")

    bot.send_message(
        message.chat.id,
        "🦈 Shark AI\n\nЯ создаю профессиональные презентации.\n\nНажмите кнопку ниже.",
        reply_markup=kb
    )

# создать презентацию
@bot.message_handler(func=lambda m: m.text == "🦈 Создать презентацию")
def topic(message):

    msg = bot.send_message(message.chat.id,"📚 Напишите тему презентации")
    bot.register_next_step_handler(msg,style)

def style(message):

    users[message.chat.id] = {"topic":message.text}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🌙 Dark","☀ Light","💜 Neon")

    msg = bot.send_message(message.chat.id,"🎨 Выберите стиль",reply_markup=kb)
    bot.register_next_step_handler(msg,slides)

def slides(message):

    users[message.chat.id]["style"] = message.text

    msg = bot.send_message(message.chat.id,"📑 Сколько слайдов? (1-10)")
    bot.register_next_step_handler(msg,generate)

def generate(message):

    count = int(message.text)

    topic = users[message.chat.id]["topic"]
    style = users[message.chat.id]["style"]

    bot.send_message(message.chat.id,"⚡ Генерирую презентацию...")

    prs = Presentation()

    for i in range(count):

        slide_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(slide_layout)

        title = slide.shapes.add_textbox(
            Inches(0.5),
            Inches(0.3),
            Inches(8),
            Inches(1)
        )

        tf = title.text_frame
        tf.text = f"{topic} — часть {i+1}"

        text = slide.shapes.add_textbox(
            Inches(4.5),
            Inches(2),
            Inches(5),
            Inches(3)
        )

        body = text.text_frame
        body.text = f"Описание темы {topic}. Этот слайд объясняет важную часть темы."

        # картинка
        try:

            img_url = f"https://source.unsplash.com/800x600/?{topic}"
            img = requests.get(img_url).content

            img_name = f"img{i}.jpg"

            with open(img_name,"wb") as f:
                f.write(img)

            slide.shapes.add_picture(
                img_name,
                Inches(0.5),
                Inches(2),
                height=Inches(3)
            )

        except:
            pass

    filename = f"presentation_{random.randint(1000,9999)}.pptx"

    prs.save(filename)

    bot.send_document(message.chat.id,open(filename,"rb"))

bot.infinity_polling()
