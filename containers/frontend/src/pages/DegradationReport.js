import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  CircularProgress,
  Grid,
} from '@mui/material';
import { Download as DownloadIcon, Assessment as ReportIcon } from '@mui/icons-material';
import { modelAPI } from '../services/api';

function DegradationReport() {
  const [deployedModels, setDeployedModels] = useState({});
  const [selectedModel, setSelectedModel] = useState('');
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchDeployedModels();
  }, []);

  const fetchDeployedModels = async () => {
    try {
      setLoading(true);
      const response = await modelAPI.getDeployedModels();
      setDeployedModels(response);
    } catch (error) {
      console.error('Error fetching deployed models:', error);
      setError('Failed to fetch deployed models. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!selectedModel) {
      setError('Please select a model first.');
      return;
    }

    try {
      setDownloading(true);
      setError('');
      setSuccess('');

      const response = await modelAPI.downloadDegradationReport(
        deployedModels[selectedModel].model_name,
        deployedModels[selectedModel].version
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${selectedModel}-degradation-report.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSuccess('Degradation report downloaded successfully!');
    } catch (error) {
      console.error('Error downloading degradation report:', error);
      setError('Failed to download degradation report. Please try again.');
    } finally {
      setDownloading(false);
    }
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
      <Typography variant="h4" gutterBottom>
        Model Degradation Reports
      </Typography>

      <Typography variant="body1" color="textSecondary" gutterBottom>
        Download comprehensive degradation reports for your deployed models. Reports include data drift analysis, 
        performance degradation metrics, and comparison with baseline performance.
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Generate Degradation Report
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {success && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  {success}
                </Alert>
              )}

              <Box sx={{ mb: 3 }}>
                <FormControl fullWidth>
                  <InputLabel>Select Deployed Model</InputLabel>
                  <Select
                    value={selectedModel}
                    label="Select Deployed Model"
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    {Object.keys(deployedModels).map((modelKey) => (
                      <MenuItem key={modelKey} value={modelKey}>
                        {deployedModels[modelKey].model_name} - Version {deployedModels[modelKey].version}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Button
                variant="contained"
                color="primary"
                onClick={handleDownloadReport}
                disabled={!selectedModel || downloading}
                startIcon={downloading ? <CircularProgress size={20} /> : <DownloadIcon />}
                fullWidth
              >
                {downloading ? 'Generating Report...' : 'Download Degradation Report'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <ReportIcon sx={{ mr: 1 }} />
                What's Included
              </Typography>
              
              <Typography variant="body2" color="textSecondary" paragraph>
                The degradation report contains:
              </Typography>

              <Box component="ul" sx={{ pl: 2, mb: 0 }}>
                <Typography component="li" variant="body2" gutterBottom>
                  Data drift analysis comparing current data to training data
                </Typography>
                <Typography component="li" variant="body2" gutterBottom>
                  Performance metrics comparison over time (week, month, year)
                </Typography>
                <Typography component="li" variant="body2" gutterBottom>
                  Statistical summaries and visualizations
                </Typography>
                <Typography component="li" variant="body2" gutterBottom>
                  Cluster analysis and distribution changes
                </Typography>
                <Typography component="li" variant="body2" gutterBottom>
                  Recommendations for model retraining
                </Typography>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Report Format
              </Typography>
              
              <Typography variant="body2" color="textSecondary">
                Reports are generated as ZIP files containing JSON data files, 
                statistical reports, and visualization charts in PNG format.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DegradationReport;
