import telebot
from threading import Thread
from flask import Flask
from telebot import types

TOKEN = '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE'
ADMIN_ID = 8648741496
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
help_requests = {}

# === АВТООТВЕТЫ ===
AUTO_REPLIES = {
    'айпи': '🌐 IP сервера: grifmcru.aternos.me:11782\n📦 Версия: 1.20.1',
    'айпи сервера': '🌐 IP сервера: grifmcru.aternos.me:11782\n📦 Версия: 1.20.1',
    'ip': '🌐 IP сервера: grifmcru.aternos.me:11782\n📦 Версия: 1.20.1',
    'ип': '🌐 IP сервера: grifmcru.aternos.me:11782\n📦 Версия: 1.20.1',
    'сервер': '🌐 IP сервера: grifmcru.aternos.me:11782\n📦 Версия: 1.20.1',
    'вайп': '⏳ Следующий вайп: **середина лета, 30 числа в 20:00**\nГотовься! 🔥',
    'обнуление': '⏳ Следующий вайп: **середина лета, 30 числа в 20:00**\nГотовься! 🔥',
    'ваип': '⏳ Следующий вайп: **середина лета, 30 числа в 20:00**\nГотовься! 🔥',
    'вайпик': '⏳ Следующий вайп: **середина лета, 30 числа в 20:00**\nГотовься! 🔥',
}

@app.route('/')
def home():
    return "Бот работает!"

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "╔══════════════════════╗\n"
        "║  𝐆𝐫𝐢𝐟 | 𝐌𝐜 | 𝐏𝐫𝐨  ║\n"
        "║  ✅ Official Bot     ║\n"
        "╚══════════════════════╝\n\n"
        "🎟️ /promo КОД — промокод\n"
        "📰 /news — новости\n"
        "📋 /list — все промокоды\n"
        "📩 /help текст — админу"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['list'])
def list_cmd(message):
    text = "🎟️ Промокоды:\n\n"
    for code, reward in PROMOCODES.items():
        text += f"🔹 {code} → {reward}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['promo'])
def promo_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ /promo КОД")
        return
    code = args[1].upper()
    if code not in PROMOCODES:
        bot.send_message(message.chat.id, "❌ Неверный код!")
        return
    waiting[message.chat.id] = code
    bot.send_message(message.chat.id, f"✅ {code} — {PROMOCODES[code]}\n👤 Введи ник:")

@bot.message_handler(commands=['help'])
def help_admin(message):
    text = message.text.replace('/help', '').strip()
    if not text:
        bot.send_message(message.chat.id, "❌ /help текст")
        return
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    sent = bot.send_message(ADMIN_ID, f"📩 От {user_info}:\n{text}")
    help_requests[message.chat.id] = sent.message_id
    bot.send_message(message.chat.id, "✅ Отправлено!")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message and m.reply_to_message.message_id in help_requests.values())
def admin_reply(message):
    for user_id, msg_id in list(help_requests.items()):
        if msg_id == message.reply_to_message.message_id:
            bot.send_message(user_id, f"📩 Ответ админа:\n\n{message.text}")
            del help_requests[user_id]
            break

@bot.message_handler(commands=['news'])
def news_cmd(message):
    text = (
        "🚧 **Функция в разработке!**\n\n"
        "Дальнейшая информация в Telegram канале 👇"
    )
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/updatebotgrif")
    markup.add(btn)
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    chat_id = message.chat.id
    
    # Ожидание ника для промокода
    if chat_id in waiting:
        nick = message.text.strip()
        code = waiting.pop(chat_id)
        reward = PROMOCODES[code]
        bot.send_message(chat_id, f"✅ Готово!\n👤 {nick}\n🎁 {reward}\n\n⏳ Нет награды 2 часа — @Manager_GrifMcRu")
        bot.send_message(ADMIN_ID, f"🎁 Промокод {code}\n👤 {nick}\n🎁 {reward}")
        return
    
    # Автоответы
    msg_lower = message.text.lower().strip()
    if msg_lower in AUTO_REPLIES:
        bot.send_message(chat_id, AUTO_REPLIES[msg_lower])
        return
    
    # Стандартный ответ
    bot.send_message(chat_id, "Команды: /start /news /list /promo /help\n\n💡 Также ты можешь просто написать:\n• айпи — IP сервера\n• вайп — дата вайпа")

def run_bot():
    print("Бот запущен!")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
