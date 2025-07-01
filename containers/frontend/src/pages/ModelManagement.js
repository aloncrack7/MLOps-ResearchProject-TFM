import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow,
  Refresh,
  Info,
} from '@mui/icons-material';
import { modelAPI } from '../services/api';

function ModelManagement() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deployDialog, setDeployDialog] = useState(false);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedVersion, setSelectedVersion] = useState('');
  const [modelVersions, setModelVersions] = useState([]);
  const [deploying, setDeploying] = useState(false);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const modelList = await modelAPI.getModelList();
      setModels(modelList);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeployClick = async (modelName) => {
    try {
      setSelectedModel(modelName);
      const versions = await modelAPI.getModelVersions(modelName);
      setModelVersions(versions);
      setDeployDialog(true);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeploy = async () => {
    try {
      setDeploying(true);
      await modelAPI.deployModel(selectedModel, selectedVersion);
      setDeployDialog(false);
      setSelectedModel('');
      setSelectedVersion('');
      setModelVersions([]);
      // Refresh the page to show updated status
      window.location.reload();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeploying(false);
    }
  };

  const handleCloseDialog = () => {
    setDeployDialog(false);
    setSelectedModel('');
    setSelectedVersion('');
    setModelVersions([]);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Model Management
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchModels}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {models.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="h6" color="textSecondary" align="center">
              No models found in MLflow registry
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {models.map((model) => (
            <Grid item xs={12} md={6} lg={4} key={model}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box flex={1}>
                      <Typography variant="h6" gutterBottom>
                        {model}
                      </Typography>
                      <Chip
                        label="Available"
                        color="primary"
                        size="small"
                        sx={{ mb: 1 }}
                      />
                    </Box>
                    <Tooltip title="Deploy Model">
                      <IconButton
                        color="primary"
                        onClick={() => handleDeployClick(model)}
                      >
                        <PlayArrow />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Deploy Dialog */}
      <Dialog open={deployDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Deploy Model</DialogTitle>
        <DialogContent>
          <Box mt={2}>
            <TextField
              fullWidth
              label="Model Name"
              value={selectedModel}
              disabled
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth>
              <InputLabel>Version</InputLabel>
              <Select
                value={selectedVersion}
                label="Version"
                onChange={(e) => setSelectedVersion(e.target.value)}
              >
                {modelVersions.map((version) => (
                  <MenuItem key={version} value={version}>
                    Version {version}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={deploying}>
            Cancel
          </Button>
          <Button
            onClick={handleDeploy}
            variant="contained"
            disabled={!selectedVersion || deploying}
            startIcon={deploying ? <CircularProgress size={20} /> : <PlayArrow />}
          >
            {deploying ? 'Deploying...' : 'Deploy'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ModelManagement; 