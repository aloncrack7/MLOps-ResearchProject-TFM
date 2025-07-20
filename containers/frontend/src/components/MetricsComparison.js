import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Close,
  CompareArrows,
  TrendingUp,
  TrendingDown,
  Remove,
} from '@mui/icons-material';

function MetricsComparison({ 
  open, 
  onClose, 
  currentMetrics, 
  historicalMetrics, 
  modelInfo 
}) {
  const [selectedHistoricalFile, setSelectedHistoricalFile] = useState('');
  const [selectedHistoricalMetrics, setSelectedHistoricalMetrics] = useState(null);

  const handleHistoricalFileChange = async (filename) => {
    setSelectedHistoricalFile(filename);
    // This would typically fetch the specific historical metrics
    // For now, we'll assume it's passed in the historicalMetrics prop
    setSelectedHistoricalMetrics(historicalMetrics.find(m => m.filename === filename)?.metrics);
  };

  const calculateDifference = (current, historical) => {
    if (typeof current !== 'number' || typeof historical !== 'number') {
      return { diff: 'N/A', percentage: 'N/A', trend: 'neutral' };
    }
    
    const diff = current - historical;
    const percentage = historical !== 0 ? ((diff / historical) * 100) : 0;
    const trend = diff > 0 ? 'up' : diff < 0 ? 'down' : 'neutral';
    
    return { diff: diff.toFixed(4), percentage: percentage.toFixed(2), trend };
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return <TrendingUp color="success" />;
      case 'down': return <TrendingDown color="error" />;
      default: return <Remove color="disabled" />;
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up': return 'success';
      case 'down': return 'error';
      default: return 'default';
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        Metrics Comparison
        <IconButton
          onClick={onClose}
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Box mb={3}>
          <FormControl fullWidth>
            <InputLabel>Select Historical Metrics to Compare</InputLabel>
            <Select
              value={selectedHistoricalFile}
              onChange={(e) => handleHistoricalFileChange(e.target.value)}
              label="Select Historical Metrics to Compare"
            >
              {historicalMetrics.map((item) => {
                const timestamp = parseFloat(item.filename.replace('metrics_at_', '').replace('.json', ''));
                const date = new Date(timestamp * 1000);
                return (
                  <MenuItem key={item.filename} value={item.filename}>
                    {date.toLocaleString()}
                  </MenuItem>
                );
              })}
            </Select>
          </FormControl>
        </Box>

        {selectedHistoricalMetrics && currentMetrics && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Metric Name</strong></TableCell>
                  <TableCell><strong>Current Value</strong></TableCell>
                  <TableCell><strong>Historical Value</strong></TableCell>
                  <TableCell><strong>Difference</strong></TableCell>
                  <TableCell><strong>Change %</strong></TableCell>
                  <TableCell><strong>Trend</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.keys(currentMetrics).map((metricName) => {
                  const currentValue = currentMetrics[metricName];
                  const historicalValue = selectedHistoricalMetrics[metricName];
                  const comparison = calculateDifference(currentValue, historicalValue);
                  
                  return (
                    <TableRow key={metricName}>
                      <TableCell>
                        <Typography variant="body2">
                          {metricName.replace(/_/g, ' ').toUpperCase()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={typeof currentValue === 'number' ? currentValue.toFixed(4) : currentValue}
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={typeof historicalValue === 'number' ? historicalValue.toFixed(4) : historicalValue || 'N/A'}
                          color="secondary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color={comparison.trend === 'up' ? 'success.main' : comparison.trend === 'down' ? 'error.main' : 'text.secondary'}>
                          {comparison.diff}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color={comparison.trend === 'up' ? 'success.main' : comparison.trend === 'down' ? 'error.main' : 'text.secondary'}>
                          {comparison.percentage}%
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {getTrendIcon(comparison.trend)}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {!selectedHistoricalMetrics && (
          <Box textAlign="center" py={4}>
            <Typography color="textSecondary">
              Select a historical metrics file to compare with current metrics
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default MetricsComparison;
