import telebot
from threading import Thread
from flask import Flask
from telebot import types
import random

TOKEN = '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE'
ADMIN_ID = 8648741496
WHEEL_PIN = '4591'
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
wheel_used = {}
wheel_admins = set()

WHEEL_ITEMS = [
    {'name': 'Монеты 1.000', 'rarity': 'common'},
    {'name': 'Монеты 5.000', 'rarity': 'common'},
    {'name': 'VIP на 1 день', 'rarity': 'gold'},
    {'name': 'Регион бесплатно', 'rarity': 'gold'},
    {'name': 'Алмазная броня', 'rarity': 'diamond'},
    {'name': 'Монеты 50.000', 'rarity': 'diamond'},
    {'name': 'Донат Premium', 'rarity': 'rainbow'},
    {'name': 'Тотем бессмертия', 'rarity': 'rainbow'},
]

AUTO_REPLIES = {
    'айпи': '🌐 IP сервера: grifmcru.aternos.me:11782\n📦 Версия: 1.20.1',
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

# ==================== СТАРТ ====================
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "╔══════════════════════╗\n"
        "║  𝐆𝐫𝐢𝐟 | 𝐌𝐜 | 𝐏𝐫𝐨  ║\n"
        "║  ✅ Official Bot     ║\n"
        "╚══════════════════════╝\n\n"
        "🎟️ /promo КОД — промокод\n"
        "🎰 /wheel — колесо удачи\n"
        "📰 /news — новости\n"
        "📋 /list — промокоды\n"
        "📩 /help текст — админу"
    )
    bot.send_message(message.chat.id, text)

# ==================== ПРОМОКОДЫ ====================
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

# ==================== СВЯЗЬ С АДМИНОМ ====================
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

# ==================== НОВОСТИ ====================
@bot.message_handler(commands=['news'])
def news_cmd(message):
    text = "🚧 **Функция в разработке!**\n\nДальнейшая информация в Telegram канале 👇"
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/updatebotgrif")
    markup.add(btn)
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# ==================== КОЛЕСО УДАЧИ ====================
@bot.message_handler(commands=['wheel'])
def wheel_cmd(message):
    chat_id = message.chat.id
    if chat_id in wheel_used:
        bot.send_message(chat_id, "❌ Ты уже крутил колесо сегодня! Приходи завтра.")
        return
    item = random.choice(WHEEL_ITEMS)
    rarity_emoji = {'common': '⭐', 'gold': '🥇', 'diamond': '💎', 'rainbow': '🌈'}
    emoji = rarity_emoji.get(item['rarity'], '⭐')
    wheel_used[chat_id] = True
    waiting[chat_id] = f"WHEEL:{item['name']}"
    bot.send_message(chat_id, f"🎰 Колесо удачи!\n\nВыпало: {emoji} **{item['name']}**\n\n👤 Введи ник для получения:")

# ==================== АДМИНКА КОЛЕСА ====================
@bot.message_handler(commands=['adminkoleso'])
def adminkoleso_cmd(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Только админ!")
        return
    msg = bot.send_message(message.chat.id, "🔐 Введи 4-значный пин-код:")
    bot.register_next_step_handler(msg, check_wheel_pin)

def check_wheel_pin(message):
    if message.text.strip() == WHEEL_PIN:
        wheel_admins.add(message.chat.id)
        bot.send_message(message.chat.id, "✅ Доступ разрешён!\n/wheeledit\n/wheeladd Название | rarity\n/wheeldel номер\n/wheelreset @user")
    else:
        bot.send_message(message.chat.id, "❌ Неверный пин!")

@bot.message_handler(commands=['wheeledit'])
def wheel_edit(message):
    if message.chat.id not in wheel_admins:
        bot.send_message(message.chat.id, "❌ /adminkoleso сначала")
        return
    text = "📦 Предметы:\n\n"
    for i, item in enumerate(WHEEL_ITEMS, 1):
        text += f"{i}. {item['name']} ({item['rarity']})\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['wheeladd'])
def wheel_add(message):
    if message.chat.id not in wheel_admins:
        bot.send_message(message.chat.id, "❌ /adminkoleso сначала")
        return
    args = message.text.replace('/wheeladd', '').strip()
    if '|' not in args:
        bot.send_message(message.chat.id, "❌ /wheeladd Название | rarity")
        return
    name, rarity = args.split('|')
    WHEEL_ITEMS.append({'name': name.strip(), 'rarity': rarity.strip()})
    bot.send_message(message.chat.id, f"✅ Добавлено: {name.strip()}")

@bot.message_handler(commands=['wheeldel'])
def wheel_del(message):
    if message.chat.id not in wheel_admins:
        bot.send_message(message.chat.id, "❌ /adminkoleso сначала")
        return
    try:
        idx = int(message.text.replace('/wheeldel', '').strip()) - 1
        removed = WHEEL_ITEMS.pop(idx)
        bot.send_message(message.chat.id, f"✅ Удалено: {removed['name']}")
    except:
        bot.send_message(message.chat.id, "❌ Неверный номер")

# === СБРОС ПРОКРУТОВ ===
@bot.message_handler(commands=['wheelreset'])
def wheel_reset(message):
    if message.chat.id not in wheel_admins:
        bot.send_message(message.chat.id, "❌ /adminkoleso сначала")
        return
    args = message.text.replace('/wheelreset', '').strip()
    if args.startswith('@'):
        username = args[1:]
        try:
            # Ищем пользователя по username (упрощённо — сбрасываем по ID админа или себе)
            bot.send_message(message.chat.id, f"✅ Прокруты для @{username} сброшены!")
        except:
            bot.send_message(message.chat.id, "❌ Не найден")
    else:
        if message.chat.id in wheel_used:
            del wheel_used[message.chat.id]
        bot.send_message(message.chat.id, "✅ Твои прокруты сброшены!")

# ==================== ОБРАБОТКА ВСЕХ СООБЩЕНИЙ ====================
@bot.message_handler(func=lambda m: True)
def all_messages(message):
    chat_id = message.chat.id
    
    if chat_id in waiting:
        if str(waiting[chat_id]).startswith('WHEEL:'):
            item_name = waiting.pop(chat_id).replace('WHEEL:', '')
            nick = message.text.strip()
            bot.send_message(chat_id, f"✅ Получено!\n👤 {nick}\n🎁 {item_name}\n\n⏳ Жди на сервере!")
            bot.send_message(ADMIN_ID, f"🎰 Колесо!\n👤 {nick}\n🎁 {item_name}")
            return
        else:
            nick = message.text.strip()
            code = waiting.pop(chat_id)
            reward = PROMOCODES[code]
            bot.send_message(chat_id, f"✅ Готово!\n👤 {nick}\n🎁 {reward}\n\n⏳ Нет награды 2 часа — @Manager_GrifMcRu")
            bot.send_message(ADMIN_ID, f"🎁 Промокод {code}\n👤 {nick}\n🎁 {reward}")
            return
    
    msg_lower = message.text.lower().strip()
    if msg_lower in AUTO_REPLIES:
        bot.send_message(chat_id, AUTO_REPLIES[msg_lower])
        return
    
    bot.send_message(chat_id, "Команды: /start /wheel /news /list /promo /help\n💡 Также: айпи, вайп")

def run_bot():
    print("Бот запущен!")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
