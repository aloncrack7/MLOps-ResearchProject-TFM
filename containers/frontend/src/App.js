import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';
import { Science } from '@mui/icons-material';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import ModelManagement from './pages/ModelManagement';
import DeployedModels from './pages/DeployedModels';
import ModelTesting from './pages/ModelTesting';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Navigation open={sidebarOpen} onToggle={handleSidebarToggle} />
          <Science sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            MLflow Model Deployment
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Box sx={{ display: 'flex', flex: 1 }}>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Container maxWidth="xl">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/models" element={<ModelManagement />} />
              <Route path="/deployed" element={<DeployedModels />} />
              <Route path="/testing" element={<ModelTesting />} />
            </Routes>
          </Container>
        </Box>
      </Box>
    </Box>
  );
}

export default App; 