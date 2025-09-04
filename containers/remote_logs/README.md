# Remote Logs & Monitoring Container

This container provides remote logging, monitoring, and reporting services for the MLOps platform. It collects, processes, and stores logs and metrics from deployed models, and can send notifications or reports to external systems (e.g., Telegram, monitoring dashboards).

---

## 📁 Folder Structure

```
remote_logs/
├── Dockerfile            # Builds the remote logs service container
├── handle_reports.py     # Handles incoming and scheduled report generation
├── handle_updates.sh     # Shell script for update automation
├── requirements.txt      # Python dependencies
├── schema.sql            # Database schema for logs/metrics
├── search_updates.py     # Script to search for updates in logs/metrics
├── send_logs.py          # Script to send logs to external systems
├── telegram_bot.py       # Telegram bot integration for notifications
├── versions.csv          # Tracks versions of deployed components
```

---

## ✨ Main Features

- **Log Collection**: Receives and stores logs from deployed models and services
- **Metrics Storage**: Persists metrics and reports for later analysis
- **Automated Reporting**: Generates and sends reports on model performance, drift, or errors
- **Update Monitoring**: Detects and notifies about new model or system updates
- **Telegram Integration**: Sends alerts and reports to Telegram channels or users
- **Scriptable**: Includes scripts for searching, sending, and handling logs/updates

---

## 🛠️ Technology Stack

- **Python 3**
- **SQLite** for local storage
- **Shell scripts** for automation
- **Docker** for containerization

---

## 🔍 How It Works

- **handle_reports.py**: Main script for generating and processing reports
- **send_logs.py**: Sends logs to external systems (e.g., via HTTP, Telegram)
- **telegram_bot.py**: Listens for commands and sends notifications via Telegram
- **search_updates.py**: Searches logs/metrics for updates or anomalies
- **handle_updates.sh**: Automates update checks and notifications
- **schema.sql**: Defines the SQLite schema for storing logs and metrics
- **versions.csv**: Tracks component versions for update monitoring

---

## 🚀 Usage

This container is started as part of the main `docker compose up` process. It is automatically configured to receive logs and send notifications.

### Standalone Build/Run

```bash
cd containers/remote_logs
docker build -t mlflow-remote-logs .
docker run mlflow-remote-logs
```

---

## ⚙️ Configuration

- **Database**: Uses SQLite for local storage (can be extended)
- **Telegram**: Configure bot token and chat IDs in environment variables or config files
- **Log Sources**: Other containers/services must be configured to send logs to this service

---

## 🩹 Troubleshooting

- **Logs not received**: Check network settings and log source configuration
- **Telegram alerts not sent**: Verify bot token and chat ID
- **Database issues**: Ensure SQLite file is writable and schema is initialized

---

## 🤝 Contributing

Pull requests and issues are welcome!

---
