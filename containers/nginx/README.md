# Nginx Gateway for MLflow Model Deployment

This container provides the Nginx gateway for the MLOps platform, acting as a secure reverse proxy for the frontend dashboard and backend API services. It handles authentication, static file serving, API routing, and caching.

---

## 📁 Folder Structure

```
nginx/
├── Dockerfile        # Builds the Nginx container
├── nginx.conf        # Main Nginx configuration
├── nginx.conf.template  # Template for dynamic config (if used)
```

---

## ✨ Main Features

- **Reverse Proxy**: Routes requests to the frontend (React app) and backend (FastAPI API)
- **Authentication**: Supports HTTP basic authentication for all endpoints
- **Static File Serving**: Serves frontend static files efficiently
- **API Routing**: Proxies `/api/` requests to the backend service
- **React Router Support**: Handles client-side routing for SPA
- **Caching**: Adds cache headers for static assets
- **Health Check**: Exposes `/health` endpoint for container health monitoring

---

## 🛠️ Technology Stack

- **Nginx** (official Alpine image)
- **Custom configuration** for MLOps deployment

---

## 🔍 How It Works

- **nginx.conf**: Defines all routing, proxy, and security rules.
    - `/` serves the React frontend (static files)
    - `/api/` proxies to the backend API (model_deployment)
    - `/health` returns a simple JSON for health checks
    - Static assets are cached for performance
    - Basic auth can be enabled for all endpoints
- **Dockerfile**: Builds the Nginx image and copies the config files
- **nginx.conf.template**: (Optional) Used for dynamic config generation if needed

---

## 🚀 Usage

This container is started as part of the main `docker compose up` process. It expects the frontend build and backend API to be available at the configured internal hostnames.

### Standalone Build/Run

```bash
cd containers/nginx
docker build -t mlflow-nginx .
docker run -p 80:3000 mlflow-nginx
```

---

## ⚙️ Configuration

- **Port**: Listens on port 3000 (can be mapped to 80/443 externally)
- **Backend API Host**: Proxies `/api/` to `model_deployment:8000` (Docker network)
- **Frontend**: Serves static files from `/usr/share/nginx/html`
- **Authentication**: Add `auth_basic` and `auth_basic_user_file` to `nginx.conf` to enable basic auth
- **Custom Domains**: Update `server_name` as needed

---

## 🩹 Troubleshooting

- **Frontend not loading**: Check that the frontend build is present and Nginx is serving `/usr/share/nginx/html`
- **API not reachable**: Ensure backend service is running and accessible as `model_deployment:8000`
- **Authentication issues**: Verify basic auth config and credentials
- **Port conflicts**: Make sure the mapped port is not in use

---

## 🤝 Contributing

Pull requests and issues are welcome!

---
