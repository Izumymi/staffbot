from bot_instance import bot
from telebot import types
import os
import json
import menu   # Импортируй модуль меню
import time   # <<< добавлено

# Администраторы
ADMIN_IDS = [6220140788, 528238909]

# Файлы
APPROVED_FILE = "approved.txt"
REQUESTS_FILE = "requests.txt"
USERS_FILE = "users.json"

user_states = {}

def get_approved_users():
    if not os.path.exists(APPROVED_FILE):
        return []
    with open(APPROVED_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def approve_user(user_id):
    approved = get_approved_users()
    if str(user_id) not in [line.split(":", 1)[0] for line in approved]:
        users = load_users()
        name = users.get(str(user_id), {}).get("name", "Без имени")
        surname = users.get(str(user_id), {}).get("surname", "")
        full_name = f"{name} {surname}".strip()

        with open(APPROVED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}:{full_name}\n")
        return True
    return False

def remove_request(user_id):
    if not os.path.exists(REQUESTS_FILE):
        return
    with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if not line.startswith(f"{user_id}:"):
                f.write(line)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    users = load_users()
    if str(user_id) in users:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚪 Войти", callback_data="enter"))
        bot.send_message(user_id, "Ты уже зарегистрирован. Нажми, чтобы войти:", reply_markup=markup)
        return

    user_states[user_id] = {"step": "ask_name"}
    bot.send_message(user_id, "Привет! Для начала введи, пожалуйста, своё имя:")

@bot.message_handler(commands=['requests'])
def show_requests(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 У тебя нет прав.")
        return

    if not os.path.exists(REQUESTS_FILE):
        bot.reply_to(message, "❌ Пока никто не подал заявку.")
        return

    with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        bot.reply_to(message, "❌ Список заявок пуст.")
        return

    for line in lines:
        try:
            user_id, info = line.split(":", 1)
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{user_id}"),
                types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
            )
            bot.send_message(message.chat.id, f"Заявка от {info.strip()}", reply_markup=markup)
        except:
            continue

@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_") or c.data.startswith("reject_"))
def handle_approval_rejection(call):
    admin_id = call.from_user.id
    if admin_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "🚫 У тебя нет прав.")
        return

    action, user_id = call.data.split("_", 1)

    if action == "approve":
        approve_user(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚪 Войти", callback_data="enter"))
        bot.send_message(int(user_id), "🎉 Ты одобрен! Нажми кнопку ниже, чтобы войти:", reply_markup=markup)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    elif action == "reject":
        bot.send_message(int(user_id), "❌ К сожалению, твоя заявка была отклонена.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    remove_request(user_id)

@bot.callback_query_handler(func=lambda c: c.data in ["confirm", "edit", "enter", "start_training"])
def callback_handler(call):
    user_id = call.from_user.id
    users = load_users()

    if call.data == "confirm":
        data = users.get(str(user_id), {})
        name = data.get("name", "")
        surname = data.get("surname", "")
        phone = data.get("phone", "")

        already_exists = False
        if os.path.exists(REQUESTS_FILE):
            with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if str(user_id) in line:
                        already_exists = True
                        break

        if not already_exists:
            with open(REQUESTS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{user_id}: {name} {surname} | {phone}\n")

        bot.send_message(user_id, "✅ Отлично! Ожидай одобрения администратора.")

    elif call.data == "edit":
        user_states[user_id] = {"step": "ask_name"}
        bot.send_message(user_id, "Окей, давай начнём заново. Введи имя:")

    elif call.data == "enter":
        if str(user_id) in get_approved_users():
            menu.show_main_menu(call.message)
        else:
            bot.send_message(user_id, "⏳ Ты ещё не одобрен.")

    elif call.data == "start_training":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🍳 Кухня", callback_data="job_кухня"),
            types.InlineKeyboardButton("🪑 Зал", callback_data="job_зал")
        )
        markup.add(
            types.InlineKeyboardButton("🍹 Бар", callback_data="job_бар"),
            types.InlineKeyboardButton("👠 Hostess", callback_data="job_hostess")
        )
        bot.send_message(user_id, "Выбери, где ты работаешь:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("job_"))
def handle_job_selection(call):
    user_id = str(call.from_user.id)
    if user_id not in get_approved_users():
        bot.answer_callback_query(call.id, "🚫 Ты не одобрен.")
        return

    job_map = {
        "кухня": "chef.pdf",
        "бар": "barman.pdf",
        "зал": "waiter.pdf",
        "hostess": "hostess.pdf"
    }

    job_code = call.data.replace("job_", "")
    file_name = job_map.get(job_code)

    if not file_name:
        bot.send_message(call.message.chat.id, "❌ Неизвестная роль.")
        return

    file_path = os.path.join("files", file_name)
    if not os.path.exists(file_path):
        bot.send_message(call.message.chat.id, "❌ Файл не найден.")
        return

    bot.send_message(call.message.chat.id, f"📂 Загружаю файл: {file_name}")
    with open(file_path, "rb") as f:
        bot.send_document(call.message.chat.id, f, caption=file_name)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# =======================
# Ответы на частые вопросы
# =======================
@bot.callback_query_handler(func=lambda c: c.data == "faq_main")
def show_faq_sections(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🍽 Выход блюд", callback_data="faq_dishes"))
    markup.add(types.InlineKeyboardButton("🍕 Советовать гостям (еда)", callback_data="faq_food"))
    markup.add(types.InlineKeyboardButton("🍷 Советовать гостям (напитки)", callback_data="faq_drinks"))
    markup.add(types.InlineKeyboardButton("🍳 Завтраки", callback_data="faq_breakfast"))
    markup.add(types.InlineKeyboardButton("💸 Зарплата и бонусы", callback_data="faq_salary"))
    markup.add(types.InlineKeyboardButton("🚬 Курение и сигареты", callback_data="faq_smoke"))

    bot.send_message(
        call.message.chat.id,
        "🧠 *Ответы на частые вопросы ⁉️*\n\nВыбери раздел:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("faq_"))
def faq_callback(call):
    answers = {
        "faq_dishes": (
            "🍽 *Выход блюд*\n\n"
            "— Шашлык: 250 г\n"
            "— Салат: 250–280 г\n"
            "— Закуски: 200–300 г"
        ),
        "faq_food": (
            "🍕 *Что советовать гостям (еда)*\n\n"
            "— К пиву: караси, эдамаме, гренки\n"
            "— К вину: сырная, фруктовая, стейки\n"
            "— На компанию: плов, мясной сет\n"
            "— Детям: фрикадельки, пицца, пельмени"
        ),
        "faq_drinks": (
            "🍷 *Что советовать гостям (напитки)*\n\n"
            "— Крепкий алкоголь: Tenjaku (виски), Lex (водка)\n"
            "— Коктейли: Whiskey Sour, Aperol Spritz, Negroni\n"
            "— Вино: San Valentin, Canti (белое и красное)"
        ),
        "faq_breakfast": (
            "🍳 *Завтраки*\n\n"
            "— Будни: 07:00–10:30\n"
            "— Выходные: 08:00–11:00 + шоколадный фонтан\n"
            "— Цена: взрослый — 8 000 тг, детский — 6 000 тг"
        ),
        "faq_salary": (
            "💸 *Зарплата и бонусы*\n\n"
            "— Зарплата: до 10 числа\n"
            "— Аванс: до 15 числа\n"
            "— % и бонусы: с 20 по 25 число"
        ),
        "faq_smoke": (
            "🚬 *Сигареты и курение*\n\n"
            "— Мы не продаём сигареты. Ближайший магазин — ЖК Liberty (Market)\n"
            "— На террасе: сигареты — нельзя, электронки — можно\n"
            "— Кальянов нет (запрещены законом РК)"
        ),
    }

    text = answers.get(call.data, "Неизвестный раздел")
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# =======================
# Обратная связь руководству
# =======================
feedback_states = {}

@bot.callback_query_handler(func=lambda c: c.data == "feedback_start")
def feedback_start(call):
    user_id = call.from_user.id
    feedback_states[user_id] = True
    bot.send_message(user_id, "✏️ Напиши своё сообщение для руководства. Оно будет отправлено вместе с твоим именем и ID.")
    bot.answer_callback_query(call.id)

def send_feedback_to_admins(user, text):
    for admin_id in ADMIN_IDS:
        bot.send_message(
            admin_id,
            f"📩 *Новое сообщение от сотрудника*\n\n"
            f"Имя: {user.first_name} {user.last_name or ''}\n"
            f"ID: `{user.id}`\n\n"
            f"Сообщение:\n{text}",
            parse_mode="Markdown"
        )

# =======================
# ТЕСТ (опрос с вариантами)
# =======================
quiz_questions = [
    {"text": "Как оцениваете обстановку?", "options": ["Отлично", "Хорошо", "Плохо"]},
    {"text": "Как вам еда?", "options": ["Очень вкусно", "Нормально", "Не понравилось"]},
    {"text": "Рекомендуете нас друзьям?", "options": ["Да", "Нет"]}
]

quiz_state = {}

@bot.message_handler(commands=['test'])
def start_quiz(message):
    user_id = message.from_user.id
    quiz_state[user_id] = {"index": 0, "answers": [], "start_time": time.time()}
    send_quiz_question(user_id)

def send_quiz_question(user_id):
    state = quiz_state[user_id]
    idx = state["index"]

    if idx >= len(quiz_questions):
        duration = int(time.time() - state.get("start_time", time.time()))
        minutes = duration // 60
        seconds = duration % 60

        results = "\n".join(
            f"{quiz_questions[i]['text']} — {ans}"
            for i, ans in enumerate(state["answers"])
        )
        users = load_users()
        user_info = users.get(str(user_id), {})
        full_name = (user_info.get("name", "") + " " + user_info.get("surname", "")).strip()
        if not full_name:
            full_name = "Без имени"

        for admin_id in ADMIN_IDS:
            bot.send_message(
                admin_id,
                f"📝 Новый тест от {full_name} (ID {user_id}):\n\n"
                f"{results}\n\n"
                f"⏱ Время прохождения: {minutes} мин {seconds} сек"
            )

        bot.send_message(
            user_id,
            f"Спасибо! Ваши ответы отправлены.\n"
            f"⏱ Ты прошёл тест за {minutes} мин {seconds} сек"
        )

        del quiz_state[user_id]
        return

    q = quiz_questions[idx]
    markup = types.InlineKeyboardMarkup()
    for option in q["options"]:
        markup.add(types.InlineKeyboardButton(option, callback_data=f"quiz_{option}"))
    bot.send_message(user_id, q["text"], reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("quiz_"))
def handle_quiz_answer(call):
    user_id = call.from_user.id
    if user_id not in quiz_state:
        bot.answer_callback_query(call.id, "Тест не запущен. Напишите /test")
        return

    answer = call.data.replace("quiz_", "")
    state = quiz_state[user_id]
    state["answers"].append(answer)
    state["index"] += 1

    bot.answer_callback_query(call.id, "Ответ записан")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    send_quiz_question(user_id)

# =======================
# ОБРАБОТЧИК ВСЕХ СООБЩЕНИЙ (ПОСЛЕДНИЙ!)
# =======================
@bot.message_handler(func=lambda msg: True)
def all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text.startswith("/"):
        return

    state = user_states.get(user_id, {})

    if feedback_states.get(user_id):
        feedback_states.pop(user_id)
        send_feedback_to_admins(message.from_user, text)
        bot.send_message(user_id, "✅ Спасибо! Сообщение отправлено руководству.")
        return

    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {}

    if state.get("step") == "ask_name":
        users[str(user_id)]["name"] = text
        user_states[user_id]["step"] = "ask_surname"
        save_users(users)
        bot.send_message(user_id, "Теперь введи свою фамилию:")

    elif state.get("step") == "ask_surname":
        users[str(user_id)]["surname"] = text
        user_states[user_id]["step"] = "ask_phone"
        save_users(users)
        bot.send_message(user_id, "Теперь введи номер телефона (в формате +7...):")

    elif state.get("step") == "ask_phone":
        users[str(user_id)]["phone"] = text
        save_users(users)
        user_data = users[str(user_id)]
        summary = (f"Проверь, всё ли правильно:\n\n"
                   f"Имя: {user_data['name']}\n"
                   f"Фамилия: {user_data['surname']}\n"
                   f"Телефон: {user_data['phone']}")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Всё верно", callback_data="confirm"),
                   types.InlineKeyboardButton("🔄 Изменить", callback_data="edit"))
        bot.send_message(user_id, summary, reply_markup=markup)

    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚪 Войти", callback_data="enter"))
        bot.send_message(user_id, "Нажми кнопку ниже, чтобы войти:", reply_markup=markup)

bot.polling()
