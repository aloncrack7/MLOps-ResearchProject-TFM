import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Alert,
  CircularProgress,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Refresh,
  Assessment,
  CloudDownload,
  TrendingUp,
  DataUsage,
  Close,
  History,
  CalendarToday,
  CompareArrows,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { modelAPI } from '../services/api';
import { useLocation } from 'react-router-dom';
import JsonTextField from '../components/JsonTextField';
import MetricsComparison from '../components/MetricsComparison';

function ModelMetrics() {
  const location = useLocation();
  const [deployedModels, setDeployedModels] = useState({});
  const [selectedModel, setSelectedModel] = useState('');
  const [currentMetrics, setCurrentMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Historical metrics state
  const [historicalMetrics, setHistoricalMetrics] = useState([]);
  const [loadingHistorical, setLoadingHistorical] = useState(false);
  const [selectedHistoricalFile, setSelectedHistoricalFile] = useState(null);
  const [historicalMetricsDialog, setHistoricalMetricsDialog] = useState(false);
  const [historicalMetricsData, setHistoricalMetricsData] = useState([]);
  const [comparisonDialog, setComparisonDialog] = useState(false);
  
  // New metrics dialog state
  const [newMetricsDialog, setNewMetricsDialog] = useState(false);
  const [newMetricsData, setNewMetricsData] = useState({
    instances: '',
    results: '',
    timestamp: null
  });
  const [updatingMetrics, setUpdatingMetrics] = useState(false);
  
  // Dataset download state
  const [datasetDialog, setDatasetDialog] = useState(false);
  const [dateRange, setDateRange] = useState({
    startDate: null,
    endDate: null
  });
  const [downloadingDataset, setDownloadingDataset] = useState(false);

  useEffect(() => {
    fetchDeployedModels();
  }, []);

  useEffect(() => {
    if (selectedModel) {
      fetchCurrentMetrics();
      fetchHistoricalMetrics();
    }
  }, [selectedModel]);

  // Handle pre-selected model from navigation state
  useEffect(() => {
    if (location.state?.selectedModel && deployedModels[location.state.selectedModel]) {
      setSelectedModel(location.state.selectedModel);
    }
  }, [location.state, deployedModels]);

  const fetchDeployedModels = async () => {
    try {
      setLoading(true);
      const models = await modelAPI.getDeployedModels();
      setDeployedModels(models);
      
      // Auto-select first model if available
      const modelKeys = Object.keys(models);
      if (modelKeys.length > 0 && !selectedModel) {
        setSelectedModel(modelKeys[0]);
      }
    } catch (err) {
      setError(`Failed to fetch deployed models: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentMetrics = async () => {
    if (!selectedModel) return;
    
    try {
      setLoading(true);
      const modelInfo = deployedModels[selectedModel];
      const metrics = await modelAPI.getModelMetrics(modelInfo.model_name, modelInfo.version);
      setCurrentMetrics(metrics);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch metrics: ${err.message}`);
      setCurrentMetrics(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalMetrics = async () => {
    if (!selectedModel) return;
    
    try {
      setLoadingHistorical(true);
      const modelInfo = deployedModels[selectedModel];
      const fileList = await modelAPI.getNewMetricsFileNames(modelInfo.model_name, modelInfo.version);
      
      // Sort files by timestamp (newest first)
      const sortedFiles = fileList.files.sort((a, b) => {
        const timestampA = parseFloat(a.replace('metrics_at_', '').replace('.json', ''));
        const timestampB = parseFloat(b.replace('metrics_at_', '').replace('.json', ''));
        return timestampB - timestampA;
      });
      
      setHistoricalMetrics(sortedFiles);
      
      // Fetch metrics data for comparison
      const metricsData = await Promise.all(
        sortedFiles.map(async (filename) => {
          try {
            const metrics = await modelAPI.getNewMetricsFile(modelInfo.model_name, modelInfo.version, filename);
            return { filename, metrics };
          } catch (err) {
            console.warn(`Failed to fetch metrics for ${filename}:`, err);
            return { filename, metrics: null };
          }
        })
      );
      
      setHistoricalMetricsData(metricsData.filter(item => item.metrics !== null));
    } catch (err) {
      console.warn('No historical metrics found or error fetching:', err.message);
      setHistoricalMetrics([]);
      setHistoricalMetricsData([]);
    } finally {
      setLoadingHistorical(false);
    }
  };

  const fetchSpecificHistoricalMetrics = async (filename) => {
    if (!selectedModel || !filename) return null;
    
    try {
      const modelInfo = deployedModels[selectedModel];
      const metrics = await modelAPI.getNewMetricsFile(modelInfo.model_name, modelInfo.version, filename);
      return metrics;
    } catch (err) {
      setError(`Failed to fetch historical metrics: ${err.message}`);
      return null;
    }
  };

  const handleViewHistoricalMetrics = async (filename) => {
    const metrics = await fetchSpecificHistoricalMetrics(filename);
    if (metrics) {
      setSelectedHistoricalFile({ filename, metrics });
      setHistoricalMetricsDialog(true);
    }
  };

  const handleUpdateMetrics = async () => {
    if (!selectedModel || !newMetricsData.instances || !newMetricsData.results) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setUpdatingMetrics(true);
      setError(null);
      
      const modelInfo = deployedModels[selectedModel];
      
      // Parse the JSON data
      const instances = JSON.parse(newMetricsData.instances);
      const results = JSON.parse(newMetricsData.results);
      
      const payload = {
        instances,
        results,
        timestamp: newMetricsData.timestamp || Date.now() / 1000
      };

      const updatedMetrics = await modelAPI.setNewMetrics(
        modelInfo.model_name, 
        modelInfo.version, 
        payload
      );
      
      setSuccess('Metrics updated successfully!');
      setNewMetricsDialog(false);
      setNewMetricsData({ instances: '', results: '', timestamp: null });
      
      // Refresh current metrics and historical metrics
      setTimeout(() => {
        fetchCurrentMetrics();
        fetchHistoricalMetrics();
        setSuccess(null);
      }, 2000);
      
    } catch (err) {
      setError(`Failed to update metrics: ${err.message}`);
    } finally {
      setUpdatingMetrics(false);
    }
  };

  const handleDownloadDataset = async () => {
    if (!selectedModel) return;
    
    try {
      setDownloadingDataset(true);
      const modelInfo = deployedModels[selectedModel];
      
      // Convert dates to ISO strings if provided
      const startDate = dateRange.startDate ? dateRange.startDate.toISOString() : null;
      const endDate = dateRange.endDate ? dateRange.endDate.toISOString() : null;
      
      const response = await modelAPI.downloadDataset(
        modelInfo.model_name,
        modelInfo.version,
        startDate,
        endDate
      );
      
      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${modelInfo.model_name}-${modelInfo.version}-dataset.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setSuccess('Dataset downloaded successfully!');
      setDatasetDialog(false);
      
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      setError(`Failed to download dataset: ${err.message}`);
    } finally {
      setDownloadingDataset(false);
    }
  };

  const renderMetricsTable = () => {
    if (!currentMetrics) return null;

    return (
      <TableContainer component={Paper} sx={{ mt: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Metric Name</strong></TableCell>
              <TableCell><strong>Value</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(currentMetrics).map(([metricName, value]) => (
              <TableRow key={metricName}>
                <TableCell>
                  <Typography variant="body2">
                    {metricName.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={typeof value === 'number' ? value.toFixed(4) : value}
                    color="primary"
                    variant="outlined"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Model Metrics Management
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Model Selection */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Select Model
                </Typography>
                <Box display="flex" gap={2} alignItems="center" mb={2}>
                  <FormControl sx={{ minWidth: 300 }}>
                    <InputLabel>Deployed Model</InputLabel>
                    <Select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      label="Deployed Model"
                    >
                      {Object.entries(deployedModels).map(([key, model]) => (
                        <MenuItem key={key} value={key}>
                          {model.model_name} v{model.version} (Port: {model.port})
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={fetchDeployedModels}
                    disabled={loading}
                  >
                    Refresh
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {selectedModel && (
            <>
              {/* Current Metrics */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        Current Metrics
                      </Typography>
                      <Box display="flex" gap={1}>
                        <Button
                          variant="outlined"
                          startIcon={<Assessment />}
                          onClick={fetchCurrentMetrics}
                          disabled={loading}
                          size="small"
                        >
                          {loading ? <CircularProgress size={20} /> : 'Refresh'}
                        </Button>
                      </Box>
                    </Box>
                    
                    {loading && !currentMetrics ? (
                      <Box display="flex" justifyContent="center" p={3}>
                        <CircularProgress />
                      </Box>
                    ) : currentMetrics ? (
                      renderMetricsTable()
                    ) : (
                      <Typography color="textSecondary">
                        No metrics available for this model
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Historical Metrics */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        Historical Metrics
                      </Typography>
                      <Box display="flex" gap={1}>
                        <Button
                          variant="outlined"
                          startIcon={<History />}
                          onClick={fetchHistoricalMetrics}
                          disabled={loadingHistorical}
                          size="small"
                        >
                          {loadingHistorical ? <CircularProgress size={20} /> : 'Refresh'}
                        </Button>
                      </Box>
                    </Box>
                    
                    {loadingHistorical ? (
                      <Box display="flex" justifyContent="center" p={3}>
                        <CircularProgress />
                      </Box>
                    ) : historicalMetrics.length > 0 ? (
                      <Box>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          {historicalMetrics.length} historical metric{historicalMetrics.length > 1 ? 's' : ''} available
                        </Typography>
                        <Box mt={2}>
                          {historicalMetrics.slice(0, 5).map((filename, index) => {
                            const timestamp = parseFloat(filename.replace('metrics_at_', '').replace('.json', ''));
                            const date = new Date(timestamp * 1000);
                            return (
                              <Box key={filename} mb={1}>
                                <Button
                                  variant="outlined"
                                  size="small"
                                  fullWidth
                                  startIcon={<CalendarToday />}
                                  onClick={() => handleViewHistoricalMetrics(filename)}
                                  sx={{ justifyContent: 'flex-start' }}
                                >
                                  {date.toLocaleString()}
                                </Button>
                              </Box>
                            );
                          })}
                          {historicalMetrics.length > 5 && (
                            <Typography variant="caption" color="textSecondary">
                              +{historicalMetrics.length - 5} more available
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    ) : (
                      <Typography color="textSecondary">
                        No historical metrics available
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Action Buttons */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Actions
                    </Typography>
                    <Box display="flex" gap={2} flexWrap="wrap">
                      <Button
                        variant="contained"
                        startIcon={<TrendingUp />}
                        onClick={() => setNewMetricsDialog(true)}
                        disabled={loading}
                      >
                        Update Metrics
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<DataUsage />}
                        onClick={() => setDatasetDialog(true)}
                        disabled={loading}
                      >
                        Download Dataset
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<CompareArrows />}
                        onClick={() => setComparisonDialog(true)}
                        disabled={loading || !currentMetrics || historicalMetricsData.length === 0}
                      >
                        Compare Metrics
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </>
          )}
        </Grid>

        {/* Historical Metrics Dialog */}
        <Dialog open={historicalMetricsDialog} onClose={() => setHistoricalMetricsDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            Historical Metrics
            <IconButton
              onClick={() => setHistoricalMetricsDialog(false)}
              sx={{ position: 'absolute', right: 8, top: 8 }}
            >
              <Close />
            </IconButton>
          </DialogTitle>
          <DialogContent>
            {selectedHistoricalFile && (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  File: {selectedHistoricalFile.filename}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Timestamp: {new Date(parseFloat(selectedHistoricalFile.filename.replace('metrics_at_', '').replace('.json', '')) * 1000).toLocaleString()}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell><strong>Metric Name</strong></TableCell>
                        <TableCell><strong>Value</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(selectedHistoricalFile.metrics).map(([metricName, value]) => (
                        <TableRow key={metricName}>
                          <TableCell>
                            <Typography variant="body2">
                              {metricName.replace(/_/g, ' ').toUpperCase()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={typeof value === 'number' ? value.toFixed(4) : value}
                              color="secondary"
                              variant="outlined"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setHistoricalMetricsDialog(false)}>
              Close
            </Button>
          </DialogActions>
        </Dialog>

        {/* Update Metrics Dialog */}
        <Dialog open={newMetricsDialog} onClose={() => setNewMetricsDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            Update Model Metrics
            <IconButton
              onClick={() => setNewMetricsDialog(false)}
              sx={{ position: 'absolute', right: 8, top: 8 }}
            >
              <Close />
            </IconButton>
          </DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Provide test data and expected results to calculate new metrics for your model.
            </Typography>
            
            <JsonTextField
              label="Input Instances (JSON Array)"
              placeholder='[{"feature1": 1.0, "feature2": 2.0}, {"feature1": 1.5, "feature2": 2.5}]'
              value={newMetricsData.instances}
              onChange={(e) => setNewMetricsData(prev => ({ ...prev, instances: e.target.value }))}
              helperText="JSON array of input instances for the model"
              rows={6}
              required
            />
            
            <JsonTextField
              label="Expected Results (JSON Array)"
              placeholder='[0, 1]'
              value={newMetricsData.results}
              onChange={(e) => setNewMetricsData(prev => ({ ...prev, results: e.target.value }))}
              helperText="JSON array of expected results corresponding to the input instances"
              rows={4}
              required
            />
            
            <TextField
              fullWidth
              label="Timestamp (optional)"
              type="number"
              value={newMetricsData.timestamp || ''}
              onChange={(e) => setNewMetricsData(prev => ({ ...prev, timestamp: e.target.value ? parseFloat(e.target.value) : null }))}
              margin="normal"
              helperText="Unix timestamp (leave empty to use current time)"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setNewMetricsDialog(false)} disabled={updatingMetrics}>
              Cancel
            </Button>
            <Button
              onClick={handleUpdateMetrics}
              variant="contained"
              disabled={updatingMetrics}
              startIcon={updatingMetrics ? <CircularProgress size={20} /> : <TrendingUp />}
            >
              {updatingMetrics ? 'Updating...' : 'Update Metrics'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Download Dataset Dialog */}
        <Dialog open={datasetDialog} onClose={() => setDatasetDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            Download Model Dataset
            <IconButton
              onClick={() => setDatasetDialog(false)}
              sx={{ position: 'absolute', right: 8, top: 8 }}
            >
              <Close />
            </IconButton>
          </DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Download the dataset of inputs that have been sent to this model. Optionally filter by date range.
            </Typography>
            
            <Box mt={3}>
              <DatePicker
                label="Start Date (optional)"
                value={dateRange.startDate}
                onChange={(newValue) => setDateRange(prev => ({ ...prev, startDate: newValue }))}
                renderInput={(params) => <TextField {...params} fullWidth margin="normal" />}
              />
              
              <DatePicker
                label="End Date (optional)"
                value={dateRange.endDate}
                onChange={(newValue) => setDateRange(prev => ({ ...prev, endDate: newValue }))}
                renderInput={(params) => <TextField {...params} fullWidth margin="normal" />}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDatasetDialog(false)} disabled={downloadingDataset}>
              Cancel
            </Button>
            <Button
              onClick={handleDownloadDataset}
              variant="contained"
              disabled={downloadingDataset}
              startIcon={downloadingDataset ? <CircularProgress size={20} /> : <CloudDownload />}
            >
              {downloadingDataset ? 'Downloading...' : 'Download CSV'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Metrics Comparison Dialog */}
        <MetricsComparison
          open={comparisonDialog}
          onClose={() => setComparisonDialog(false)}
          currentMetrics={currentMetrics}
          historicalMetrics={historicalMetricsData}
          modelInfo={selectedModel ? deployedModels[selectedModel] : null}
        />
      </Box>
    </LocalizationProvider>
  );
}

export default ModelMetrics;
