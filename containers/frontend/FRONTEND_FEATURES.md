# Frontend New Features Documentation

This document describes the new frontend features that have been added to integrate with the new backend endpoints for model metrics management and dataset download.

## New Features

### 1. Model Metrics Management Page

**Location**: `/metrics`

**Description**: A dedicated page for managing and monitoring model metrics.

**Features**:
- **View Current Metrics**: Display current baseline metrics for deployed models
- **Update Metrics**: Calculate new metrics by providing test data and expected results
- **Download Dataset**: Download CSV files of all input data sent to a model
- **Date Range Filtering**: Filter dataset downloads by date range

**How to Use**:
1. Navigate to "Model Metrics" in the sidebar
2. Select a deployed model from the dropdown
3. View current metrics in the table
4. Click "Update Metrics" to calculate new metrics with test data
5. Click "Download Dataset" to export input data as CSV

### 2. Enhanced Deployed Models Page

**Location**: `/deployed`

**New Features**:
- **Manage Metrics Button**: Quick access to metrics management for each model
- **Download Dataset Button**: Direct dataset download from the deployed models table

**How to Use**:
1. Navigate to "Deployed Models"
2. For each deployed model, you now have additional action buttons:
   - **Trending Up Icon**: Opens the metrics management page for that specific model
   - **Data Usage Icon**: Downloads the dataset for that model directly

### 3. New API Endpoints Integration

The frontend now integrates with these new backend endpoints:

- `GET /model/{model_name}-{version}/metrics` - Retrieve current metrics
- `POST /model/{model_name}-{version}/set_new_metrics` - Update metrics with new data
- `GET /model/{model_name}-{version}/dataset` - Download dataset as CSV

### 4. Enhanced Components

#### JSON Text Field Component
**Location**: `src/components/JsonTextField.js`

**Features**:
- Real-time JSON validation
- Syntax error highlighting
- User-friendly error messages
- Monospace font for better JSON readability

#### Updated Navigation
- Added "Model Metrics" menu item with assessment icon
- Organized menu with logical grouping of features

## Technical Details

### Dependencies Added
- `@mui/x-date-pickers`: For date range selection
- `date-fns`: Date manipulation library

### State Management
- Uses React hooks for state management
- Implements proper loading states and error handling
- Provides user feedback for all operations

### Data Flow
1. **Metrics Update**: Frontend sends test data and expected results to backend
2. **Backend Processing**: Backend calls the model, compares results, calculates metrics
3. **Metrics Storage**: New metrics are saved with timestamps
4. **Dataset Download**: Backend queries MongoDB for model input data and returns CSV

## Usage Examples

### Updating Model Metrics

```json
// Example input instances
[
  {"feature1": 1.0, "feature2": 2.0, "feature3": 0.5},
  {"feature1": 1.5, "feature2": 2.5, "feature3": 0.8}
]

// Example expected results
[0, 1]
```

### Dataset Download
- **No Date Filter**: Downloads all input data for the model
- **With Date Filter**: Downloads data within the specified date range
- **Output Format**: CSV file with all input features sent to the model

## Error Handling

- **JSON Validation**: Real-time validation with helpful error messages
- **Network Errors**: User-friendly error messages for API failures
- **Loading States**: Visual feedback during operations
- **Success Messages**: Confirmation when operations complete successfully

## Future Enhancements

Potential areas for future development:
- **Metrics Visualization**: Charts and graphs for metrics trends over time
- **Automated Alerts**: Notifications when metrics drift beyond thresholds
- **Batch Processing**: Upload CSV files for bulk metrics calculations
- **Model Comparison**: Side-by-side metrics comparison between models
- **Export Options**: Additional export formats (JSON, Excel, etc.)
