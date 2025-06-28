# MLflow Model Deployment Frontend

A modern React-based control panel for managing MLflow model deployments.

## Features

- **Dashboard**: Overview of system statistics and model counts
- **Model Management**: Browse available models and deploy them
- **Deployed Models**: Monitor and manage currently deployed models
- **Real-time Updates**: Automatic refresh and status monitoring
- **Responsive Design**: Works on desktop and mobile devices

## Pages

### Dashboard
- System overview with key metrics
- Total models count
- Deployed models count
- Available ports
- System status

### Model Management
- List all available models from MLflow registry
- View model versions
- Deploy models with version selection
- Real-time deployment status

### Deployed Models
- Table view of all deployed models
- Model information (name, version, port)
- Status indicators
- Actions: view model info, undeploy
- Direct access to model endpoints

## Technology Stack

- **React 18**: Modern React with hooks
- **Material-UI**: Professional UI components
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **Docker**: Containerized deployment

## Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Local Development
```bash
cd containers/frontend
npm install
npm start
```

The app will be available at `http://localhost:3000`

### Building for Production
```bash
npm run build
```

### Docker Build
```bash
docker build -t mlflow-frontend .
```

## API Integration

The frontend communicates with the model deployment API through:

- **Base URL**: `/api` (proxied to backend)
- **Endpoints**:
  - `GET /get_model_list` - List available models
  - `GET /get_model_version_list/{model}` - Get model versions
  - `POST /deploy/{model}/{version}` - Deploy a model
  - `GET /get_deployed_models` - Get deployed models
  - `POST /undeploy/{model-version}` - Undeploy a model

## Configuration

### Environment Variables
- `REACT_APP_API_URL`: Backend API URL (default: `/api`)

### Nginx Configuration
The frontend is served through nginx with:
- Authentication required
- API proxy configuration
- Static file caching

## Usage

1. **Access the Control Panel**: Navigate to `control.yourdomain.com`
2. **Authenticate**: Enter your credentials
3. **Browse Models**: Go to Model Management to see available models
4. **Deploy Models**: Click the deploy button and select a version
5. **Monitor Deployments**: Check the Deployed Models page for status
6. **Manage Models**: Undeploy models when no longer needed

## Security

- All requests require authentication via nginx basic auth
- API calls are proxied through nginx
- No sensitive data stored in frontend
- HTTPS recommended for production

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check if the backend service is running
   - Verify nginx configuration
   - Check authentication credentials

2. **Model Deployment Failures**
   - Check backend logs
   - Verify model exists in MLflow registry
   - Check port availability

3. **Frontend Not Loading**
   - Check if frontend container is running
   - Verify nginx configuration
   - Check browser console for errors

### Debug Mode
Enable debug logging by setting `NODE_ENV=development` in the container environment. 