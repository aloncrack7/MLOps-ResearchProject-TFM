FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 \
                       python3-pip \
                       python3-venv \
                       sqlite3

COPY . /app

WORKDIR /app

RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    sqlite3 users.db < schema.sql

CMD ["./venv/bin/python", "telegram_bot.py"]