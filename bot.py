import telebot
import os

TOKEN = os.environ["TOKEN"]
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот работает 🚀")

print("Бот запущен...")
bot.infinity_polling()
