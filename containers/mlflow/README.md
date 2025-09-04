# MLflow Tracking Server Container

This container provides the MLflow tracking server for the MLOps platform. It manages the model registry, experiment tracking, artifact storage, and serves as the central hub for all model lifecycle metadata.

---

## 📁 Folder Structure

```
mlflow/
├── Dockerfile         # Builds the MLflow server container
├── entrypoint.sh      # Entrypoint script to start MLflow
```

---

## ✨ Main Features

- **MLflow Tracking Server**: Centralized experiment and model registry
- **Model Registry**: Stores and manages all registered models and versions
- **Artifact Store**: Persists model artifacts, datasets, and logs
- **API Access**: Exposes MLflow REST API for programmatic access
- **Conda Environment**: Runs in an isolated conda environment for reproducibility
- **Database Integration**: Supports PostgreSQL for tracking and registry
- **S3/Local Storage**: Configurable artifact storage backend

---

## 🛠️ Technology Stack

- **MLflow** (Python)
- **Miniconda** for environment management
- **Ubuntu** base image
- **Docker** for containerization

---

## 🔍 How It Works

- **Dockerfile**: Installs Python, MLflow, and all dependencies. Sets up conda environment and configures the server.
- **entrypoint.sh**: Starts the MLflow server with the correct backend and artifact store settings.
- **Environment Variables**: Used to configure database, artifact store, and MLflow options.

---

## 🚀 Usage

This container is started as part of the main `docker compose up` process. It expects the database and artifact store to be available at the configured hostnames.

### Standalone Build/Run

```bash
cd containers/mlflow
docker build -t mlflow-server .
docker run -p 5000:5000 mlflow-server
```

---

## ⚙️ Configuration

- **Port**: Listens on port 5000 (default MLflow server port)
- **Database**: Set via environment variables (e.g., `MLFLOW_TRACKING_URI`)
- **Artifact Store**: Set via environment variables (e.g., S3, local path)
- **Conda Environment**: Created and activated for MLflow
- **User**: Runs as a non-root user for security

---

## 🩹 Troubleshooting

- **Server not starting**: Check logs for dependency or database errors
- **Artifacts not saving**: Verify artifact store configuration and permissions
- **Database issues**: Ensure the database is running and accessible
- **Port conflicts**: Make sure port 5000 is not in use

---

## 🤝 Contributing

Pull requests and issues are welcome!

---
