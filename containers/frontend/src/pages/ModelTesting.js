import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Chip,
  InputAdornment,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  PlayArrow,
  Upload,
  Download,
  ExpandMore,
  ExpandLess,
  Info,
  Code,
  DataObject,
} from '@mui/icons-material';
import { modelAPI } from '../services/api';
import { useLocation } from 'react-router-dom';

const ModelTesting = () => {
  const location = useLocation();
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(location.state?.selectedModel || '');
  const [selectedVersion, setSelectedVersion] = useState(location.state?.selectedVersion || '');
  const [modelVersions, setModelVersions] = useState([]);
  const [signature, setSignature] = useState(null);
  const [typeMapping, setTypeMapping] = useState({});
  const [inputData, setInputData] = useState({});
  const [jsonInput, setJsonInput] = useState('');
  const [testMode, setTestMode] = useState('manual'); // 'manual' or 'json'
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedInputs, setExpandedInputs] = useState(true);
  const [expandedOutputs, setExpandedOutputs] = useState(true);
  const [expandedParams, setExpandedParams] = useState(true);

  useEffect(() => {
    loadModels();
    loadTypeMapping();
  }, []);

  useEffect(() => {
    if (selectedModel) {
      loadModelVersions(selectedModel);
    }
  }, [selectedModel]);

  useEffect(() => {
    if (selectedModel && selectedVersion) {
      loadModelSignature(selectedModel, selectedVersion);
    }
  }, [selectedModel, selectedVersion]);

  const loadModels = async () => {
    try {
      const modelList = await modelAPI.getModelList();
      setModels(modelList);
    } catch (error) {
      setError('Failed to load models: ' + error.message);
    }
  };

  const loadModelVersions = async (modelName) => {
    try {
      const versions = await modelAPI.getModelVersions(modelName);
      setModelVersions(versions);
      setSelectedVersion('');
    } catch (error) {
      setError('Failed to load model versions: ' + error.message);
    }
  };

  const loadModelSignature = async (modelName, version) => {
    try {
      setLoading(true);
      const signatureData = await modelAPI.getModelSignature(modelName, version);
      setSignature(signatureData);
      setInputData({});
      setJsonInput('');
      setResult(null);
      setError('');
    } catch (error) {
      setError('Failed to load model signature: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTypeMapping = async () => {
    try {
      const mapping = await modelAPI.getTypeMapping();
      setTypeMapping(mapping.python_to_mlflow_types);
    } catch (error) {
      console.error('Failed to load type mapping:', error);
    }
  };

  const handleInputChange = (inputName, value) => {
    setInputData(prev => ({
      ...prev,
      [inputName]: value
    }));
  };

  const handleJsonFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const jsonData = JSON.parse(e.target.result);
          setJsonInput(JSON.stringify(jsonData, null, 2));
          setInputData(jsonData);
        } catch (error) {
          setError('Invalid JSON file: ' + error.message);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleTestModel = async () => {
    if (!selectedModel || !selectedVersion) {
      setError('Please select a model and version');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const dataToSend = testMode === 'json' && jsonInput 
        ? JSON.parse(jsonInput) 
        : inputData;

      const response = await modelAPI.callModel(selectedModel, selectedVersion, dataToSend);
      setResult(response);
    } catch (error) {
      setError('Model test failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const getTypeInfo = (typeName) => {
    return typeMapping[typeName] || { example: 'Unknown type', notes: 'Type not found in mapping' };
  };

  const downloadResult = () => {
    if (result) {
      const dataStr = JSON.stringify(result, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${selectedModel}-${selectedVersion}-result.json`;
      link.click();
      URL.revokeObjectURL(url);
    }
  };

  const renderInputField = (input) => {
    const typeInfo = getTypeInfo(input.type);
    
    return (
      <TextField
        key={input.name}
        label={input.name}
        type={input.type === 'bool' ? 'text' : 'text'}
        placeholder={typeInfo.example?.toString() || 'Enter value'}
        value={inputData[input.name] || ''}
        onChange={(e) => handleInputChange(input.name, e.target.value)}
        fullWidth
        margin="normal"
        helperText={`Type: ${input.type} - ${typeInfo.notes}`}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <Chip 
                label={input.type} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            </InputAdornment>
          ),
        }}
      />
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Model Testing
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Model Selection */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Model Selection
            </Typography>
            <FormControl fullWidth margin="normal">
              <InputLabel>Model</InputLabel>
              <Select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                label="Model"
              >
                {models.map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Version</InputLabel>
              <Select
                value={selectedVersion}
                onChange={(e) => setSelectedVersion(e.target.value)}
                label="Version"
                disabled={!selectedModel}
              >
                {modelVersions.map((version) => (
                  <MenuItem key={version} value={version}>
                    {version}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        {/* Test Mode Selection */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Test Mode
            </Typography>
            <FormControl fullWidth margin="normal">
              <InputLabel>Input Method</InputLabel>
              <Select
                value={testMode}
                onChange={(e) => setTestMode(e.target.value)}
                label="Input Method"
              >
                <MenuItem value="manual">Manual Input</MenuItem>
                <MenuItem value="json">JSON File Upload</MenuItem>
              </Select>
            </FormControl>
            
            {testMode === 'json' && (
              <>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<Upload />}
                  fullWidth
                  sx={{ mt: 2 }}
                >
                  Upload JSON File
                  <input
                    type="file"
                    hidden
                    accept=".json"
                    onChange={handleJsonFileUpload}
                  />
                </Button>
                <Button
                  variant="text"
                  startIcon={<Download />}
                  fullWidth
                  sx={{ mt: 1 }}
                  onClick={() => {
                    const link = document.createElement('a');
                    link.href = '/example-input.json';
                    link.download = 'example-input.json';
                    link.click();
                  }}
                >
                  Download Example JSON
                </Button>
              </>
            )}
          </Paper>
        </Grid>

        {/* Model Signature */}
        {signature && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Model Signature
              </Typography>
              
              {/* Inputs */}
              {signature.signature.inputs && signature.signature.inputs.length > 0 && (
                <Card sx={{ mb: 2 }}>
                  <CardHeader
                    title="Inputs"
                    avatar={<DataObject />}
                    action={
                      <IconButton onClick={() => setExpandedInputs(!expandedInputs)}>
                        {expandedInputs ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    }
                  />
                  <Collapse in={expandedInputs}>
                    <CardContent>
                      <Grid container spacing={2}>
                        {signature.signature.inputs.map((input) => (
                          <Grid item xs={12} md={6} key={input.name}>
                            {renderInputField(input)}
                          </Grid>
                        ))}
                      </Grid>
                    </CardContent>
                  </Collapse>
                </Card>
              )}

              {/* Parameters */}
              {signature.signature.params && signature.signature.params.length > 0 && (
                <Card sx={{ mb: 2 }}>
                  <CardHeader
                    title="Parameters"
                    avatar={<Code />}
                    action={
                      <IconButton onClick={() => setExpandedParams(!expandedParams)}>
                        {expandedParams ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    }
                  />
                  <Collapse in={expandedParams}>
                    <CardContent>
                      <Grid container spacing={2}>
                        {signature.signature.params.map((param) => (
                          <Grid item xs={12} md={6} key={param.name}>
                            {renderInputField(param)}
                          </Grid>
                        ))}
                      </Grid>
                    </CardContent>
                  </Collapse>
                </Card>
              )}

              {/* Outputs */}
              {signature.signature.outputs && signature.signature.outputs.length > 0 && (
                <Card>
                  <CardHeader
                    title="Expected Outputs"
                    avatar={<Info />}
                    action={
                      <IconButton onClick={() => setExpandedOutputs(!expandedOutputs)}>
                        {expandedOutputs ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    }
                  />
                  <Collapse in={expandedOutputs}>
                    <CardContent>
                      <List>
                        {signature.signature.outputs.map((output) => {
                          const typeInfo = getTypeInfo(output.type);
                          return (
                            <ListItem key={output.name}>
                              <ListItemIcon>
                                <Chip 
                                  label={output.type} 
                                  size="small" 
                                  color="secondary" 
                                  variant="outlined"
                                />
                              </ListItemIcon>
                              <ListItemText
                                primary={output.name}
                                secondary={`${typeInfo.notes} (Example: ${typeInfo.example})`}
                              />
                            </ListItem>
                          );
                        })}
                      </List>
                    </CardContent>
                  </Collapse>
                </Card>
              )}
            </Paper>
          </Grid>
        )}

        {/* JSON Input */}
        {testMode === 'json' && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                JSON Input
              </Typography>
              <TextField
                multiline
                rows={8}
                fullWidth
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
                placeholder="Enter JSON data here or upload a file..."
                variant="outlined"
              />
            </Paper>
          </Grid>
        )}

        {/* Test Button */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              startIcon={<PlayArrow />}
              onClick={handleTestModel}
              disabled={loading || !selectedModel || !selectedVersion}
            >
              {loading ? 'Testing...' : 'Test Model'}
            </Button>
          </Box>
        </Grid>

        {/* Results */}
        {result && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Test Results
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  onClick={downloadResult}
                >
                  Download Result
                </Button>
              </Box>
              <TextField
                multiline
                rows={10}
                fullWidth
                value={JSON.stringify(result, null, 2)}
                InputProps={{
                  readOnly: true,
                }}
                variant="outlined"
              />
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default ModelTesting;
