# MLOps-ResearchProject-TFM

An end-to-end MLOps platform for dynamic MLflow model deployment, monitoring, and management. This project upgrades the [TFG](https://oa.upm.es/74985/) to MLOps Level 2, providing a production-ready, containerized solution for model lifecycle automation.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white)
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Bash Script](https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)
![mlflow](https://img.shields.io/badge/mlflow-%23d9ead3.svg?style=for-the-badge&logo=numpy&logoColor=blue)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=for-the-badge&logo=kaggle&logoColor=white)

[![DOI](https://zenodo.org/badge/816219393.svg)](https://doi.org/10.5281/zenodo.17055907)

---

## 🚀 Overview

This system enables:
- **Dynamic deployment** of MLflow models with automatic port allocation
- **Centralized control panel** (React frontend) for model management
- **Metrics tracking, monitoring, and reporting**
- **API-first architecture** for integration and automation

---

## 🏗️ Architecture

**Main components:**
- **Frontend**: React dashboard for model management and monitoring
- **Model Deployment Service**: FastAPI backend for deploying, undeploying, and proxying models
- **MLflow Tracking Server**: Model registry and artifact store
- **Databases**: PostgreSQL (MLflow), MongoDB (metrics/data)
- **Nginx**: API gateway, authentication, and routing

```
User → Nginx → Model Deployment API → MLflow/Deployed Models
```

---

## ✨ Features

- Deploy/undeploy MLflow models on demand
- Automatic port management (8001-8100)
- Model versioning and registry integration
- Real-time metrics and health monitoring
- Download datasets and compare model metrics
- Secure access via nginx basic auth
- Responsive, modern UI

---

## ⚡ Quick Start

### Prerequisites
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [AWS account for S3](https://console.aws.amazon.com/s3/home) recomended, [GCP account for HDFS](https://console.cloud.google.com/dataproc) or having a local instance of HDFS.
- Two telegram bots.

### Installation
Clone the repo and run:

```bash
./install.sh
```

Once installed you could run with:

```bash
docker compose up -d
```

The system will be available at `http://localhost` (see nginx config for details).

---

## 🖥️ Usage

### Web UI
1. Go to `http://localhost` (or your configured domain)
2. Log in with your credentials (nginx basic auth)
3. Use the dashboard to:
	- View available models
	- Deploy/undeploy models
	- Monitor deployed models and metrics
	- Download datasets

### API Endpoints (examples)

- **List models:** `GET /get_model_list`
- **Deploy model:** `POST /deploy/{model}/{version}`
- **List deployed models:** `GET /get_deployed_models`
- **Undeploy model:** `POST /undeploy/{model-version}`
- **Call model:** `POST /{model}-{version}`

See `MODEL_DEPLOYMENT_README.md` for full API docs and usage examples.

---

## 📁 Directory Structure

- `containers/frontend/` – React app (dashboard)
- `containers/model_deployment/` – FastAPI backend for deployment
- `containers/mlflow/` – MLflow tracking server
- `containers/mongodb/` – MongoDB init scripts
- `nginx/` – Nginx config for routing/auth
- `examples/` – Example training scripts and notebooks
- `compose.yaml` – Docker Compose setup

---

## 🛠️ Development

### [Frontend](https://github.com/aloncrack7/MLOps-ResearchProject-TFM/blob/main/containers/frontend/README.md)
### [Backend](https://github.com/aloncrack7/MLOps-ResearchProject-TFM/blob/main/containers/model_deployment/README.md)
### [NGINX](https://github.com/aloncrack7/MLOps-ResearchProject-TFM/blob/main/containers/nginx/README.md)
### [mlflow](https://github.com/aloncrack7/MLOps-ResearchProject-TFM/blob/main/containers/mlflow/README.md)
### [MongoDB](https://github.com/aloncrack7/MLOps-ResearchProject-TFM/blob/main/containers/mongodb/README.md)
### [Postgres](https://github.com/aloncrack7/MLOps-ResearchProject-TFM/blob/main/containers/postgres/README.md)
### [Remote logs](https://github.com/aloncrack7/MLOps-ResearchProject-TFM/blob/main/containers/remote_logs/README.md)

---

## 🩹 Troubleshooting

- **Model not accessible**: Verify deployment, check logs, ensure correct model name-version
- **Frontend/API errors**: Check container logs, nginx config, and authentication

---

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue to discuss major changes.

---

## 📄 License

MIT License

---

## 📬 Contact

For questions or support, open an issue or contact the maintainer.
