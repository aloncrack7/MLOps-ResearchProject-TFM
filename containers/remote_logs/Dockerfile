FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 \
                       python3-pip \
                       python3-venv \
                       sqlite3 \
                       cron \
                       wget

COPY . /app

WORKDIR /app

RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    sqlite3 users.db < schema.sql

RUN chmod +x handle_updates.sh && \
    crontab -l | { cat; echo "0 7 * * * /app/handle_updates.sh"; echo "5 7 * * 1 /app/venv/bin/python /app/handle_reports.py" } | crontab -

CMD ["/app/venv/bin/python3", "telegram_bot.py"]
