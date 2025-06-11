from dotenv import load_dotenv
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
import sqlite3
from contextlib import closing

load_dotenv("remote_logs.env")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    filename="../logs/telegram_bot.log",
    filemode="a",  # Append to the log file
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def _subscribe(user):
    with closing(sqlite3.connect("users.db")) as conn:
        with conn:
            conn.execute("INSERT INTO users (user_id) VALUES (?)", (user,))

def _unsubscribe(user):
    with closing(sqlite3.connect("users.db")) as conn:
        with conn:
            conn.execute("DELETE FROM users WHERE user_id=(?)", (user,))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Yes, I would like to subscribe ✅", callback_data='subscribe')],
        [InlineKeyboardButton("No, thank you ❌", callback_data='no_subscribe')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user
    await update.message.reply_html(
        rf"Greetings, {user.mention_html()}!\nWould you like to subscribe to mlflow notifications?",
        reply_markup=reply_markup,
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'subscribe':
        user_id = query.from_user.id
        _subscribe(user_id)
        await query.edit_message_text("Perfect! You are subscribed to the notifications. 📬\nYou can unsubscribe by using /unsubscribe.")
    elif query.data == 'no_subscribe':
        await query.edit_message_text("No problem. You can subscribe by using /subscribe. 👍")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Command list:*\n"
        "/start - Start the bot\n"
        "/subscribe - Subscribe to notifications\n"
        "/unsubscribe - Cancel subscription\n"
        "/help - Show this help",
        parse_mode="Markdown"
    )

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    _subscribe(user_id)
    await update.message.reply_text(f"✅ You have subscribed successfully.\nTalk to @{os.getenv("TELEGRAM_BACKUP_NOTIFICATIONS_ID")}")

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    _unsubscribe(user_id)
    await update.message.reply_text("❎ You have unsubscribed successfully.")

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running")
    app.run_polling()

if __name__=="__main__":
    main()