# Dynamic Model Deployment System

This system provides dynamic model deployment capabilities for MLflow models with automatic port allocation and nginx routing.

## Architecture

The system consists of:
1. **Model Deployment Service** (`containers/model_deployment/`): FastAPI service that manages model deployment
2. **Nginx Proxy** (`containers/nginx/`): Routes requests to appropriate services
3. **Docker Compose**: Orchestrates all services with dynamic port exposure

## How It Works

### 1. Model Deployment Process

When you deploy a model:
1. The system allocates a free port from the range 8001-8100
2. MLflow model server is started on that port
3. The model is registered in the deployment service with its port mapping
4. Nginx routes requests to the deployment service, which proxies to the correct model

### 2. Request Flow

```
Client Request → Nginx → Model Deployment Service → Deployed Model
```

For example:
- `GET /my_model-1/invocations` → routed to model deployed on port 8001
- `GET /my_model-2/invocations` → routed to model deployed on port 8002

## API Endpoints

### Model Management
- `GET /get_model_list` - List available models in MLflow
- `GET /get_model_version_list/{model_name}` - List versions for a model
- `POST /deploy/{model_name}/{version}` - Deploy a specific model version
- `GET /get_deployed_models` - List currently deployed models
- `POST /undeploy/{model_name_and_version}` - Undeploy a model

### Model Access
- `GET /{model_name}-{version}/{path}` - Access deployed model endpoints
- `POST /{model_name}-{version}/{path}` - Send requests to deployed models

## Usage Examples

### 1. Deploy a Model
```bash
curl -X POST "http://localhost:8000/deploy/my_model/1"
```

### 2. Access Deployed Model
```bash
# Make predictions
curl -X POST "http://localhost:8000/my_model-1/invocations" \
  -H "Content-Type: application/json" \
  -d '{"data": [1, 2, 3]}'

# Get model info
curl "http://localhost:8000/my_model-1/"
```

### 3. List Deployed Models
```bash
curl "http://localhost:8000/get_deployed_models"
```

## Configuration

### Docker Compose
The `compose.yaml` file exposes:
- Port 8000: Model deployment API
- Ports 8001-8100: Dynamic range for deployed models

### Nginx Configuration
The nginx configuration routes:
- `config.{domain}` → Model deployment API (port 8000)
- `models.{domain}` → Dynamic model routing

## Security

- All endpoints require authentication via nginx basic auth
- Models are isolated in separate processes
- Port allocation prevents conflicts

## Troubleshooting

### Port Allocation Issues
If you get "No free ports available" error:
1. Check for zombie processes: `ps aux | grep mlflow`
2. Restart the model deployment service
3. Ensure ports 8001-8100 are not used by other services

### Model Access Issues
1. Verify the model is deployed: `GET /get_deployed_models`
2. Check the model server logs
3. Ensure the model name-version format is correct

## Development

### Adding New Features
1. Modify `containers/model_deployment/deployments.py`
2. Update `containers/model_deployment/requirements.txt` if needed
3. Rebuild the container: `docker-compose build model_deployment`

### Testing
Use the provided test script:
```bash
python test_model_deployment.py
``` 