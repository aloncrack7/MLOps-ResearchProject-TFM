# Model Testing Feature

This document describes the Model Testing feature that allows users to test deployed MLflow models through a web interface.

## Overview

The Model Testing page provides a comprehensive interface for:
- Viewing model signatures (inputs, outputs, and parameters)
- Testing models with manual input or JSON file upload
- Downloading test results
- Understanding data types and examples

## Features

### 1. Model Selection
- Dropdown to select from available models
- Version selection for each model
- Automatic signature loading when model is selected

### 2. Input Methods
- **Manual Input**: Fill in form fields based on model signature
- **JSON Upload**: Upload a JSON file with test data
- **JSON Editor**: Direct JSON editing in a text area

### 3. Signature Display
- **Inputs**: Shows all required input fields with type information
- **Parameters**: Displays model parameters if any
- **Outputs**: Shows expected output structure and types
- **Collapsible Sections**: Expandable/collapsible signature sections
- **Type Information**: Shows data type examples and notes

### 4. Testing Features
- Real-time model testing
- Error handling and display
- Loading states during testing
- Result display in formatted JSON
- Download results as JSON file

### 5. Navigation Integration
- Accessible from main navigation menu
- Quick access from Deployed Models page
- Quick access from Dashboard
- Pre-selection of model when navigating from Deployed Models

## Usage

### Basic Testing Workflow

1. **Navigate to Model Testing**
   - Use the navigation menu: "Model Testing"
   - Or click "Test Models" from Dashboard
   - Or click the test icon (🧪) from Deployed Models page

2. **Select Model and Version**
   - Choose a model from the dropdown
   - Select the version to test

3. **Choose Input Method**
   - **Manual**: Fill in the form fields that appear
   - **JSON**: Upload a file or edit JSON directly

4. **Review Model Signature**
   - Check the inputs, parameters, and expected outputs
   - Note the data types and examples provided

5. **Test the Model**
   - Click "Test Model" button
   - View results in the results section
   - Download results if needed

### JSON Input Format

The JSON input should match your model's signature. Example:

```json
{
  "feature1": 1.0,
  "feature2": "example_string",
  "feature3": true,
  "feature4": 42
}
```

### Type Support

The system supports various MLflow data types:
- **str**: String values
- **int**: Integer values
- **float**: Floating-point numbers
- **bool**: Boolean values (true/false)
- **datetime**: Date/time values
- **bytes**: Binary data
- **numpy types**: Various NumPy data types

## API Endpoints

The Model Testing feature uses these backend endpoints:

- `GET /model/{model_name}-{version}/signature` - Get model signature
- `GET /type_mapping` - Get type mapping information
- `POST /model/{model_name}-{version}` - Call the model
- `GET /get_model_list` - Get available models
- `GET /get_model_version_list/{model_name}` - Get model versions

## Error Handling

The interface handles various error scenarios:
- Model not found
- Invalid JSON input
- Network errors
- Model execution errors
- Type conversion errors

## Example Files

An example JSON input file is provided at `/example-input.json` that users can download and modify for their specific models.

## Integration Points

### Deployed Models Page
- Test button (🧪) for each deployed model
- Pre-selects model and version when navigating

### Dashboard
- Quick action button to access Model Testing
- Direct navigation to testing interface

### Navigation Menu
- Dedicated "Model Testing" menu item
- Consistent navigation across the application

## Technical Implementation

### Frontend Components
- `ModelTesting.js` - Main testing interface
- `api.js` - API service functions
- Material-UI components for consistent UI

### State Management
- React hooks for local state
- Form state management
- Loading and error states
- Navigation state handling

### Data Flow
1. Load models and type mapping on component mount
2. Load model versions when model is selected
3. Load signature when version is selected
4. Handle user input (manual or JSON)
5. Send test request to backend
6. Display results or errors

## Future Enhancements

Potential improvements for the Model Testing feature:
- Batch testing with multiple inputs
- Test result history
- Model performance metrics
- Input validation rules
- Custom test scenarios
- Integration with CI/CD pipelines 