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
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Stop,
  Refresh,
  OpenInNew,
  Info,
  Delete,
  Science,
  Assessment,
  Download,
} from '@mui/icons-material';
import { modelAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

function DeployedModels() {
  const navigate = useNavigate();
  const [deployedModels, setDeployedModels] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [undeployDialog, setUndeployDialog] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  const [undeploying, setUndeploying] = useState(false);
  const [reportDialog, setReportDialog] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [downloadingReport, setDownloadingReport] = useState(null);
  const [currentReportModel, setCurrentReportModel] = useState(null);

  useEffect(() => {
    fetchDeployedModels();
  }, []);

  const fetchDeployedModels = async () => {
    try {
      setLoading(true);
      const models = await modelAPI.getDeployedModels();
      setDeployedModels(models);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUndeployClick = (modelKey, modelInfo) => {
    setSelectedModel({ key: modelKey, info: modelInfo });
    setUndeployDialog(true);
  };

  const handleUndeploy = async () => {
    try {
      setUndeploying(true);
      await modelAPI.undeployModel(selectedModel.key);
      setUndeployDialog(false);
      setSelectedModel(null);
      fetchDeployedModels(); // Refresh the list
    } catch (err) {
      setError(err.message);
    } finally {
      setUndeploying(false);
    }
  };

  const handleCloseDialog = () => {
    setUndeployDialog(false);
    setSelectedModel(null);
  };

  const handleViewReport = async (modelName, version) => {
    try {
      setLoadingReport(true);
      setReportDialog(true);
      setCurrentReportModel({ modelName, version });
      const report = await modelAPI.getInitialReport(modelName, version);
      setReportData(report);
    } catch (err) {
      setError(err.message);
      setReportDialog(false);
    } finally {
      setLoadingReport(false);
    }
  };

  const handleCloseReportDialog = () => {
    setReportDialog(false);
    setReportData(null);
    setCurrentReportModel(null);
  };

  const handleDownloadReport = async (modelName, version) => {
    try {
      setDownloadingReport(`${modelName}-${version}`);
      const response = await modelAPI.downloadInitialReport(modelName, version);
      
      // Create a blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${modelName}-${version}-initial-report.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(`Failed to download report: ${err.message}`);
    } finally {
      setDownloadingReport(null);
    }
  };

  const renderReportContent = () => {
    if (loadingReport) {
      return (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      );
    }

    if (!reportData || !reportData.files) {
      return (
        <Typography variant="body1" color="textSecondary">
          No report data available
        </Typography>
      );
    }

    return (
      <Box>
        {reportData.files.map((file, index) => (
          <Box key={index} mb={3}>
            <Typography variant="h6" gutterBottom>
              {file.filename}
            </Typography>
            {file.type === 'json' ? (
              <Box
                component="pre"
                sx={{
                  backgroundColor: 'grey.100',
                  p: 2,
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: 300,
                  fontSize: '0.875rem',
                }}
              >
                {JSON.stringify(file.content, null, 2)}
              </Box>
            ) : file.type === 'png' ? (
              <Box textAlign="center">
                <img
                  src={`data:image/png;base64,${file.content}`}
                  alt={file.filename}
                  style={{ maxWidth: '100%', height: 'auto' }}
                />
              </Box>
            ) : null}
          </Box>
        ))}
      </Box>
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const deployedModelsList = Object.entries(deployedModels);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Deployed Models
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchDeployedModels}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {deployedModelsList.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="h6" color="textSecondary" align="center">
              No models are currently deployed
            </Typography>
            <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 1 }}>
              Deploy a model from the Model Management page to get started
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Model Name</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Port</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {deployedModelsList.map(([modelKey, modelInfo]) => (
                <TableRow key={modelKey}>
                  <TableCell>
                    <Typography variant="subtitle1">
                      {modelInfo.model_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`v${modelInfo.version}`}
                      size="small"
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {modelInfo.port}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label="Running"
                      size="small"
                      color="success"
                    />
                  </TableCell>
                  <TableCell>
                    <Box display="flex" gap={1}>
                      <Tooltip title="View Initial Report">
                        <IconButton
                          size="small"
                          color="info"
                          onClick={() => handleViewReport(modelInfo.model_name, modelInfo.version)}
                        >
                          <Assessment />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download Initial Report">
                        <IconButton
                          size="small"
                          color="secondary"
                          onClick={() => handleDownloadReport(modelInfo.model_name, modelInfo.version)}
                          disabled={downloadingReport === `${modelInfo.model_name}-${modelInfo.version}`}
                        >
                          {downloadingReport === `${modelInfo.model_name}-${modelInfo.version}` ? 
                            <CircularProgress size={20} /> : <Download />
                          }
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Test Model">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => {
                            navigate('/testing', { 
                              state: { 
                                selectedModel: modelInfo.model_name, 
                                selectedVersion: modelInfo.version 
                              } 
                            });
                          }}
                        >
                          <Science />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Undeploy Model">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleUndeployClick(modelKey, modelInfo)}
                        >
                          <Stop />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Undeploy Dialog */}
      <Dialog open={undeployDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Undeploy Model</DialogTitle>
        <DialogContent>
          {selectedModel && (
            <Box mt={2}>
              <Typography variant="body1" gutterBottom>
                Are you sure you want to undeploy this model?
              </Typography>
              <Typography variant="h6" color="primary">
                {selectedModel.info.model_name} v{selectedModel.info.version}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Port: {selectedModel.info.port}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={undeploying}>
            Cancel
          </Button>
          <Button
            onClick={handleUndeploy}
            variant="contained"
            color="error"
            disabled={undeploying}
            startIcon={undeploying ? <CircularProgress size={20} /> : <Stop />}
          >
            {undeploying ? 'Undeploying...' : 'Undeploy'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Report Dialog */}
      <Dialog open={reportDialog} onClose={handleCloseReportDialog} maxWidth="md" fullWidth>
        <DialogTitle>Initial Report</DialogTitle>
        <DialogContent>
          {renderReportContent()}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseReportDialog}>
            Close
          </Button>
          {currentReportModel && (
            <Button
              onClick={() => handleDownloadReport(currentReportModel.modelName, currentReportModel.version)}
              startIcon={downloadingReport === `${currentReportModel.modelName}-${currentReportModel.version}` ? 
                <CircularProgress size={16} /> : <Download />}
              variant="outlined"
              disabled={downloadingReport === `${currentReportModel.modelName}-${currentReportModel.version}`}
            >
              Download Report
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default DeployedModels; 