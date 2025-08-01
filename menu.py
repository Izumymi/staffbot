import os
from telebot import types
from bot_instance import bot

def send_file(chat_id, filename, caption=None):
    file_path = os.path.join("files", filename)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            bot.send_document(chat_id, f, caption=caption or filename)
    else:
        bot.send_message(chat_id, f"❌ Файл {filename} не найден.")

def show_main_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👥 Кто мы", callback_data="menu_who"))
    markup.add(types.InlineKeyboardButton("🎤 Информация по VIP", callback_data="menu_vip"))
    markup.add(types.InlineKeyboardButton("🍽️ Информация о ресторане", callback_data="menu_restaurant"))
    markup.add(types.InlineKeyboardButton("📋 Меню", callback_data="menu_menu"))
    markup.add(types.InlineKeyboardButton("💼 Должностные обязанности", callback_data="menu_roles"))
    markup.add(types.InlineKeyboardButton("🎁 Система мотивации и бонусов", callback_data="menu_bonus"))
    markup.add(types.InlineKeyboardButton("📄 Для приёма на работу", callback_data="menu_job"))
    markup.add(types.InlineKeyboardButton("🧠 Ответы на частые вопросы ⁉️", callback_data="faq_main"))
    markup.add(types.InlineKeyboardButton("✉️ Обратная связь руководству", callback_data="feedback_start"))
    bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("menu_"))
def handle_menu_callbacks(call):
    if call.data == "menu_who":
        send_file(
            call.message.chat.id,
            "Welcom! We are Айша Биби_2025.pptx.pdf",
            "О нас: Welcom! We are Айша Биби"
        )
    elif call.data == "menu_vip":
        send_file(
            call.message.chat.id,
            "Информация по VIP (караоке залы).pdf",
            "Информация по VIP"
        )
    elif call.data == "menu_restaurant":
        send_file(
            call.message.chat.id,
            "Схема зала и террасы.pdf",
            "Схема зала и террасы"
        )
        send_file(
            call.message.chat.id,
            "информация по специальным предложениям.pdf",
            "Информация по специальным предложениям"
        )
    elif call.data == "menu_menu":
        # Отправляем ссылку на Google Drive вместо файла
        bot.send_message(
            call.message.chat.id,
            "Меню можно скачать по ссылке: https://drive.google.com/file/d/1h1s6YUczP6y0hjHSAo8ORvBwfQn_eLMI/view?pli=1"
        )
    elif call.data == "menu_roles":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🧑‍🍳 Официант", callback_data="role_waiter"))
        markup.add(types.InlineKeyboardButton("🍸 Бармен", callback_data="role_barman"))
        markup.add(types.InlineKeyboardButton("👠 Хостесс", callback_data="role_hostess"))
        bot.send_message(call.message.chat.id, "Выберите должность:", reply_markup=markup)
    elif call.data == "menu_bonus":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎁 Бонусы за VIP", callback_data="bonus_vip"))
        markup.add(types.InlineKeyboardButton("💸 Бонусы официанта", callback_data="bonus_waiter"))
        bot.send_message(call.message.chat.id, "🎁 Система мотивации и бонусов:", reply_markup=markup)
    elif call.data == "menu_job":
        send_file(
            call.message.chat.id,
            "Список документов.xlsx",
            "Список документов для приёма на работу"
        )

@bot.callback_query_handler(func=lambda c: c.data in [
    "role_waiter", "role_barman", "role_hostess", "bonus_vip", "bonus_waiter"
])
def handle_submenu_callbacks(call):
    if call.data == "role_waiter":
        send_file(call.message.chat.id, "waiter.pdf", "Стандарт официанта")
    elif call.data == "role_barman":
        send_file(call.message.chat.id, "Должностная инструкция бармен.pdf", "Должностная инструкция бармен")
    elif call.data == "role_hostess":
        send_file(call.message.chat.id, "hostess.pdf", "Стандарт хостесс")
    elif call.data == "bonus_vip":
        send_file(call.message.chat.id, "бонусы за вип.pdf", "Бонусы за VIP")
    elif call.data == "bonus_waiter":
        send_file(call.message.chat.id, "Бонусы официанта.pdf", "Бонусы официанта")