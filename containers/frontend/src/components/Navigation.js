import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  IconButton,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ModelTraining as ModelIcon,
  PlayArrow as DeployedIcon,
  Science as TestingIcon,
  Menu as MenuIcon,
  GetApp as GetAppIcon,
  Assessment as MetricsIcon,
} from '@mui/icons-material';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Model Management', icon: <ModelIcon />, path: '/models' },
  { text: 'Deployed Models', icon: <DeployedIcon />, path: '/deployed' },
  { text: 'Model Testing', icon: <TestingIcon />, path: '/testing' },
  { text: 'Model Metrics', icon: <MetricsIcon />, path: '/metrics' },
  { text: 'Download Dataset', icon: <GetAppIcon />, path: '/download' },
];

function Navigation({ open, onToggle }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <>
      <IconButton
        color="inherit"
        aria-label="toggle sidebar"
        onClick={onToggle}
        sx={{ mr: 2 }}
      >
        <MenuIcon />
      </IconButton>
      
      <Drawer
        variant="temporary"
        open={open}
        onClose={onToggle}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Box sx={{ overflow: 'auto', mt: 8 }}>
          <List>
            {menuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => {
                    navigate(item.path);
                    onToggle(); // Close sidebar after navigation
                  }}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Divider />
        </Box>
      </Drawer>
    </>
  );
}

export default Navigation; 