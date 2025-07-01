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
                      <Tooltip title="View Model Info">
                        <IconButton
                          size="small"
                          onClick={() => {
                            // Open model info in new tab
                            window.open(`http://localhost:${modelInfo.port}`, '_blank');
                          }}
                        >
                          <OpenInNew />
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
    </Box>
  );
}

export default DeployedModels; 