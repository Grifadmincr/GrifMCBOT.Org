import telebot
from threading import Thread
from flask import Flask
import requests

TOKEN = '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
WEB3FORMS_KEY = '42864224-6df0-4e25-8068-7b486cf314dd'

PROMOCODES = {
    'START2026': '50.000 монет',
    'VIPBONUS': 'VIP на 3 дня',
    'FREEDOM': 'Бесплатный регион',
    'LUCKY10': '10.000 монет',
    'GRIFGOLD': 'Золотая броня'
}

@app.route('/')
def home():
    return "Бот работает!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, '🎮 GrifMC Pro Бот!\n/promo КОД - активировать промокод\n/list - список')

@bot.message_handler(commands=['list'])
def list_cmd(message):
    text = '🎟️ Промокоды:\n'
    for code, reward in PROMOCODES.items():
        text += f'{code} — {reward}\n'
    bot.reply_to(message, text)

@bot.message_handler(commands=['promo'])
def promo_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, '❌ /promo КОД')
        return
    code = args[1].upper()
    if code not in PROMOCODES:
        bot.reply_to(message, '❌ Неверный код!')
        return
    msg = bot.reply_to(message, f'✅ {code} — {PROMOCODES[code]}\n👤 Введи ник:')
    bot.register_next_step_handler(msg, get_nick, code)

def get_nick(message, code):
    nick = message.text.strip()
    reward = PROMOCODES[code]
    try:
        response = requests.post('https://api.web3forms.com/submit', data={
            'access_key': WEB3FORMS_KEY,
            'subject': f'Промокод: {code}',
            'Ник': nick,
            'Код': code,
            'Награда': reward
        }, timeout=10)
        print('Письмо отправлено:', response.status_code)
    except Exception as e:
        print('Ошибка:', e)
    bot.reply_to(message, f'✅ Готово!\n👤 {nick}\n🎁 {reward}\n📧 Ожидай награду на сервере!')

def run_bot():
    print('Бот запущен!')
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
