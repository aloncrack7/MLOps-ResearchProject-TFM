import sqlite3
from telegram import Bot
import os
from dotenv import load_dotenv 
from contextlib import closing
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def send_message_to_subscribers_backups(message):
    load_dotenv("./remote_logs.env")

    bot = Bot(os.getenv("TELEGRAM_TOKEN_BACKUP_NOTIFICATIONS"))
    with closing(sqlite3.connect("./users.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT users.user_id 
                            FROM users, services, subcriptions
                            WHERE users.id=subcriptions.user_id and services.id=subcriptions.service_id
                                and service_name="backup" and subcriptions.uses_telegram
                       """)
        for (user_id,) in cursor:
            try:
                await bot.send_message(chat_id=user_id, text=message)
            except Exception as e:
                print(f"Failed to send to {user_id}: {e}")

        cursor.execute("""SELECT users.email_address 
                            FROM users, services, subcriptions
                            WHERE users.id=subcriptions.user_id and services.id=subcriptions.service_id
                                and service_name="backup" and subcriptions.uses_email
                       """)
        
        for (email_address,) in cursor:
            msg = MIMEMultipart()
            msg["From"] = os.getenv("EMAIL_SENDER_ADDRESS")
            msg["To"] = email_address
            msg["Subject"] = "mlflow backup notification system"
            msg.attach(MIMEText(message, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(msg["From"], os.getenv("EMAIL_SENDER_TOEKN"))
                server.sendmail(msg["From"], msg["To"], msg.as_string())

if __name__ == "__main__":
    import sys

    print("Sending message to subscribers of backups...")
    if len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
        asyncio.run(send_message_to_subscribers_backups(message))  
    else:
        print("Usage: python send_logs.py <message>")
