# PostgreSQL Database Container

This container provides the PostgreSQL database for the MLOps platform. It is used as the backend database for the MLflow tracking server, storing experiment metadata, model registry information, and other persistent data.

---

## 📁 Folder Structure

```
postgres/
├── make_backup.sh         # Script to create database backups
├── restore_backups.sh     # Script to restore database from backups
```

---

## ✨ Main Features

- **PostgreSQL Database**: Reliable, production-grade relational database
- **Persistent Storage**: Data is stored in Docker volumes for durability
- **Backup & Restore**: Scripts provided for easy backup and restore of the database
- **Integration**: Used by MLflow tracking server for experiment and model registry data

---

## 🛠️ Technology Stack

- **PostgreSQL** (official Docker image)
- **Bash** scripts for backup/restore
- **Docker** for containerization

---

## 🔍 How It Works

- The container runs the official PostgreSQL image
- Database data is stored in a Docker volume for persistence
- `make_backup.sh` can be used to create a backup of the database
- `restore_backups.sh` can be used to restore the database from a backup file
- Environment variables (set in `docker-compose.yaml`) configure the database name, user, and password

---

## 🚀 Usage

This container is started as part of the main `docker compose up` process. It is automatically configured and used by the MLflow tracking server.

### Standalone Build/Run

```bash
cd containers/postgres
docker build -t mlflow-postgres .
docker run -e POSTGRES_DB=mlflow -e POSTGRES_USER=mlflow -e POSTGRES_PASSWORD=mlflow -p 5432:5432 mlflow-postgres
```

---

## ⚙️ Configuration

- **Port**: Listens on port 5432 (default PostgreSQL port)
- **Database Name/User/Password**: Set via environment variables
- **Data Volume**: Data is persisted in a Docker volume

---

## 🩹 Troubleshooting

- **Database not starting**: Check logs for errors, ensure no port conflicts
- **Connection issues**: Verify credentials and network settings
- **Backup/restore issues**: Ensure scripts have execute permissions and correct paths

---

## 🤝 Contributing

Pull requests and issues are welcome!

---
