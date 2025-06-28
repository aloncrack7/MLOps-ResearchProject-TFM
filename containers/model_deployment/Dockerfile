FROM ubuntu:latest

# Install python3 and pip and other dependencies
RUN apt-get update && \
    apt-get install -y python3 \
                       python3-pip \
                       python3-venv \
                       sqlite3 \
                       nmap

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt

COPY schema.sql /app/schema.sql
RUN sqlite3 /app/model_deployment.db < schema.sql

RUN python3 -m venv venv
RUN . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt