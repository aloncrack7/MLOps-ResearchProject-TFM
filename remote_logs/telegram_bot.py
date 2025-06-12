from dotenv import load_dotenv
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
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
    filemode="a",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# In-memory user state (for the quiz)
user_states = {}

def _subscribe(user_telegram_id, email_address, service_name, uses_telegram, uses_email):
    with closing(sqlite3.connect("users.db")) as conn:
        with conn:
            # 1. Insert user if not exists
            conn.execute("""
                INSERT OR IGNORE INTO users (user_id, email_adress)
                VALUES (?, ?)
            """, (user_telegram_id, email_address))

            # 2. Get user internal id
            user_row = conn.execute("""
                SELECT id FROM users WHERE user_id = ?
            """, (user_telegram_id,)).fetchone()
            if not user_row:
                raise ValueError("User not found after insert.")
            user_id = user_row[0]

            # 3. Get service_id
            service_row = conn.execute("""
                SELECT id FROM services WHERE service_name = ?
            """, (service_name,)).fetchone()
            if not service_row:
                raise ValueError("Service not found after insert.")
            service_id = service_row[0]

            (status_row) = conn.execute(f"""
                SELECT user_id, service_id 
                FROM subcriptions
                WHERE user_id=? AND service_id=?
            """, (user_id, service_id)).fetchone()
            if status_row is not None:
                uses_telegram = status_row[0] if uses_telegram==0 else uses_telegram
                uses_email = status_row[1] if uses_email==0 else uses_email

            # 4. Insert or update subscription
            conn.execute("""
                INSERT INTO subcriptions (user_id, service_id, uses_telegram, uses_email)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, service_id) DO UPDATE SET
                    uses_telegram=excluded.uses_telegram,
                    uses_email=excluded.uses_email
            """, (user_id, service_id, uses_telegram, uses_email))


def _unsubscribe(user_telegram_id, service_name, unsubscribe_telegram=False, unsubscribe_email=False):
    with closing(sqlite3.connect("users.db")) as conn:
        with conn:
            # 1. Get user ID
            user_row = conn.execute("""
                SELECT id FROM users WHERE user_id = ?
            """, (user_telegram_id,)).fetchone()
            if not user_row:
                raise ValueError("User does not exist.")
            user_id = user_row[0]

            # 2. Get service ID
            service_row = conn.execute("""
                SELECT id FROM services WHERE service_name = ?
            """, (service_name,)).fetchone()
            if not service_row:
                raise ValueError("Service does not exist.")
            service_id = service_row[0]

            # 3. Build update query depending on what the user wants to unsubscribe from
            status_row = conn.execute(f"""
                SELECT user_id, service_id 
                FROM subcriptions
                WHERE user_id=? AND service_id=?
            """, (user_id, service_id)).fetchone()
            if not status_row:
                raise ValueError("The user is not subcribed to this service.")
            status = status_row[0]

            unsubscribe_telegram_val = 1 if not unsubscribe_telegram and status[0]==1 else 0
            unsubscribe_email_val = 1 if not unsubscribe_email and status[1]==1 else 0

            conn.execute(f"""
                UPDATE subcriptions
                SET uses_telegram= ?, uses_email= ?
                WHERE user_id = ? AND service_id = ?
            """, (unsubscribe_telegram_val, unsubscribe_email_val, user_id, service_id))

            return True

# Quiz step 1
async def ask_subscription_class(update_or_query, user_id):
    user_states[user_id] = {}  # Reset/init state

    keyboard = [
        [InlineKeyboardButton("Backup", callback_data='class_backup')],
        # Add more options as needed
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if isinstance(update_or_query, Update) and update_or_query.message:
        await update_or_query.message.reply_text(
            "📦 What service do you want to subscribe to?",
            reply_markup=reply_markup
        )
    else:
        await update_or_query.edit_message_text(
            "📦 What service do you want to subscribe to?",
            reply_markup=reply_markup
        )

# Telegram bot commands
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
    await update.message.reply_text(
        "Let's set up your subscription. Select a service:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Backup", callback_data='quiz_service_Backup')]
        ])
    )

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Select the service you want to unsubscribe from:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Backup", callback_data='unsub_service_Backup')]
        ])
    )

# Button interactions (for inline keyboards)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == 'no_subscribe':
        await query.edit_message_text("No worries! You can subscribe any time using /subscribe.")
        return

    if data == 'quiz_start':
        await query.edit_message_text(
            "Which service do you want to subscribe to?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Backup", callback_data='quiz_service_Backup')],
            ])
        )
        return

    if data.startswith('quiz_service_'):
        service = data.replace('quiz_service_', '')
        context.user_data['service'] = service
        await query.edit_message_text(
            f"Selected service: {service}\n\nWhich platform(s) do you want to use?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Telegram", callback_data='quiz_platform_telegram')],
                [InlineKeyboardButton("Email", callback_data='quiz_platform_email')],
                [InlineKeyboardButton("Both", callback_data='quiz_platform_both')]
            ])
        )
        return

    if data.startswith('quiz_platform_'):
        platform = data.replace('quiz_platform_', '')
        service = context.user_data.get('service').lower()

        uses_telegram = 1 if platform in ['telegram', 'both'] else 0
        uses_email = 1 if platform in ['email', 'both'] else 0

        _subscribe(user_id, None, service, uses_telegram, uses_email)
        await query.edit_message_text(
            f"✅ Subscribed to *{service}* via *{platform}*.",
            parse_mode="Markdown"
        )
        return

    # Unsubscribe flow
    if data.startswith('unsub_service_'):
        service = data.replace('unsub_service_', '')
        context.user_data['unsub_service'] = service
        await query.edit_message_text(
            f"Unsubscribe from *{service}*. Select method(s):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Telegram", callback_data='unsub_platform_telegram')],
                [InlineKeyboardButton("Email", callback_data='unsub_platform_email')],
                [InlineKeyboardButton("Both", callback_data='unsub_platform_both')]
            ]),
            parse_mode="Markdown"
        )
        return

    if data.startswith('unsub_platform_'):
        platform = data.replace('unsub_platform_', '')
        service = context.user_data.get('unsub_service').lower()

        unsubscribe_telegram = platform in ['telegram', 'both']
        unsubscribe_email = platform in ['email', 'both']

        success = _unsubscribe(user_id, service, unsubscribe_telegram, unsubscribe_email)

        if success:
            await query.edit_message_text(
                f"✅ Unsubscribed from *{service}* via *{platform}*.",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ Could not find your subscription to update.")
        return

# Main entrypoint
def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running")
    app.run_polling()

if __name__ == "__main__":
    main()
