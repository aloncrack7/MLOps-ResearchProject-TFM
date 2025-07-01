import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import {
  ModelTraining,
  PlayArrow,
  Storage,
  Speed,
  Science,
} from '@mui/icons-material';
import { modelAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalModels: 0,
    deployedModels: 0,
    freePorts: 0,
    loading: true,
    error: null,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [modelList, deployedModels, freePorts] = await Promise.all([
          modelAPI.getModelList(),
          modelAPI.getDeployedModels(),
          modelAPI.getNumberFreePorts(),
        ]);

        setStats({
          totalModels: modelList.length,
          deployedModels: Object.keys(deployedModels).length,
          freePorts: freePorts,
          loading: false,
          error: null,
        });
      } catch (error) {
        setStats({
          totalModels: 0,
          deployedModels: 0,
          freePorts: 0,
          loading: false,
          error: error.message,
        });
      }
    };

    fetchStats();
  }, []);

  const StatCard = ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              backgroundColor: color,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (stats.loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (stats.error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading dashboard: {stats.error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Models"
            value={stats.totalModels}
            icon={<ModelTraining sx={{ color: 'white' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Deployed Models"
            value={stats.deployedModels}
            icon={<PlayArrow sx={{ color: 'white' }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Available Ports"
            value={stats.freePorts}
            icon={<Storage sx={{ color: 'white' }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="System Status"
            value="Online"
            icon={<Speed sx={{ color: 'white' }} />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item>
            <Button
              variant="contained"
              startIcon={<Science />}
              onClick={() => navigate('/testing')}
              sx={{ mr: 2 }}
            >
              Test Models
            </Button>
          </Grid>
        </Grid>
        <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
          Use the navigation menu to manage your models and deployments.
        </Typography>
      </Box>
    </Box>
  );
}

export default Dashboard; 