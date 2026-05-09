import telebot
from threading import Thread
from flask import Flask
from telebot import types
import random

TOKEN = '8604199684:AAFO1YuWPWS3Lyi5J4vcFCfdhfDyzevoFBE'
ADMIN_ID = 8648741496
WHEEL_PIN = '4591'
SHOP_PIN = '4599'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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

SHOP_ITEMS = [
    {'name': 'VIP на 1 день', 'price': 500},
    {'name': 'Регион бесплатно', 'price': 1000},
    {'name': '10.000 монет', 'price': 300},
]

player_balance = {}
daily_used = {}
shop_admins = set()
waiting = {}
help_requests = {}
wheel_used = {}
wheel_admins = set()

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
        "💰 /shop — магазин\n"
        "🎰 /wheel — колесо\n"
        "🎟️ /promo — промокод\n"
        "📋 /list — промокоды\n"
        "📩 /help — админу\n"
        "🚨 /report — жалоба\n"
        "📰 /news — новости"
    )
    bot.send_message(message.chat.id, text)

# ==================== МАГАЗИН ====================
@bot.message_handler(commands=['shop'])
def shop_cmd(message):
    uid = message.chat.id
    bal = get_balance(uid)
    
    text = f"💰 Твой баланс: **{bal}** монет\n\n🛒 Товары:\n"
    for i, item in enumerate(SHOP_ITEMS, 1):
        text += f"{i}. {item['name']} — **{item['price']}** монет\n"
    text += "\n🛍️ Чтобы купить: /buy номер"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💵 Баланс", callback_data="balance"))
    markup.add(types.InlineKeyboardButton("🎁 Daily бонус", callback_data="daily"))
    bot.send_message(uid, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'balance')
def callback_balance(call):
    bal = get_balance(call.message.chat.id)
    bot.answer_callback_query(call.id, f"Баланс: {bal} монет", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'daily')
def callback_daily(call):
    uid = call.message.chat.id
    if uid in daily_used:
        bot.answer_callback_query(call.id, "Ты уже получал бонус сегодня!", show_alert=True)
        return
    amount = random.randint(100, 500)
    add_balance(uid, amount)
    daily_used[uid] = True
    bot.answer_callback_query(call.id, f"Получено +{amount} монет!", show_alert=True)
    bot.send_message(uid, f"🎁 Ежедневный бонус: **+{amount}** монет!\n💰 Баланс: **{get_balance(uid)}**", parse_mode="Markdown")

@bot.message_handler(commands=['buy'])
def buy_cmd(message):
    try:
        idx = int(message.text.replace('/buy', '').strip()) - 1
        if idx < 0 or idx >= len(SHOP_ITEMS):
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ /buy номер")
        return
    
    uid = message.chat.id
    item = SHOP_ITEMS[idx]
    if get_balance(uid) < item['price']:
        bot.send_message(uid, f"❌ Недостаточно! Нужно: {item['price']}, у тебя: {get_balance(uid)}")
        return
    
    remove_balance(uid, item['price'])
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {uid}"
    bot.send_message(uid, f"✅ Куплено: **{item['name']}** за {item['price']} монет!", parse_mode="Markdown")
    bot.send_message(ADMIN_ID, f"🛒 {user_info}\n🛍️ {item['name']}\n💵 {item['price']}")

# ==================== АДМИНКИ ====================
@bot.message_handler(commands=['adminshop'])
def adminshop_cmd(message):
    if message.chat.id != ADMIN_ID: return
    msg = bot.send_message(message.chat.id, "🔐 Пин:")
    bot.register_next_step_handler(msg, check_shop_pin)

def check_shop_pin(message):
    if message.text.strip() == SHOP_PIN:
        shop_admins.add(message.chat.id)
        bot.send_message(message.chat.id, "✅ Доступ!\n/give @user сумма\n/take @user сумма\n/balances")
    else:
        bot.send_message(message.chat.id, "❌ Неверно")

@bot.message_handler(commands=['give'])
def give_cmd(message):
    if message.chat.id not in shop_admins: return
    args = message.text.split()
    if len(args) < 3 or not args[1].startswith('@'):
        bot.send_message(message.chat.id, "❌ /give @user сумма"); return
    try:
        amount = int(args[2])
        username = args[1][1:]
        for uid in player_balance:
            try:
                if bot.get_chat(uid).username == username:
                    add_balance(uid, amount)
                    bot.send_message(message.chat.id, f"✅ +{amount} @{username}")
                    bot.send_message(uid, f"💰 Админ выдал +{amount}!")
                    return
            except: pass
        bot.send_message(message.chat.id, "❌ Не найден")
    except:
        bot.send_message(message.chat.id, "❌ Сумма")

@bot.message_handler(commands=['take'])
def take_cmd(message):
    if message.chat.id not in shop_admins: return
    args = message.text.split()
    if len(args) < 3 or not args[1].startswith('@'):
        bot.send_message(message.chat.id, "❌ /take @user сумма"); return
    try:
        amount = int(args[2])
        username = args[1][1:]
        for uid in player_balance:
            try:
                if bot.get_chat(uid).username == username:
                    remove_balance(uid, amount)
                    bot.send_message(message.chat.id, f"✅ -{amount} @{username}")
                    return
            except: pass
        bot.send_message(message.chat.id, "❌ Не найден")
    except:
        bot.send_message(message.chat.id, "❌ Сумма")

@bot.message_handler(commands=['balances'])
def balances_cmd(message):
    if message.chat.id not in shop_admins: return
    text = "💰 Балансы:\n\n"
    for uid, bal in player_balance.items():
        try:
            u = bot.get_chat(uid)
            name = f"@{u.username}" if u.username else f"ID:{uid}"
            text += f"{name}: {bal}\n"
        except:
            text += f"ID:{uid}: {bal}\n"
    bot.send_message(message.chat.id, text or "Нет данных")

@bot.message_handler(commands=['adminshop2'])
def adminshop2_cmd(message):
    if message.chat.id not in shop_admins: return
    text = "📦 Товары:\n\n"
    for i, item in enumerate(SHOP_ITEMS, 1):
        text += f"{i}. {item['name']} — {item['price']}\n"
    text += "\n/additem Название | цена\n/delitem номер"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['additem'])
def additem_cmd(message):
    if message.chat.id not in shop_admins: return
    args = message.text.replace('/additem', '').strip()
    if '|' not in args:
        bot.send_message(message.chat.id, "❌ /additem Название | цена"); return
    name, price = args.split('|')
    try:
        SHOP_ITEMS.append({'name': name.strip(), 'price': int(price.strip())})
        bot.send_message(message.chat.id, f"✅ {name.strip()}")
    except:
        bot.send_message(message.chat.id, "❌ Цена")

@bot.message_handler(commands=['delitem'])
def delitem_cmd(message):
    if message.chat.id not in shop_admins: return
    try:
        idx = int(message.text.replace('/delitem', '').strip()) - 1
        removed = SHOP_ITEMS.pop(idx)
        bot.send_message(message.chat.id, f"✅ {removed['name']}")
    except:
        bot.send_message(message.chat.id, "❌ Номер")

# ==================== ОСТАЛЬНОЕ (без изменений) ====================
@bot.message_handler(commands=['list'])
def list_cmd(message):
    text = "🎟️ Промокоды:\n\n"
    for code, reward in PROMOCODES.items():
        text += f"🔹 {code} → {reward}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['promo'])
def promo_cmd(message):
    args = message.text.split()
    if len(args) < 2: bot.send_message(message.chat.id, "❌ /promo КОД"); return
    code = args[1].upper()
    if code not in PROMOCODES: bot.send_message(message.chat.id, "❌ Неверный!"); return
    waiting[message.chat.id] = code
    bot.send_message(message.chat.id, f"✅ {code} — {PROMOCODES[code]}\n👤 Введи ник:")

@bot.message_handler(commands=['help'])
def help_admin(message):
    text = message.text.replace('/help', '').strip()
    if not text: bot.send_message(message.chat.id, "❌ /help текст"); return
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    sent = bot.send_message(ADMIN_ID, f"📩 От {user_info}:\n{text}")
    help_requests[message.chat.id] = sent.message_id
    bot.send_message(message.chat.id, "✅ Отправлено!")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message and m.reply_to_message.message_id in help_requests.values())
def admin_reply(message):
    for uid, mid in list(help_requests.items()):
        if mid == message.reply_to_message.message_id:
            bot.send_message(uid, f"📩 Ответ админа:\n\n{message.text}")
            del help_requests[uid]; break

@bot.message_handler(commands=['news'])
def news_cmd(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Канал", url="https://t.me/updatebotgrif"))
    bot.send_message(message.chat.id, "🚧 Новости в канале 👇", reply_markup=markup)

@bot.message_handler(commands=['report'])
def report_cmd(message):
    text = message.text.replace('/report', '').strip()
    if not text: bot.send_message(message.chat.id, "❌ /report\nНик:...\nМой ник:..."); return
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    bot.send_message(ADMIN_ID, f"🚨 От {user_info}:\n{text}")
    bot.send_message(message.chat.id, "✅ Отправлено!")

@bot.message_handler(commands=['wheel'])
def wheel_cmd(message):
    uid = message.chat.id
    if uid in wheel_used: bot.send_message(uid, "❌ Уже крутил!"); return
    item = random.choice(WHEEL_ITEMS)
    emojis = {'common':'⭐','gold':'🥇','diamond':'💎','rainbow':'🌈'}
    emoji = emojis.get(item['rarity'], '⭐')
    wheel_used[uid] = True
    waiting[uid] = f"WHEEL:{item['name']}"
    bot.send_message(uid, f"🎰 {emoji} **{item['name']}**\n👤 Введи ник:", parse_mode="Markdown")

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

@bot.message_handler(commands=['wheeledit','wheeladd','wheeldel','wheelreset'])
def wheel_admin(message):
    if message.chat.id not in wheel_admins: return
    cmd = message.text.split()[0][1:]
    if cmd == 'wheeladd':
        args = message.text.replace('/wheeladd','').strip()
        if '|' in args:
            n, r = args.split('|')
            WHEEL_ITEMS.append({'name':n.strip(),'rarity':r.strip()})
            bot.send_message(message.chat.id, f"✅ {n.strip()}")
    elif cmd == 'wheeldel':
        try:
            idx = int(message.text.replace('/wheeldel','').strip()) - 1
            bot.send_message(message.chat.id, f"✅ {WHEEL_ITEMS.pop(idx)['name']}")
        except: bot.send_message(message.chat.id, "❌ Номер")
    elif cmd == 'wheelreset':
        if message.chat.id in wheel_used: del wheel_used[message.chat.id]
        bot.send_message(message.chat.id, "✅ Сброшено")

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    chat_id = message.chat.id
    if chat_id in waiting:
        if str(waiting[chat_id]).startswith('WHEEL:'):
            item = waiting.pop(chat_id).replace('WHEEL:','')
            nick = message.text.strip()
            bot.send_message(chat_id, f"✅ {nick}\n🎁 {item}")
            bot.send_message(ADMIN_ID, f"🎰 {nick} — {item}")
        else:
            nick = message.text.strip()
            code = waiting.pop(chat_id)
            bot.send_message(chat_id, f"✅ {nick}\n🎁 {PROMOCODES[code]}")
            bot.send_message(ADMIN_ID, f"🎁 {code} | {nick} | {PROMOCODES[code]}")
        return
    msg_lower = message.text.lower().strip()
    if msg_lower in AUTO_REPLIES:
        bot.send_message(chat_id, AUTO_REPLIES[msg_lower])
        return
    bot.send_message(chat_id, "/start /shop /wheel /promo /help /report")

def run_bot():
    print("Bot started!")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
