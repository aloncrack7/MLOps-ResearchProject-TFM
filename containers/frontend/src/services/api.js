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
  deployModel: async (modelName, version) => {
    const response = await api.post(`/deploy/${modelName}/${version}`);
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