import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, MenuItem, Select, FormControl, InputLabel, CircularProgress, Alert, Paper } from '@mui/material';
import { modelAPI } from '../services/api';

const API_BASE = process.env.REACT_APP_API_URL || '/api';

export default function DownloadDataset() {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');
  const [loadingModels, setLoadingModels] = useState(true);
  const [loadingVersions, setLoadingVersions] = useState(false);

  useEffect(() => {
    async function fetchModels() {
      setLoadingModels(true);
      setError('');
      try {
        const modelList = await modelAPI.getModelList();
        setModels(modelList);
      } catch (err) {
        setError('Failed to fetch models');
      } finally {
        setLoadingModels(false);
      }
    }
    fetchModels();
  }, []);

  useEffect(() => {
    if (!selectedModel) {
      setVersions([]);
      setSelectedVersion('');
      return;
    }
    async function fetchVersions() {
      setLoadingVersions(true);
      setError('');
      try {
        const versionList = await modelAPI.getModelVersions(selectedModel);
        setVersions(versionList);
      } catch (err) {
        setError('Failed to fetch versions');
      } finally {
        setLoadingVersions(false);
      }
    }
    fetchVersions();
  }, [selectedModel]);

  const handleDownload = async (e) => {
    e.preventDefault();
    setError('');
    setDownloading(true);
    try {
      const url = `${API_BASE}/model/${selectedModel}-${selectedVersion}/dataset`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to download dataset.');
      }
      const blob = await response.blob();
      const urlBlob = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = urlBlob;
      a.download = `${selectedModel}-${selectedVersion}-dataset.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(urlBlob);
    } catch (err) {
      setError(err.message);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ maxWidth: 500, margin: '40px auto', padding: 4 }}>
      <Typography variant="h5" gutterBottom>
        Download Model Dataset
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <form onSubmit={handleDownload}>
        <FormControl fullWidth sx={{ mb: 3 }} disabled={loadingModels || downloading}>
          <InputLabel>Model</InputLabel>
          <Select
            value={selectedModel}
            label="Model"
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            {loadingModels ? (
              <MenuItem value=""><CircularProgress size={20} /></MenuItem>
            ) : (
              models.map((model) => (
                <MenuItem key={model} value={model}>{model}</MenuItem>
              ))
            )}
          </Select>
        </FormControl>
        <FormControl fullWidth sx={{ mb: 3 }} disabled={!selectedModel || loadingVersions || downloading}>
          <InputLabel>Version</InputLabel>
          <Select
            value={selectedVersion}
            label="Version"
            onChange={(e) => setSelectedVersion(e.target.value)}
          >
            {loadingVersions ? (
              <MenuItem value=""><CircularProgress size={20} /></MenuItem>
            ) : (
              versions.map((version) => (
                <MenuItem key={version} value={version}>{version}</MenuItem>
              ))
            )}
          </Select>
        </FormControl>
        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          disabled={!selectedModel || !selectedVersion || downloading}
        >
          {downloading ? 'Downloading...' : 'Download CSV'}
        </Button>
      </form>
    </Paper>
  );
} 