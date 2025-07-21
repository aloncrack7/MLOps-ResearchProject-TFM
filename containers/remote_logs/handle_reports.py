import sys
import sqlite3
from telegram import Bot
import os
from dotenv import load_dotenv 
from contextlib import closing
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import io


async def send_message_to_subscribers(zip_content, service_name):
    load_dotenv("./remote_logs.env")
    bot = Bot(os.getenv("TELEGRAM_TOKEN_NOTIFICATIONS"))
    
    # Create a file-like object from zip content
    zip_file = io.BytesIO(zip_content)
    zip_file.name = f"{service_name}_report.zip"
    
    with closing(sqlite3.connect("./users.db")) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT users.user_id 
                            FROM users, services, subcriptions
                            WHERE users.id=subcriptions.user_id and services.id=subcriptions.service_id
                                and service_name=? and subcriptions.uses_telegram
                       """, (service_name,))
        for (user_id,) in cursor:
            try:
                await bot.send_document(chat_id=user_id, document=zip_file, caption=f"Degradation report for {service_name}")
                zip_file.seek(0)  # Reset file pointer for next send
            except Exception as e:
                print(f"Failed to send to {user_id}: {e}")

        cursor.execute("""SELECT users.email_address 
                            FROM users, services, subcriptions
                            WHERE users.id=subcriptions.user_id and services.id=subcriptions.service_id
                                and service_name=? and subcriptions.uses_email
                       """, (service_name,))
        for (email_address,) in cursor:
            msg = MIMEMultipart()
            msg["From"] = os.getenv("EMAIL_SENDER_ADDRESS")
            msg["To"] = email_address
            msg["Subject"] = "MLflow Degradation Report"
            msg.attach(MIMEText(f"Please find attached the degradation report for {service_name}", "plain"))

            # Attach zip file
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(zip_content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{service_name}_report.zip"')
            msg.attach(part)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(msg["From"], os.getenv("EMAIL_SENDER_TOKEN"))
                    server.sendmail(msg["From"], msg["To"], msg.as_string())
            except Exception as e:
                print(f"Failed to send email to {email_address}: {e}")

if __name__ == "__main__":
    response = requests.get("http://model_deployment:8000/get_deployed_models")

    models = []
    if response.status_code == 200:
        data = response.json()
        for key, model_info in data.items():
            model_name = model_info["model_name"]
            version = model_info["version"]
            models.append((model_name, version))    
    else:
        print(response.text)
        sys.exit(1)

    if not models:
        print("No deployed models found.")
        sys.exit(0)

    for model_name, version in models:
        zip_response = requests.get(f"http://model_deployment:8000//model/{model_name}-{version}/degradation_report")
        if zip_response.status_code == 200:
            asyncio.run(send_message_to_subscribers(zip_response.content, f"degradation_report_{model_name}_{version}"))
        else:
            print(f"Failed to get report for {model_name} v{version}")