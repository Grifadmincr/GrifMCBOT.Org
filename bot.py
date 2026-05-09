import telebot
from threading import Thread
from flask import Flask
from telebot import types

TOKEN = '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE'
ADMIN_ID = 8648741496
NEWS_CHANNEL = '@grifmcorg'
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

# ====== НОВОСТИ С КНОПКАМИ ======
NEWS_PER_PAGE = 3

def get_pinned_posts():
    """Получает закреплённые посты из канала"""
    try:
        # Получаем ID канала
        chat = bot.get_chat(NEWS_CHANNEL)
        # Пытаемся получить закреплённое сообщение
        # Примечание: Bot API не даёт прямой доступ к закреплённым сообщениям,
        # поэтому используем обходной путь через get_chat
        return [], chat.invite_link or f"t.me/{NEWS_CHANNEL[1:]}"
    except:
        return [], None

def format_news_page(page, total_pages, posts):
    """Форматирует страницу новостей"""
    text = f"📰 Новости сервера ({page}/{total_pages}):\n\n"
    start = (page - 1) * NEWS_PER_PAGE
    end = start + NEWS_PER_PAGE
    for i, post in enumerate(posts[start:end], start + 1):
        text += f"📌 Пост {i}\n"
    return text

@bot.message_handler(commands=['news'])
def news_cmd(message):
    # Получаем информацию о канале
    try:
        chat = bot.get_chat(NEWS_CHANNEL)
        link = chat.invite_link or f"t.me/{NEWS_CHANNEL[1:]}"
        
        text = (
            f"📰 **Новости сервера**\n\n"
            f"🔗 Все новости в нашем канале:\n"
            f"[{NEWS_CHANNEL}]({link})\n\n"
            f"📢 Подписывайся, чтобы быть в курсе!"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)
    except:
        bot.send_message(message.chat.id, "❌ Не удалось загрузить новости. Проверь, что бот добавлен в канал.")

# ====== ОБРАБОТКА ОСТАЛЬНЫХ СООБЩЕНИЙ ======
@bot.message_handler(func=lambda m: True)
def all_messages(message):
    chat_id = message.chat.id
    if chat_id in waiting:
        nick = message.text.strip()
        code = waiting.pop(chat_id)
        reward = PROMOCODES[code]
        bot.send_message(chat_id, f"✅ Готово!\n👤 {nick}\n🎁 {reward}\n\n⏳ Если награды нет 2 часа — @Manager_GrifMcRu")
        bot.send_message(ADMIN_ID, f"🎁 Промокод {code}\n👤 {nick}\n🎁 {reward}")
    else:
        bot.send_message(chat_id, "Команды: /start /news /list /promo /help")

def run_bot():
    print("Бот запущен!")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
