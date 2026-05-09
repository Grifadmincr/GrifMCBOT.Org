import telebot
from threading import Thread
from flask import Flask

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

@app.route('/')
def home():
    return "Бот работает!"

# === КРАСИВЫЙ СТАРТ ===
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "╔════════════════════╗\n"
        "║  🎮  GRIFMC  PRO   ║\n"
        "║  ✅ Official Bot   ║\n"
        "╚════════════════════╝\n\n"
        "🎟️ /promo КОД — активировать промокод\n"
        "📋 /list — список промокодов\n"
        "📩 /help текст — связь с админом"
    )
    bot.send_message(message.chat.id, text)

# === СПИСОК ПРОМОКОДОВ ===
@bot.message_handler(commands=['list'])
def list_cmd(message):
    text = "🎟️ Доступные промокоды:\n\n"
    for code, reward in PROMOCODES.items():
        text += f"🔹 {code} → {reward}\n"
    bot.send_message(message.chat.id, text)

# === АКТИВАЦИЯ ПРОМОКОДА ===
@bot.message_handler(commands=['promo'])
def promo_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ Используй: /promo КОД\nНапример: /promo START2026")
        return
    code = args[1].upper()
    if code not in PROMOCODES:
        bot.send_message(message.chat.id, "❌ Неверный или несуществующий промокод!")
        return
    waiting[message.chat.id] = code
    bot.send_message(message.chat.id, f"✅ Код **{code}** принят!\n🎁 Награда: **{PROMOCODES[code]}**\n\n👤 Введи свой ник на сервере:")

# === СВЯЗЬ С АДМИНОМ ===
@bot.message_handler(commands=['help'])
def help_admin(message):
    text = message.text.replace('/help', '').strip()
    if not text:
        bot.send_message(message.chat.id, "❌ Напиши: /help твоё сообщение\nНапример: /help когда будет вайп?")
        return
    # Отправляем админу
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    msg_to_admin = (
        f"📩 **Новое сообщение!**\n"
        f"👤 От: {user_info}\n"
        f"💬 Текст: {text}"
    )
    sent = bot.send_message(ADMIN_ID, msg_to_admin, parse_mode="Markdown")
    # Сохраняем связку для ответа
    help_requests[message.chat.id] = sent.message_id
    bot.send_message(message.chat.id, "✅ Твоё сообщение отправлено админу! Ожидай ответа в этом чате.")

# === ОТВЕТ АДМИНА ИГРОКУ ===
@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message and m.reply_to_message.message_id in help_requests.values())
def admin_reply(message):
    replied_msg_id = message.reply_to_message.message_id
    # Ищем, кому ответил админ
    for user_id, msg_id in list(help_requests.items()):
        if msg_id == replied_msg_id:
            bot.send_message(
                user_id,
                f"📩 **Ответ от администратора:**\n\n{message.text}",
                parse_mode="Markdown"
            )
            bot.send_message(ADMIN_ID, "✅ Твой ответ отправлен игроку!")
            del help_requests[user_id]
            break

# === ОБРАБОТКА ОСТАЛЬНЫХ СООБЩЕНИЙ ===
@bot.message_handler(func=lambda m: True)
def all_messages(message):
    chat_id = message.chat.id
    
    # Если ждём ник для промокода
    if chat_id in waiting:
        nick = message.text.strip()
        code = waiting.pop(chat_id)
        reward = PROMOCODES[code]
        bot.send_message(
            chat_id,
            f"✅ **Промокод активирован!**\n\n"
            f"👤 Ник: **{nick}**\n"
            f"🎁 Награда: **{reward}**\n\n"
            f"⏳ Если награды нет 2 часа — пиши @Manager_GrifMcRu",
            parse_mode="Markdown"
        )
        # Уведомление админу
        bot.send_message(
            ADMIN_ID,
            f"🎁 Активирован промокод **{code}**\n👤 Ник: **{nick}**\n🎁 Награда: **{reward}**",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(chat_id, "Используй команды:\n/start — главное меню\n/promo КОД — активировать промокод\n/list — список промокодов\n/help текст — связь с админом")

# === ЗАПУСК ===
def run_bot():
    print("Бот запущен!")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
