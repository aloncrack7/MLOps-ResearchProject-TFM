import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Model Management API
export const modelAPI = {
  // Get list of available models
  getModelList: async () => {
    const response = await api.get('/get_model_list');
    return response.data;
  },

  // Get model versions
  getModelVersions: async (modelName) => {
    const response = await api.get(`/get_model_version_list/${modelName}`);
    return response.data;
  },

  // Deploy a model
  deployModel: async (modelName, version, numberOfOutputClasses = null) => {
    const params = numberOfOutputClasses ? { number_of_output_classes: numberOfOutputClasses } : {};
    const response = await api.post(`/deploy/${modelName}/${version}`, null, { params });
    return response.data;
  },

  // Get deployed models
  getDeployedModels: async () => {
    const response = await api.get('/get_deployed_models');
    return response.data;
  },

  // Get number of free ports
  getNumberFreePorts: async () => {
    const response = await api.get('/get_number_free_ports');
    return response.data;
  },

  // Undeploy a model
  undeployModel: async (modelNameAndVersion) => {
    const response = await api.post(`/undeploy/${modelNameAndVersion}`);
    return response.data;
  },

  // Get model signature
  getModelSignature: async (modelName, version) => {
    const response = await api.get(`/model/${modelName}-${version}/signature`);
    return response.data;
  },

  // Get type mapping
  getTypeMapping: async () => {
    const response = await api.get('/type_mapping');
    return response.data;
  },

  // Call a model
  callModel: async (modelName, version, data) => {
    const response = await api.post(`/model/${modelName}-${version}`, data);
    return response.data;
  },

  // Get initial report for a model
  getInitialReport: async (modelName, version) => {
    const response = await api.get(`/model/${modelName}-${version}/initial_report`);
    return response.data;
  },

  // Download initial report for a model
  downloadInitialReport: async (modelName, version) => {
    const response = await api.get(`/model/${modelName}-${version}/initial_report/download`, {
      responseType: 'blob'
    });
    return response;
  },

  // Get current metrics for a model
  getModelMetrics: async (modelName, version) => {
    const response = await api.get(`/model/${modelName}-${version}/metrics`);
    return response.data;
  },

  // Update model metrics with new data
  setNewMetrics: async (modelName, version, data) => {
    const response = await api.post(`/model/${modelName}-${version}/set_new_metrics`, data);
    return response.data;
  },

  // Download dataset for a model
  downloadDataset: async (modelName, version, startDate = null, endDate = null) => {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get(`/model/${modelName}-${version}/dataset`, {
      responseType: 'blob',
      params
    });
    return response;
  },

  // Get list of new metrics files for a model
  getNewMetricsFileNames: async (modelName, version) => {
    const response = await api.get(`/model/${modelName}-${version}/new_metrics_file_name`);
    return response.data;
  },

  // Get specific new metrics file content
  getNewMetricsFile: async (modelName, version, filename) => {
    const response = await api.get(`/model/${modelName}-${version}/new_metrics/${filename}`);
    return response.data;
  },

  // Download degradation report for a model
  downloadDegradationReport: async (modelName, version) => {
    const response = await api.get(`/model/${modelName}-${version}/degradation_report`, {
      responseType: 'blob'
    });
    return response;
  },
};

// Error handler
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

export default api; 