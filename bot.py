import telebot
import os

TOKEN = os.environ.get('BOT_TOKEN', '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, '🎮 Привет! Я бот сервера GrifMC Pro!\n\nКоманды:\n/help - Помощь\n/server - Информация о сервере')

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, '📋 Список команд:\n/start - Запуск бота\n/help - Помощь\n/server - IP сервера')

@bot.message_handler(commands=['server'])
def server(message):
    bot.reply_to(message, '🌐 IP сервера: grifmcru.aternos.me:11782\n📦 Версия: 1.20.1\n🟢 Статус: Онлайн')

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, 'Используй команды: /start /help /server')

print('Бот запущен!')
bot.polling(none_stop=True)
