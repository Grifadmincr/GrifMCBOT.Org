import telebot
from threading import Thread
from flask import Flask

TOKEN = '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE'
ADMIN_ID = 8648741496  # Твой Telegram ID
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
# Словарь для хранения пар "игрок-сообщение" для ответа админа
help_requests = {}

@app.route('/')
def home():
    return "Бот работает!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '🎮 GrifMC Pro Бот!\n/promo КОД - активировать промокод\n/list - список\n/help сообщение - связь с админом')

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

@bot.message_handler(commands=['help'])
def help_admin(message):
    text = message.text.replace('/help', '').strip()
    if not text:
        bot.send_message(message.chat.id, '❌ Напиши: /help твоё сообщение')
        return
    # Отправляем админу
    msg = bot.send_message(ADMIN_ID, f'📩 Сообщение от @{message.from_user.username or "игрока"} (ID: {message.chat.id}):\n\n{text}')
    # Сохраняем связку для ответа
    help_requests[message.chat.id] = msg.message_id
    bot.send_message(message.chat.id, '✅ Сообщение отправлено админу! Ожидай ответ.')

# Обработка ответа админа
@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message and m.reply_to_message.message_id in help_requests.values())
def admin_reply(message):
    # Ищем, кому ответил админ
    for user_id, msg_id in help_requests.items():
        if msg_id == message.reply_to_message.message_id:
            bot.send_message(user_id, f'📩 Ответ от админа:\n\n{message.text}')
            bot.send_message(ADMIN_ID, '✅ Ответ отправлен!')
            del help_requests[user_id]
            break

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    chat_id = message.chat.id
    if chat_id in waiting:
        nick = message.text.strip()
        code = waiting.pop(chat_id)
        reward = PROMOCODES[code]
        bot.send_message(chat_id, f'✅ Готово!\n👤 {nick}\n🎁 {reward}\n\n⏳ Если награды нет 2 часа — @Manager_GrifMcRu')
    else:
        bot.send_message(chat_id, 'Используй: /start /list /promo КОД /help сообщение')

def run_bot():
    print('Бот запущен!')
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
