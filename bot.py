import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pptx import Presentation

TOKEN = os.environ.get("TOKEN")

bot = telebot.TeleBot(TOKEN)

user_data = {}

# старт
@bot.message_handler(commands=['start'])
def start(message):

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🧠 Создать презентацию", callback_data="create"))

    bot.send_message(
        message.chat.id,
        "🦈 Shark AI\n\nЯ создаю презентации по твоему описанию.\n\nНажми кнопку ниже чтобы начать.",
        reply_markup=kb
    )


# кнопка создать
@bot.callback_query_handler(func=lambda call: call.data == "create")
def create_presentation(call):

    bot.send_message(
        call.message.chat.id,
        "✏️ Напиши тему презентации.\n\nПример:\nКосмос"
    )

    user_data[call.message.chat.id] = {"step": "theme"}


# тема
@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "theme")
def get_theme(message):

    user_data[message.chat.id]["theme"] = message.text
    user_data[message.chat.id]["step"] = "slides"

    bot.send_message(
        message.chat.id,
        "📊 Сколько слайдов?\n\nОтправь число от 3 до 10"
    )


# количество слайдов
@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "slides")
def get_slides(message):

    try:
        slides = int(message.text)

        if slides < 1 or slides > 20:
            bot.send_message(message.chat.id, "❌ Введи число от 1 до 20")
            return

    except:
        bot.send_message(message.chat.id, "❌ Нужно число")
        return

    user_data[message.chat.id]["slides"] = slides
    user_data[message.chat.id]["step"] = "done"

    generate_presentation(message)


# генерация
def generate_presentation(message):

    theme = user_data[message.chat.id]["theme"]
    slides_count = user_data[message.chat.id]["slides"]

    prs = Presentation()

    slides_text = []

    for i in range(slides_count):

        title = f"{theme} — часть {i+1}"

        text = f"Описание темы {theme}. Этот слайд объясняет важную часть темы."

        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)

        slide.shapes.title.text = title
        slide.placeholders[1].text = text

        slides_text.append(text)

    file_name = f"presentation_{message.chat.id}.pptx"

    prs.save(file_name)

    user_data[message.chat.id]["slides_text"] = slides_text

    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton("✏️ Изменить слайд", callback_data="edit"))
    kb.add(InlineKeyboardButton("✅ Скачать презентацию", callback_data="download"))

    bot.send_message(
        message.chat.id,
        "✅ Презентация создана!\n\nТы можешь изменить любой слайд.",
        reply_markup=kb
    )


# редактировать
@bot.callback_query_handler(func=lambda call: call.data == "edit")
def edit_slide(call):

    slides = user_data[call.message.chat.id]["slides"]

    kb = InlineKeyboardMarkup()

    for i in range(slides):
        kb.add(
            InlineKeyboardButton(
                f"Слайд {i+1}",
                callback_data=f"slide_{i}"
            )
        )

    bot.send_message(
        call.message.chat.id,
        "Выбери слайд для изменения",
        reply_markup=kb
    )


# выбор слайда
@bot.callback_query_handler(func=lambda call: call.data.startswith("slide_"))
def slide_selected(call):

    slide_index = int(call.data.split("_")[1])

    user_data[call.message.chat.id]["edit_slide"] = slide_index
    user_data[call.message.chat.id]["step"] = "editing"

    bot.send_message(
        call.message.chat.id,
        f"✏️ Напиши новый текст для слайда {slide_index+1}"
    )


# изменение текста
@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "editing")
def save_edit(message):

    slide_index = user_data[message.chat.id]["edit_slide"]

    user_data[message.chat.id]["slides_text"][slide_index] = message.text

    user_data[message.chat.id]["step"] = "done"

    bot.send_message(
        message.chat.id,
        "✅ Слайд обновлён!"
    )


# скачать
@bot.callback_query_handler(func=lambda call: call.data == "download")
def download(call):

    file_name = f"presentation_{call.message.chat.id}.pptx"

    with open(file_name, "rb") as f:
        bot.send_document(call.message.chat.id, f)


print("Shark AI запущен")

bot.infinity_polling()
