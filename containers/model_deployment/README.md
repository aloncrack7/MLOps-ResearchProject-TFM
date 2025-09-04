# MLflow Model Deployment Backend

A FastAPI-based backend service for dynamic deployment, management, and monitoring of MLflow models. This backend exposes a robust API for model lifecycle operations, integrates with MLflow, manages port allocation, and provides metrics, reporting, and dataset management for deployed models.

---

## 📁 Folder Structure

```
model_deployment/
├── Dockerfile           # Container build for backend service
├── entrypoint.sh        # Entrypoint script for container
├── requirements.txt     # Python dependencies
├── deployments.py       # Main FastAPI app and all backend logic
├── schema.sql           # SQLite schema for deployment state
├── type_mapping.json    # Type mapping for model signatures
```

---

## ✨ Main Features

- **Dynamic Model Deployment**: Deploy/undeploy MLflow models on demand
- **Automatic Port Management**: Allocates ports for each deployed model (8001-8100)
- **Model Registry Integration**: Lists models and versions from MLflow
- **API Endpoints**: RESTful endpoints for all operations (deploy, undeploy, list, call, metrics, etc.)
- **Metrics Management**: Track, update, and compare model metrics
- **Degradation Reports**: Generate and download model degradation reports
- **Dataset Management**: Download input datasets for any deployed model
- **Security**: Designed to work behind nginx with basic auth
- **Logging & Monitoring**: Logs all operations and integrates with monitoring tools

---

## 🛠️ Technology Stack

- **Python 3**
- **FastAPI** for REST API
- **MLflow** for model registry and serving
- **SQLite** for deployment state
- **MongoDB** for metrics and data storage
- **Docker** for containerization

---

## 🔍 How It Works

- **deployments.py**: Main FastAPI app. Handles all API endpoints, model deployment logic, port allocation, metrics, and reporting.
- **Dockerfile**: Builds the backend image, installs dependencies, sets up the environment.
- **entrypoint.sh**: Starts the FastAPI server in the container.
- **requirements.txt**: Lists all Python dependencies (FastAPI, MLflow, pymongo, etc.).
- **schema.sql**: Initializes SQLite DB for tracking deployed models and ports.
- **type_mapping.json**: Maps Python types to MLflow types for signature validation.

---

## 🚀 Development & Usage

### Prerequisites
- Python 3.8+
- Docker & Docker Compose

### Local Development

```bash
cd containers/model_deployment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn deployments:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

The backend is started as part of the main `docker compose up` process. To build and run individually:

```bash
docker compose build model_deployment
docker compose up model_deployment
```

---

## ⚡ API Endpoints

- `GET /get_model_list` - List available models
- `GET /get_model_version_list/{model}` - List versions for a model
- `POST /deploy/{model}/{version}` - Deploy a model version
- `GET /get_deployed_models` - List currently deployed models
- `POST /undeploy/{model-version}` - Undeploy a model
- `POST /{model}-{version}` - Call a deployed model
- `GET /model/{model}-{version}/metrics` - Get model metrics
- `POST /model/{model}-{version}/set_new_metrics` - Update metrics
- `GET /model/{model}-{version}/dataset` - Download dataset
- `GET /model/{model}-{version}/degradation_report` - Download degradation report

See the main project README and API docs for full details.

---

## 🔒 Security

- Designed to run behind nginx with basic authentication
- Models are isolated in separate processes
- Port allocation prevents conflicts

---

## 🩹 Troubleshooting

- **No free ports available**: Check for zombie MLflow processes, restart service, ensure ports 8001-8100 are free
- **Model not accessible**: Verify deployment, check logs, ensure correct model name-version
- **API errors**: Check container logs and dependencies

---

## 🤝 Contributing

Pull requests and issues are welcome!

---
