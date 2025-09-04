# MLflow Model Deployment Frontend

A modern React-based dashboard for managing, monitoring, and testing MLflow model deployments. This frontend provides a user-friendly interface to interact with the backend model deployment API, visualize metrics, download datasets, and more.

---

## 📁 Folder Structure

```
frontend/
├── Dockerfile           # Multi-stage build for production with Nginx
├── nginx.conf           # Nginx config for serving and API proxy
├── package.json         # Project dependencies and scripts
├── public/
│   └── index.html       # HTML entry point
└── src/
    ├── App.js           # Main app layout and routing
    ├── index.js         # React entry point
    ├── components/
    │   ├── JsonTextField.js
    │   ├── MetricsComparison.js
    │   └── Navigation.js
    ├── pages/
    │   ├── Dashboard.js
    │   ├── ModelManagement.js
    │   ├── DeployedModels.js
    │   ├── ModelTesting.js
    │   ├── ModelMetrics.js
    │   ├── DegradationReport.js
    │   └── DownloadDataset.js
    └── services/
        └── api.js
```

---

## ✨ Main Features

- **Dashboard**: System overview (model count, deployed models, available ports, status).
- **Model Management**: Browse MLflow registry, deploy models, select versions.
- **Deployed Models**: List, monitor, undeploy, and access deployed models. Download initial reports and datasets.
- **Model Testing**: Test deployed models with manual or JSON input, view and download results.
- **Model Metrics**: View, update, and compare model metrics (current and historical).
- **Degradation Reports**: Download detailed model degradation reports (data drift, performance, recommendations).
- **Dataset Download**: Download input datasets for any deployed model/version.
- **Navigation**: Sidebar for quick access to all features.
- **Responsive Design**: Works on desktop and mobile.

---

## 🛠️ Technology Stack

- **React 18** with hooks
- **Material-UI** for UI components
- **React Router** for navigation
- **Axios** for API calls
- **date-fns** and **@mui/x-date-pickers** for date handling
- **Docker** and **Nginx** for production deployment

---

## 🔍 How It Works

- **App.js**: Sets up the main layout, top bar, and routes to all feature pages.
- **Navigation.js**: Sidebar menu for navigating between dashboard, management, metrics, etc.
- **api.js**: Centralizes all API calls to the backend (model list, deploy, metrics, reports, etc.).
- **Dashboard.js**: Fetches and displays system stats and quick actions.
- **ModelManagement.js**: Lists all models in MLflow, allows deployment of any version.
- **DeployedModels.js**: Shows all running models, allows undeploy, report/dataset download, and quick actions.
- **ModelTesting.js**: Lets users test models with custom/manual or JSON input, and view/download results.
- **ModelMetrics.js**: Displays current and historical metrics, allows updating and comparing metrics, and dataset download.
- **DegradationReport.js**: Lets users download comprehensive degradation reports for any deployed model.
- **DownloadDataset.js**: Simple UI to download the dataset for any model/version.

---

## 🚀 Development & Usage

### Prerequisites

- Node.js 18+
- npm or yarn

### Local Development

```bash
cd containers/frontend
npm install
npm start
# App runs at http://localhost:3000
```

### Production Build

```bash
npm run build
docker build -t mlflow-frontend .
```

### Docker/Nginx

- The `Dockerfile` builds the React app and serves it with Nginx.
- `nginx.conf` proxies `/api` requests to the backend and serves static files.

---

## ⚡ API Integration

All API calls are made via `/api` (proxied to backend). See `src/services/api.js` for all endpoints used.

---

## 🔒 Security

- All requests require authentication (nginx basic auth).
- No sensitive data is stored in the frontend.
- HTTPS is recommended for production.

---

## 🩹 Troubleshooting

- **API errors**: Check backend service and nginx proxy.
- **Model deployment issues**: Check backend logs and MLflow registry.
- **Frontend not loading**: Ensure the container is running and nginx is configured.

---

## 🤝 Contributing

Pull requests and issues are welcome!

---
