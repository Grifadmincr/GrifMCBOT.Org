import telebot
from threading import Thread
from flask import Flask

TOKEN = '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

PROMOCODES = {
    'START2026': '50.000 монет',
    'VIPBONUS': 'VIP на 3 дня',
    'FREEDOM': 'Бесплатный регион',
    'LUCKY10': '10.000 монет',
    'GRIFGOLD': 'Золотая броня'
}

waiting = {}

@app.route('/')
def home():
    return "Бот работает!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '🎮 GrifMC Pro Бот!\n/promo КОД\n/list')

@bot.message_handler(commands=['list'])
def list_cmd(message):
    text = '🎟️ Промокоды:\n'
    for code, reward in PROMOCODES.items():
        text += f'{code} — {reward}\n'
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['promo'])
def promo_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, '❌ /promo КОД')
        return
    code = args[1].upper()
    if code not in PROMOCODES:
        bot.send_message(message.chat.id, '❌ Неверный код!')
        return
    waiting[message.chat.id] = code
    bot.send_message(message.chat.id, f'✅ {code} — {PROMOCODES[code]}\n👤 Введи ник:')

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    chat_id = message.chat.id
    if chat_id in waiting:
        nick = message.text.strip()
        code = waiting.pop(chat_id)
        reward = PROMOCODES[code]
        bot.send_message(chat_id, f'✅ Готово!\n👤 {nick}\n🎁 {reward}\n\n⏳ Если награды нет 2 часа — @Manager_GrifMcRu')
    else:
        bot.send_message(chat_id, 'Используй: /start /list /promo КОД')

def run_bot():
    print('Бот запущен!')
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
