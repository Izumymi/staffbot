import telebot
from dotenv import load_dotenv
import os

load_dotenv()  # Должно быть ДО os.getenv!
TOKEN = os.getenv("BOT_TOKEN")  # После load_dotenv
if not TOKEN:
    raise RuntimeError("BOT_TOKEN не найден! Проверь файл .env")

bot = telebot.TeleBot(TOKEN)