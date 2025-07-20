import React, { useState } from 'react';
import {
  TextField,
  Box,
  Typography,
  Alert,
  Collapse,
} from '@mui/material';

function JsonTextField({ 
  label, 
  value, 
  onChange, 
  placeholder, 
  helperText, 
  rows = 4,
  required = false,
  ...props 
}) {
  const [isValid, setIsValid] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  const validateJson = (text) => {
    if (!text.trim()) {
      if (required) {
        setIsValid(false);
        setErrorMessage('This field is required');
        return false;
      } else {
        setIsValid(true);
        setErrorMessage('');
        return true;
      }
    }

    try {
      JSON.parse(text);
      setIsValid(true);
      setErrorMessage('');
      return true;
    } catch (error) {
      setIsValid(false);
      setErrorMessage(`Invalid JSON: ${error.message}`);
      return false;
    }
  };

  const handleChange = (event) => {
    const newValue = event.target.value;
    onChange(event);
    validateJson(newValue);
  };

  return (
    <Box>
      <TextField
        {...props}
        fullWidth
        multiline
        rows={rows}
        label={label}
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        margin="normal"
        helperText={helperText}
        error={!isValid}
        sx={{
          '& .MuiOutlinedInput-root': {
            fontFamily: 'monospace',
          },
        }}
      />
      <Collapse in={!isValid}>
        <Alert severity="error" sx={{ mt: 1 }}>
          {errorMessage}
        </Alert>
      </Collapse>
    </Box>
  );
}

export default JsonTextField;
