import telebot
from threading import Thread
from flask import Flask
from telebot import types
import random
import json

TOKEN = '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE'
ADMIN_ID = 8648741496
WHEEL_PIN = '4591'
SHOP_PIN = '4599'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ==================== ДАННЫЕ ====================
PROMOCODES = {
    'START2026': '50.000 монет', 'VIPBONUS': 'VIP на 3 дня',
    'FREEDOM': 'Бесплатный регион', 'LUCKY10': '10.000 монет', 'GRIFGOLD': 'Золотая броня'
}

WHEEL_ITEMS = [
    {'name': 'Монеты 1.000', 'rarity': 'common'}, {'name': 'Монеты 5.000', 'rarity': 'common'},
    {'name': 'VIP на 1 день', 'rarity': 'gold'}, {'name': 'Регион бесплатно', 'rarity': 'gold'},
    {'name': 'Алмазная броня', 'rarity': 'diamond'}, {'name': 'Монеты 50.000', 'rarity': 'diamond'},
    {'name': 'Донат Premium', 'rarity': 'rainbow'}, {'name': 'Тотем бессмертия', 'rarity': 'rainbow'},
]

AUTO_REPLIES = {
    'айпи': '🌐 IP: grifmcru.aternos.me:11782\n📦 1.20.1',
    'ip': '🌐 IP: grifmcru.aternos.me:11782\n📦 1.20.1',
    'сервер': '🌐 IP: grifmcru.aternos.me:11782\n📦 1.20.1',
    'вайп': '⏳ Середина лета, 30 числа в 20:00 🔥',
}

# Товары магазина
SHOP_ITEMS = [
    {'name': 'VIP на 1 день', 'price': 500},
    {'name': 'Регион бесплатно', 'price': 1000},
    {'name': '10.000 монет', 'price': 300},
]

# Валюта игроков
player_balance = {}  # {user_id: coins}
daily_used = {}

ADMINS = {ADMIN_ID}
shop_admins = set()

waiting = {}
help_requests = {}
wheel_used = {}
wheel_admins = set()

# ==================== ФУНКЦИИ ====================
def get_balance(uid):
    return player_balance.get(uid, 0)

def add_balance(uid, amount):
    player_balance[uid] = get_balance(uid) + amount

def remove_balance(uid, amount):
    player_balance[uid] = max(0, get_balance(uid) - amount)

@app.route('/')
def home():
    return "Bot works!"

# ==================== СТАРТ ====================
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "╔══════════════════════╗\n"
        "║  𝐆𝐫𝐢𝐟 | 𝐌𝐜 | 𝐏𝐫𝐨  ║\n"
        "║  ✅ Official Bot     ║\n"
        "╚══════════════════════╝\n\n"
        "🎟️ /promo КОД\n🎰 /wheel\n💰 /shop\n📋 /list\n"
        "📩 /help текст\n🚨 /report\n💵 /balance\n📋 /daily"
    )
    bot.send_message(message.chat.id, text)

# ==================== БАЛАНС ====================
@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    bal = get_balance(message.chat.id)
    bot.send_message(message.chat.id, f"💰 Твой баланс: **{bal}** монет", parse_mode="Markdown")

# ==================== ЕЖЕДНЕВНЫЙ БОНУС ====================
@bot.message_handler(commands=['daily'])
def daily_cmd(message):
    uid = message.chat.id
    if uid in daily_used:
        bot.send_message(uid, "❌ Ты уже получал бонус сегодня!")
        return
    amount = random.randint(100, 500)
    add_balance(uid, amount)
    daily_used[uid] = True
    bot.send_message(uid, f"🎁 Ежедневный бонус: **+{amount}** монет!\n💰 Баланс: **{get_balance(uid)}**", parse_mode="Markdown")

# ==================== МАГАЗИН ====================
@bot.message_handler(commands=['shop'])
def shop_cmd(message):
    text = "🛒 **Магазин услуг:**\n\n"
    for i, item in enumerate(SHOP_ITEMS, 1):
        text += f"{i}. {item['name']} — **{item['price']}** монет\n"
    text += "\nЧтобы купить: /buy номер"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['buy'])
def buy_cmd(message):
    try:
        idx = int(message.text.replace('/buy', '').strip()) - 1
        if idx < 0 or idx >= len(SHOP_ITEMS):
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ /buy номер\nПример: /buy 1")
        return
    
    uid = message.chat.id
    item = SHOP_ITEMS[idx]
    if get_balance(uid) < item['price']:
        bot.send_message(uid, f"❌ Недостаточно монет! Нужно: {item['price']}, у тебя: {get_balance(uid)}")
        return
    
    remove_balance(uid, item['price'])
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {uid}"
    bot.send_message(uid, f"✅ Куплено: **{item['name']}** за {item['price']} монет!\n💰 Остаток: {get_balance(uid)}", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"🛒 Покупка!\n👤 {user_info}\n🛍️ {item['name']}\n💵 {item['price']} монет")

# ==================== АДМИНКА МАГАЗИНА (валюта) ====================
@bot.message_handler(commands=['adminshop'])
def adminshop_cmd(message):
    if message.chat.id not in ADMINS:
        bot.send_message(message.chat.id, "❌ Только админ!")
        return
    msg = bot.send_message(message.chat.id, "🔐 Введи пин-код (4 цифры):")
    bot.register_next_step_handler(msg, check_shop_pin)

def check_shop_pin(message):
    if message.text.strip() == SHOP_PIN:
        shop_admins.add(message.chat.id)
        bot.send_message(message.chat.id, "✅ Доступ открыт!\n/give @user сумма\n/take @user сумма\n/balances — все балансы")
    else:
        bot.send_message(message.chat.id, "❌ Неверный пин!")

@bot.message_handler(commands=['give'])
def give_cmd(message):
    if message.chat.id not in shop_admins:
        bot.send_message(message.chat.id, "❌ /adminshop сначала")
        return
    args = message.text.split()
    if len(args) < 3:
        bot.send_message(message.chat.id, "❌ /give @user сумма")
        return
    username = args[1]
    if not username.startswith('@'):
        bot.send_message(message.chat.id, "❌ Используй @username")
        return
    try:
        amount = int(args[2])
        # Ищем пользователя (упрощённо — по username в данных)
        for uid in player_balance:
            try:
                if bot.get_chat(uid).username == username[1:]:
                    add_balance(uid, amount)
                    bot.send_message(message.chat.id, f"✅ Выдано {amount} монет пользователю {username}")
                    bot.send_message(uid, f"💰 Админ выдал тебе {amount} монет!\nБаланс: {get_balance(uid)}")
                    return
            except:
                pass
        bot.send_message(message.chat.id, f"❌ Пользователь {username} не найден в базе")
    except:
        bot.send_message(message.chat.id, "❌ Неверная сумма")

@bot.message_handler(commands=['take'])
def take_cmd(message):
    if message.chat.id not in shop_admins:
        bot.send_message(message.chat.id, "❌ /adminshop сначала")
        return
    args = message.text.split()
    if len(args) < 3:
        bot.send_message(message.chat.id, "❌ /take @user сумма")
        return
    username = args[1]
    if not username.startswith('@'):
        bot.send_message(message.chat.id, "❌ Используй @username")
        return
    try:
        amount = int(args[2])
        for uid in player_balance:
            try:
                if bot.get_chat(uid).username == username[1:]:
                    remove_balance(uid, amount)
                    bot.send_message(message.chat.id, f"✅ Списано {amount} монет у {username}")
                    bot.send_message(uid, f"💰 Админ списал {amount} монет.\nБаланс: {get_balance(uid)}")
                    return
            except:
                pass
        bot.send_message(message.chat.id, f"❌ {username} не найден")
    except:
        bot.send_message(message.chat.id, "❌ Неверная сумма")

@bot.message_handler(commands=['balances'])
def balances_cmd(message):
    if message.chat.id not in shop_admins:
        bot.send_message(message.chat.id, "❌ /adminshop сначала")
        return
    text = "💰 Балансы игроков:\n\n"
    for uid, bal in player_balance.items():
        try:
            user = bot.get_chat(uid)
            name = f"@{user.username}" if user.username else f"ID:{uid}"
            text += f"{name}: {bal} монет\n"
        except:
            text += f"ID:{uid}: {bal} монет\n"
    if not player_balance:
        text += "Нет данных"
    bot.send_message(message.chat.id, text)

# ==================== АДМИНКА МАГАЗИНА 2 (товары) ====================
@bot.message_handler(commands=['adminshop2'])
def adminshop2_cmd(message):
    if message.chat.id not in shop_admins:
        bot.send_message(message.chat.id, "❌ Сначала /adminshop")
        return
    text = "📦 Товары:\n\n"
    for i, item in enumerate(SHOP_ITEMS, 1):
        text += f"{i}. {item['name']} — {item['price']} монет\n"
    text += "\n/additem Название | цена\n/delitem номер"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['additem'])
def additem_cmd(message):
    if message.chat.id not in shop_admins:
        return
    args = message.text.replace('/additem', '').strip()
    if '|' not in args:
        bot.send_message(message.chat.id, "❌ /additem Название | цена")
        return
    name, price = args.split('|')
    try:
        price = int(price.strip())
        SHOP_ITEMS.append({'name': name.strip(), 'price': price})
        bot.send_message(message.chat.id, f"✅ Добавлено: {name.strip()} за {price} монет")
    except:
        bot.send_message(message.chat.id, "❌ Неверная цена")

@bot.message_handler(commands=['delitem'])
def delitem_cmd(message):
    if message.chat.id not in shop_admins:
        return
    try:
        idx = int(message.text.replace('/delitem', '').strip()) - 1
        removed = SHOP_ITEMS.pop(idx)
        bot.send_message(message.chat.id, f"✅ Удалено: {removed['name']}")
    except:
        bot.send_message(message.chat.id, "❌ Неверный номер")

# ==================== ОСТАЛЬНЫЕ КОМАНДЫ (из старого кода) ====================
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
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/updatebotgrif"))
    bot.send_message(message.chat.id, "🚧 Функция в разработке! 👇", reply_markup=markup)

@bot.message_handler(commands=['report'])
def report_cmd(message):
    text = message.text.replace('/report', '').strip()
    if not text:
        bot.send_message(message.chat.id, "❌ /report\nНик нарушителя: ...\nМой ник: ...")
        return
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    bot.send_message(ADMIN_ID, f"🚨 Жалоба от {user_info}:\n{text}")
    bot.send_message(message.chat.id, "✅ Отправлено!")

@bot.message_handler(commands=['wheel'])
def wheel_cmd(message):
    uid = message.chat.id
    if uid in wheel_used:
        bot.send_message(uid, "❌ Уже крутил сегодня!")
        return
    item = random.choice(WHEEL_ITEMS)
    emojis = {'common':'⭐','gold':'🥇','diamond':'💎','rainbow':'🌈'}
    emoji = emojis.get(item['rarity'], '⭐')
    wheel_used[uid] = True
    waiting[uid] = f"WHEEL:{item['name']}"
    bot.send_message(uid, f"🎰 {emoji} **{item['name']}**\n👤 Введи ник:", parse_mode="Markdown")

# Админка колеса
@bot.message_handler(commands=['adminkoleso'])
def adminkoleso_cmd(message):
    if message.chat.id != ADMIN_ID: return
    msg = bot.send_message(message.chat.id, "🔐 Пин:")
    bot.register_next_step_handler(msg, check_wheel_pin)

def check_wheel_pin(message):
    if message.text.strip() == WHEEL_PIN:
        wheel_admins.add(message.chat.id)
        bot.send_message(message.chat.id, "✅ Доступ!")
    else:
        bot.send_message(message.chat.id, "❌ Неверно")

@bot.message_handler(commands=['wheeledit'])
def wheel_edit(message):
    if message.chat.id not in wheel_admins: return
    text = "📦 Предметы:\n\n"
    for i, item in enumerate(WHEEL_ITEMS, 1):
        text += f"{i}. {item['name']} ({item['rarity']})\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['wheeladd'])
def wheel_add(message):
    if message.chat.id not in wheel_admins: return
    args = message.text.replace('/wheeladd','').strip()
    if '|' not in args: bot.send_message(message.chat.id, "❌ Название | rarity"); return
    name, rarity = args.split('|')
    WHEEL_ITEMS.append({'name':name.strip(), 'rarity':rarity.strip()})
    bot.send_message(message.chat.id, f"✅ {name.strip()}")

@bot.message_handler(commands=['wheeldel'])
def wheel_del(message):
    if message.chat.id not in wheel_admins: return
    try:
        idx = int(message.text.replace('/wheeldel','').strip()) - 1
        removed = WHEEL_ITEMS.pop(idx)
        bot.send_message(message.chat.id, f"✅ {removed['name']}")
    except:
        bot.send_message(message.chat.id, "❌ Номер")

@bot.message_handler(commands=['wheelreset'])
def wheel_reset(message):
    if message.chat.id not in wheel_admins: return
    if message.chat.id in wheel_used: del wheel_used[message.chat.id]
    bot.send_message(message.chat.id, "✅ Сброшено")

# ==================== ОБРАБОТКА ВСЕХ СООБЩЕНИЙ ====================
@bot.message_handler(func=lambda m: True)
def all_messages(message):
    chat_id = message.chat.id
    
    if chat_id in waiting:
        if str(waiting[chat_id]).startswith('WHEEL:'):
            item_name = waiting.pop(chat_id).replace('WHEEL:', '')
            nick = message.text.strip()
            bot.send_message(chat_id, f"✅ {nick}\n🎁 {item_name}")
            bot.send_message(ADMIN_ID, f"🎰 {nick} — {item_name}")
            return
        else:
            nick = message.text.strip()
            code = waiting.pop(chat_id)
            reward = PROMOCODES[code]
            bot.send_message(chat_id, f"✅ {nick}\n🎁 {reward}")
            bot.send_message(ADMIN_ID, f"🎁 {code} | {nick} | {reward}")
            return
    
    msg_lower = message.text.lower().strip()
    if msg_lower in AUTO_REPLIES:
        bot.send_message(chat_id, AUTO_REPLIES[msg_lower])
        return
    
    bot.send_message(chat_id, "/start /shop /balance /daily /wheel /list /promo /help /report")

def run_bot():
    print("Bot started!")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
