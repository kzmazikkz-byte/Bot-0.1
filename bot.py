import telebot
import os

TOKEN = os.environ["8656766315:AAFgJDtIs5eqF4af39fFJDRRRxx_Y2T0Va8"]
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот работает 🚀")

print("Бот запущен...")
bot.infinity_polling()
