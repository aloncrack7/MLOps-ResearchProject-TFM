import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, File
from mlflow.tracking import MlflowClient
from mlflow.models.model import get_model_info
import os
import socket
import httpx
import re
import sqlite3
import time
import logging
from pymongo import MongoClient
import json
import base64
from bson import ObjectId
import pandas as pd
from fastapi.responses import StreamingResponse
import io
from uptime_kuma_api import UptimeKumaApi, MonitorType
import subprocess
from data_degradation_detector import report, multivariate as mv
import zipfile
import numpy as np
from sklearn import metrics as sk_metrics
from datetime import datetime, timedelta

from sklearn import metrics as sk_metrics

metric_function_mapping = {
    # Classification Metrics
    "accuracy_score": sk_metrics.accuracy_score,
    "accuracy": sk_metrics.accuracy_score,

    "balanced_accuracy_score": sk_metrics.balanced_accuracy_score,
    "balanced_accuracy": sk_metrics.balanced_accuracy_score,

    "f1_score": sk_metrics.f1_score,
    "f1": sk_metrics.f1_score,

    "fbeta_score": sk_metrics.fbeta_score,
    "fbeta": sk_metrics.fbeta_score,

    "precision_score": sk_metrics.precision_score,
    "precision": sk_metrics.precision_score,

    "recall_score": sk_metrics.recall_score,
    "recall": sk_metrics.recall_score,

    "jaccard_score": sk_metrics.jaccard_score,
    "jaccard": sk_metrics.jaccard_score,

    "cohen_kappa_score": sk_metrics.cohen_kappa_score,
    "kappa": sk_metrics.cohen_kappa_score,

    "confusion_matrix": sk_metrics.confusion_matrix,
    "cm": sk_metrics.confusion_matrix,

    "classification_report": sk_metrics.classification_report,
    "report": sk_metrics.classification_report,

    "matthews_corrcoef": sk_metrics.matthews_corrcoef,
    "mcc": sk_metrics.matthews_corrcoef,

    "hamming_loss": sk_metrics.hamming_loss,
    "hinge_loss": sk_metrics.hinge_loss,

    "zero_one_loss": sk_metrics.zero_one_loss,

    "top_k_accuracy_score": sk_metrics.top_k_accuracy_score,
    "top_k_accuracy": sk_metrics.top_k_accuracy_score,

    "multilabel_confusion_matrix": sk_metrics.multilabel_confusion_matrix,

    # Probabilistic Metrics
    "roc_auc_score": sk_metrics.roc_auc_score,
    "auc": sk_metrics.roc_auc_score,  # Common alias
    "roc_auc": sk_metrics.roc_auc_score,

    "average_precision_score": sk_metrics.average_precision_score,
    "ap": sk_metrics.average_precision_score,

    "log_loss": sk_metrics.log_loss,
    "cross_entropy": sk_metrics.log_loss,

    "brier_score_loss": sk_metrics.brier_score_loss,
    "brier": sk_metrics.brier_score_loss,

    "class_likelihood_ratios": sk_metrics.class_likelihood_ratios,

    # Ranking Metrics
    "dcg_score": sk_metrics.dcg_score,
    "ndcg_score": sk_metrics.ndcg_score,
    "dcg": sk_metrics.dcg_score,
    "ndcg": sk_metrics.ndcg_score,

    # Regression Metrics
    "mean_squared_error": sk_metrics.mean_squared_error,
    "mse": sk_metrics.mean_squared_error,

    "root_mean_squared_error": sk_metrics.mean_squared_error,  # will apply sqrt
    "rmse": sk_metrics.mean_squared_error,

    "mean_squared_log_error": sk_metrics.mean_squared_log_error,
    "msle": sk_metrics.mean_squared_log_error,

    "root_mean_squared_log_error": sk_metrics.mean_squared_log_error,  # will apply sqrt
    "rmsle": sk_metrics.mean_squared_log_error,

    "mean_absolute_error": sk_metrics.mean_absolute_error,
    "mae": sk_metrics.mean_absolute_error,

    "median_absolute_error": sk_metrics.median_absolute_error,
    "medae": sk_metrics.median_absolute_error,

    "mean_absolute_percentage_error": sk_metrics.mean_absolute_percentage_error,
    "mape": sk_metrics.mean_absolute_percentage_error,

    "explained_variance_score": sk_metrics.explained_variance_score,
    "explained_variance": sk_metrics.explained_variance_score,

    "r2_score": sk_metrics.r2_score,
    "r2": sk_metrics.r2_score,

    "max_error": sk_metrics.max_error,

    "mean_gamma_deviance": sk_metrics.mean_gamma_deviance,
    "mean_pinball_loss": sk_metrics.mean_pinball_loss,
    "mean_poisson_deviance": sk_metrics.mean_poisson_deviance,
    "mean_tweedie_deviance": sk_metrics.mean_tweedie_deviance,

    "d2_log_loss_score": sk_metrics.d2_log_loss_score,
    "d2_absolute_error_score": sk_metrics.d2_absolute_error_score,
    "d2_pinball_score": sk_metrics.d2_pinball_score,
    "d2_tweedie_score": sk_metrics.d2_tweedie_score,
}

logger = logging.getLogger("uvicorn.error")

def _get_free_port():
    """
    Get a free port within the exposed range (start_port-end_port)
    """
    start_port = os.environ.get('START_PORT')
    end_port = os.environ.get('END_PORT')
    
    if start_port is None or end_port is None:
        raise RuntimeError("START_PORT and END_PORT environment variables must be set")
    
    for port in range(int(start_port), int(end_port)):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                s.listen(1)
                s.close()
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free ports available in range {start_port}-{end_port}")

def _get_db_connection():
    conn = sqlite3.connect('/app/model_deployment.db')
    conn.row_factory = sqlite3.Row
    return conn

def _init_database():
    """
    Initialize the database with the required schema if it doesn't exist
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    # Create the table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_deployment (
            id text PRIMARY KEY,
            model_name text NOT NULL,
            model_version text NOT NULL,
            port int NOT NULL,
            run_uuid text NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def _load_deployed_models():
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM model_deployment")

        models = cursor.fetchall()
        deployed_models = dict()
        for model in models:
            deployed_models[model['id']] = {
                "model_name": model['model_name'],
                "version": model['model_version'],
                "port": model['port'],
                "run_uuid": model['run_uuid']
            }
        conn.close()
        return deployed_models
    except sqlite3.OperationalError as e:
        # If table doesn't exist, initialize it and return empty dict
        if "no such table" in str(e):
            _init_database()
            return {}
        else:
            raise e

def _check_database_mongo():
    try:
        # Build connection string with authentication
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        mongodb_user = os.environ.get('MONGODB_USER')
        mongodb_password = os.environ.get('MONGODB_PASSWORD')
        mongodb_database = os.environ.get('MONGODB_DATABASE', 'mlflow')
        
        # If we have credentials, use them
        if mongodb_user and mongodb_password:
            # Replace the URI to include authentication
            if mongodb_uri.startswith('mongodb://'):
                mongodb_uri = f"mongodb://{mongodb_user}:{mongodb_password}@mongodb:27017/{mongodb_database}?authSource=admin"
            else:
                mongodb_uri = f"mongodb://{mongodb_user}:{mongodb_password}@mongodb:27017/{mongodb_database}?authSource=admin"
        
        client = MongoClient(mongodb_uri)
        db = client[mongodb_database]
        
        # Test the connection by listing collections
        db.list_collection_names()
        client.close()

        logger.info(f"MongoDB connection successful")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")

def _monitor_exists(api, name):
    monitors = api.get_monitors()
    return any(m['name'] == name for m in monitors)

# Initialize the database and load deployed models
_init_database()
app = FastAPI()
client = MlflowClient()
deployed_models = _load_deployed_models()
_check_database_mongo()

def _reload_deployed_models():
    for model in deployed_models:
        # Check if the port is actually being used by the model service
        logger.info(f"Checking if model {model} is running on port {deployed_models[model]['port']}")
        port_status = subprocess.run(["nmap", "-p", str(deployed_models[model]['port']), "localhost"], capture_output=True, text=True)
        if port_status.returncode != 0 or "closed" in port_status.stdout:
            logger.warning(f"Model {model} is not running on port {deployed_models[model]['port']}")
            # If not running, try to restart it
            logger.info(f"Attempting to restart model {model} on port {deployed_models[model]['port']}")
            # Model is not running, restart it
            env_vars = {
                'VIRTUAL_ENV': '/app/venv',
                'PATH': '/app/venv/bin:' + os.environ.get('PATH', ''),
                'MLFLOW_DISABLE_ENV_CREATION': 'true'
            }
            env_str = ' '.join([f'{k}={v}' for k, v in env_vars.items()])
            
            result = os.system(f"bash -c '{env_str} mlflow models serve -m runs:/{deployed_models[model]['run_uuid']}/model -p {deployed_models[model]['port']} --host 0.0.0.0 --no-conda &'")
            if result != 0:
                print(f"Warning: Failed to restart model {model} on port {deployed_models[model]['port']}")
            else:
                retries = 60
                running = False
                while retries>0 and not running:
                    port_status = subprocess.run(["nmap", "-p", str(deployed_models[model]['port']), "localhost"], capture_output=True, text=True)
                    if port_status.returncode == 0 and "open" in port_status.stdout:
                        logger.info(f"Model {model} restarted successfully on port {deployed_models[model]['port']}")
                        running = True
                    retries -= 1
                    time.sleep(1)

                if retries == 0:
                    logger.error(f"Failed to restart model {model} on port {deployed_models[model]['port']} after multiple attempts")                

                with UptimeKumaApi('http://uptime-kuma:3001') as api:
                    uptime_kuma_user = os.getenv("UPTIME_KUMA_USER")
                    uptime_kuma_password = os.getenv("UPTIME_KUMA_PASSWORD")
                    api.login(uptime_kuma_user, uptime_kuma_password)
                    monitor = {
                        "type": MonitorType.HTTP,
                        "name": f"{deployed_models[model]['model_name']} version {deployed_models[model]['version']}",
                        "url": f"http://model_deployment:8000/{model}"
                    }

                    if not _monitor_exists(api, monitor["name"]):
                        api.add_monitor(**monitor)
                        logger.info(f"Monitor '{monitor['name']}' registered in Uptime Kuma.")
                    else:
                        logger.info(f"Monitor '{monitor['name']}' already exists in Uptime Kuma. Skipping registration.")

_reload_deployed_models()

@app.get("/get_model_list")
def get_model_list():
    """
    Retrieve the list of models available in the MLflow tracking server.
    """
    try:
        model_list = client.search_registered_models()
        return [model.name for model in model_list]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_model_version_list/{model_name}")
def get_model_version_list(model_name: str):
    """
    Retrieve the list of versions for a specific model.
    """
    try:
        model_versions = client.search_model_versions(f"name='{model_name}'")
        return [version.version for version in model_versions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_info/{model_name}/{version}")
def get_model_python_version(model_name: str, version: str):
    """
    Get the Python version used to train a specific model version.
    """
    try:
        model_versions = client.search_model_versions(f"name='{model_name}'")
        run_uuid = None
        for mv in model_versions:
            if str(mv.version) == version:
                run_uuid = mv.run_id
                break
        
        if run_uuid is None:
            raise HTTPException(status_code=404, detail=f"Model version {version} not found for model {model_name}")

        model_info = get_model_info(f"runs:/{run_uuid}/model")
        client.download_artifacts(run_uuid, "model/requirements.txt", dst_path="/tmp")

        with open("/tmp/requirements.txt", "r") as f:
            requirements = f.readlines()

        os.system("rm /tmp/requirements.txt")
        
        # Get model info which contains metadata including Python version
        return requirements
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Python version for model {model_name} version {version}: {str(e)}")

@app.get("/model/{model_name}-{version}/initial_report/download")
async def download_initial_report(model_name: str, version: str):
    """
    Download the initial report of a model as a zip file.
    """
    try:
        report_files = initial_report(model_name, version)
        if "files" not in report_files or not report_files["files"]:
            raise HTTPException(status_code=404, detail=f"Initial report for model {model_name} version {version} not found")

        # Create a zip file from the report files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in report_files["files"]:
                if file["type"] == "json":
                    zip_file.writestr(file["filename"], json.dumps(file["content"], indent=4))
                elif file["type"] == "png":
                    zip_file.writestr(file["filename"], base64.b64decode(file["content"]))

        zip_buffer.seek(0)
        return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={model_name}-{version}-initial_report.zip"})
    
    except Exception as e:
        logger.error(f"Error downloading initial report for model {model_name} version {version}: {str(e)}")
        

@app.get("/model/{model_name}-{version}/initial_report")
def initial_report(model_name: str, version: str):
    """
    Get the initial report of a model
    """

    try:        
        model_name_and_version = f"{model_name}-{version}"
        if model_name_and_version not in deployed_models:
            raise HTTPException(status_code=404, detail=f"Model {model_name_and_version} not found")
        
        report_path = f"/app/models/{model_name}-{version}/initial_report"
        if not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail=f"Initial report for model {model_name} version {version} not found")

        # Collect all .json and .png files in the report directory
        files = []
        for filename in os.listdir(report_path):
            file_path = os.path.join(report_path, filename)
            if filename.endswith('.json'):
                with open(file_path, 'r') as f:
                    files.append({
                    "filename": filename,
                    "type": "json",
                    "content": json.load(f)
                    })
            elif filename.endswith('.png'):
                with open(file_path, 'rb') as f:
                    files.append({
                    "filename": filename,
                    "type": "png",
                    "content": base64.b64encode(f.read()).decode('utf-8')
                    })

        return {"files": files}

    except Exception as e:
        logger.error(f"Error retrieving initial report for model {model_name} version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving initial report for model {model_name} version {version}")


@app.post("/deploy/{model_name}/{version}")
async def deploy(model_name: str, version: str, request: Request):
    """
    Deploy a specific version of a model.
    """

    try:        
        # Get the run UUID from the model and version
        model_versions = client.search_model_versions(f"name='{model_name}'")
        run_uuid = None
        for mv in model_versions:
            if str(mv.version) == version:
                run_uuid = mv.run_id
                break

        if run_uuid is None:
            raise HTTPException(status_code=404, detail=f"Model version {version} not found for model {model_name}")

        logger.info(f"Deploying model {model_name} version {version} with run UUID {run_uuid}")

        # Download the dataset.csv artifact from MLflow for this run
        os.makedirs(f"/app/models/{model_name}-{version}/initial", exist_ok=True)
        os.makedirs(f"/app/models/{model_name}-{version}/data", exist_ok=True)
        dataset_path = client.download_artifacts(run_uuid, "data/dataset.csv", dst_path=f"/app/models/{model_name}-{version}")
        logger.info(f"Dataset downloaded to {dataset_path}")
        X = pd.read_csv(dataset_path)
        logger.info(f"Dataset shape: {X.shape}")
        metrics = client.get_run(run_uuid).data.metrics
        logger.info(f"Metrics for model {model_name} version {version}: {metrics}")

        try:
            report.create_initial_report(X, metrics, f"/app/models/{model_name}-{version}/initial_report", int(request.query_params.get("number_of_output_classes", None)))
        except Exception as e:
            logger.error(f"Error creating initial report for model {model_name} version {version}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating initial report for model {model_name} version {version}: {str(e)}")
        
        port = _get_free_port()

        logger.info(f"Deploying model {model_name} version {version} on port {port}")
        client.download_artifacts(run_uuid, "model/requirements.txt", dst_path=f"/app/models/{model_name}-{version}")
        logger.info(f"Downloaded requirements.txt for model {model_name} version {version}")

        try:
            with open(f"/app/models/{model_name}-{version}/requirements.txt", "a+") as f:
                f.write("\nboto3\nhdfs\n")
                f.seek(0)
                requirements = f.readlines()
                logger.info(f"Requirements for {model_name} version {version}: {requirements}")
        except Exception as e:
            raise HTTPException(status_code=504, detail=f"Requirements file not found for model {model_name} version {version}, {str(e)}")

        logger.info(f"Starting deployment for model {model_name} version {version} on port {port}")
        # Create the virtual environment
        os.system(f"""mkdir -p /app/models/{model_name}-{version} && \
            python -m venv /app/models/{model_name}-{version}/venv && \
            bash -c 'source /app/models/{model_name}-{version}/venv/bin/activate && pip install -r /app/models/{model_name}-{version}/requirements.txt'""")
        logger.info(f"Virtual environment created for model {model_name} version {version}")
        
        # Start the model service and check if it actually started
        # Use the existing virtual environment and set MLflow to not create new environments
        env_vars = {
            'VIRTUAL_ENV': f'/app/models/{model_name}-{version}/venv',
            'PATH': f'/app/models/{model_name}-{version}/venv/bin:' + os.environ.get('PATH', ''),
            'MLFLOW_DISABLE_ENV_CREATION': 'true'
        }
        env_str = ' '.join([f'{k}={v}' for k, v in env_vars.items()])
        
        result = os.system(f"bash -c '{env_str} mlflow models serve -m runs:/{run_uuid}/model -p {port} --host 0.0.0.0 --no-conda &'")
        logger.info(f"Model service started with result code: {result}")
        if result != 0:
            raise HTTPException(status_code=500, detail=f"Failed to start model service for {model_name} version {version}")
        
        # Wait a moment for the service to start and check if it's actually running
        retries = 60
        running = False
        while retries > 0 and not running:
            # Check if the port is actually being used
            port_status = subprocess.run(["nmap", "-p", str(port), "localhost"], capture_output=True, text=True)
            logger.info(f"Port status for {port}: {port_status.stdout}")
            logger.info(f"Port status return code: {port_status.returncode}")

            if port_status.returncode == 0 and "open" in port_status.stdout:
                logger.info(f"Model service is running on port {port} for {model_name} version {version}")
                running = True

            retries -= 1
            time.sleep(1)

        if retries == 0:
            raise HTTPException(status_code=500, detail=f"Model service failed to start on port {port} for {model_name} version {version}")

        # If the port is not open, raise an error
        if port_status.returncode != 0 or "closed" in port_status.stdout:
            raise HTTPException(status_code=500, detail=f"Model service failed to start on port {port} for {model_name} version {version}")
        
        # Save to database
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO model_deployment (id, model_name, model_version, port, run_uuid) VALUES (?, ?, ?, ?, ?)",
            (f"{model_name}-{version}", model_name, version, port, run_uuid)
        )
        conn.commit()
        conn.close()
        
        # Update in-memory dictionary
        deployed_models[f"{model_name}-{version}"] = {
            "model_name": model_name,
            "version": version,
            "port": port,
            "run_uuid": run_uuid
        }

        with UptimeKumaApi('http://uptime-kuma:3001') as api:
            uptime_kuma_user = os.getenv("UPTIME_KUMA_USER")
            uptime_kuma_password = os.getenv("UPTIME_KUMA_PASSWORD")
            api.login(uptime_kuma_user, uptime_kuma_password)
            monitor = {
                "type": MonitorType.HTTP,
                "name": f"{model_name} version {version}",
                "url": f"http://model_deployment:8000/{model_name}-{version}/health"
            }

            if not _monitor_exists(api, monitor["name"]):
                api.add_monitor(**monitor)
                logger.info(f"Monitor '{monitor['name']}' registered in Uptime Kuma.")
            else:
                logger.info(f"Monitor '{monitor['name']}' already exists in Uptime Kuma. Skipping registration.")

        return {"message": f"Model {model_name} version {version} deployed on port {port}"}
    except Exception as e:
        logger.error(f"Error deploying model {model_name} version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_deployed_models")
def get_deployed_models():
    """
    Get the list of deployed models.
    """
    return deployed_models

@app.post("/undeploy/{model_name_and_version}")
def undeploy(model_name_and_version: str):
    """
    Undeploy a specific version of a model.
    """
    try:
        if model_name_and_version not in deployed_models:
            raise HTTPException(status_code=404, detail=f"Model {model_name_and_version} not found")
        
        # Kill the process
        os.system(f"pkill -f 'mlflow models serve -m runs:/{deployed_models[model_name_and_version]['run_uuid']}/model -p {deployed_models[model_name_and_version]['port']}'")
        
        # Remove from database
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM model_deployment WHERE id = ?", (model_name_and_version,))
        conn.commit()
        conn.close()
        
        # Remove from in-memory dictionary
        del deployed_models[model_name_and_version]

        # Remove monitor from Uptime Kuma
        with UptimeKumaApi('http://uptime-kuma:3001') as api:
            uptime_kuma_user = os.getenv("UPTIME_KUMA_USER")
            uptime_kuma_password = os.getenv("UPTIME_KUMA_PASSWORD")
            api.login(uptime_kuma_user, uptime_kuma_password)
            monitors = api.get_monitors()
            monitor_name = f"{model_name_and_version}"
            for monitor in monitors:
                if monitor['name'] == monitor_name:
                    api.delete_monitor(monitor['id'])
                    logger.info(f"Monitor '{monitor_name}' removed from Uptime Kuma.")
                    break

        os.rmdir(f"/app/models/{model_name_and_version}")

        logger.info(f"Model {model_name_and_version} undeployed successfully.")
        
        return {"message": f"Model {model_name_and_version} undeployed"}
    except Exception as e:
        logger.error(f"Error undeploying model {model_name_and_version}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_number_free_ports")
async def get_number_free_ports():
    """
    Get the number of free ports.
    """
    try:
        start_port = os.getenv('START_PORT')
        end_port = os.getenv('END_PORT')

        print(f"start_port: {start_port}\nend_port: {end_port}")
        if start_port is None or end_port is None:
            raise HTTPException(status_code=500, detail="START_PORT or END_PORT environment variables not set\n" + f"start_port: {start_port}\nend_port: {end_port}")
        
        total_ports = int(end_port) - int(start_port)
        used_ports = len(deployed_models)
        free_ports = total_ports - used_ports
        
        print(f"total_ports: {total_ports}, used_ports: {used_ports}, free_ports: {free_ports}")
        
        return free_ports
    except Exception as e:
        print(f"Error in get_number_free_ports: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error calculating free ports: {str(e)}")

# Type mapping from Python types to MLflow types
PYTHON_TO_MLFLOW_TYPES = {
    "str": {
        "mlflow_type": "1",
        "example": "hello world",
        "notes": "Standard Python string"
    },
    "int": {
        "mlflow_type": "2",
        "example": 42,
        "notes": "64-bit integers"
    },
    "numpy.int32": {
        "mlflow_type": "3",
        "example": "np.int32(42)",
        "notes": "32-bit integers"
    },
    "float": {
        "mlflow_type": "4",
        "example": 3.14159,
        "notes": "64-bit float (MLflow DataType.double)"
    },
    "numpy.float32": {
        "mlflow_type": "5",
        "example": "np.float32(3.14)",
        "notes": "32-bit floats"
    },
    "bool": {
        "mlflow_type": "6",
        "example": True,
        "notes": "Standard Python boolean"
    },
    "numpy.bool_": {
        "mlflow_type": "7",
        "example": "np.bool_(True)",
        "notes": "NumPy boolean"
    },
    "datetime": {
        "mlflow_type": "8",
        "example": "pd.Timestamp('2023-01-01')",
        "notes": "Pandas timestamp"
    },
    "bytes": {
        "mlflow_type": "9",
        "example": "b'binary data'",
        "notes": "Standard Python bytes"
    },
    "bytearray": {
        "mlflow_type": "10",
        "example": "bytearray(b'data')",
        "notes": "Python bytearray"
    },
    "numpy.bytes_": {
        "mlflow_type": "11",
        "example": "np.bytes_(b'data')",
        "notes": "NumPy bytes"
    },
    "DataType.double": {
        "mlflow_type": "4",
        "example": 3.14159,
        "notes": "64-bit float (MLflow DataType.double)"
    },
    "double": {
        "mlflow_type": "4",
        "example": 3.14159,
        "notes": "64-bit float (MLflow DataType.double)"
    },
    "DataType.long": {
        "mlflow_type": "2",
        "example": 42,
        "notes": "64-bit integer (MLflow DataType.long)"
    },
    "long": {
        "mlflow_type": "2",
        "example": 42,
        "notes": "64-bit integer (MLflow DataType.long)"
    }
}

@app.get("/model/{model_name}-{version}/signature")
async def get_model_signature(model_name: str, version: str):
    """
    Get the signature of a model.
    """
    try:
        model_versions = client.search_model_versions(f"name='{model_name}'")
        run_uuid = None
        for mv in model_versions:
            if str(mv.version) == version:
                run_uuid = mv.run_id
                break
        
        if run_uuid is None:
            raise HTTPException(status_code=404, detail=f"Model version {version} not found for model {model_name}")

        model_info = get_model_info(f"runs:/{run_uuid}/model")
        signature = model_info.signature
        
        return {
            "model_name": model_name,
            "version": version,
            "signature": {
                "inputs": [{"name": inp.name, "type": str(inp.type)} for inp in signature.inputs] if signature.inputs else [],
                "outputs": [{"name": out.name, "type": str(out.type)} for out in signature.outputs] if signature.outputs else [],
                "params": [{"name": param.name, "type": str(param.type)} for param in signature.params] if signature.params else []
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/type_mapping")
async def get_type_mapping():
    """
    Get the complete Python to MLflow type mapping with examples.
    """
    return {
        "python_to_mlflow_types": PYTHON_TO_MLFLOW_TYPES,
        "description": "Mapping of Python types to MLflow types with examples and notes"
    }

def _clean_dataset(dataset):
    """
    Clean the dataset: convert cursor to list and ObjectId to str, then extract instances as rows.
    Returns a list of dicts (each instance as a row).
    """
    data = []
    for doc in dataset:
        doc = dict(doc)
        # Convert ObjectId to string
        if '_id' in doc and isinstance(doc['_id'], ObjectId):
            doc['_id'] = str(doc['_id'])
        data.append(doc)

    logger.info(f"Data has been converted to list")

    results = []
    for doc in data:
        logger.info(f"Doc: {doc}")
        data_field = doc.get("data", {})
        logger.info(f"Data: {data_field}")
        # Check if data_field is a dict before calling .get
        if isinstance(data_field, dict):
            instances = data_field.get("instances", [])
        else:
            instances = []
        logger.info(f"Instances: {instances}")
        for instance in instances:
            # If instance is a dict of features, just append it
            # If instance is a dict with a "data" key, use instance["data"]["features"]
            if isinstance(instance, dict):
                if "data" in instance and "features" in instance["data"]:
                    results.append(instance["data"]["features"])
                else:
                    results.append(instance)
            else:
                results.append(instance)

    logger.info(f"Results has been converted to list")

    return results  # This is now JSON serializable

@app.get("/model/{model_name}-{version}/dataset")
async def get_dataset(model_name: str, version: str, request: Request):
    """
    Get a dataset from the model usage as a CSV file.
    """
    try:
        mongodb_uri = os.environ.get('MONGODB_URI')
        mongodb_user = os.environ.get('MONGODB_USER')
        mongodb_password = os.environ.get('MONGODB_PASSWORD')
        mongodb_database = os.environ.get('MONGODB_DATABASE', 'mlflow')

        # If we have credentials, use them
        if mongodb_user and mongodb_password:
            # Build the connection string with authentication
            mongodb_uri = f"mongodb://{mongodb_user}:{mongodb_password}@mongodb:27017/{mongodb_database}?authSource=admin"

        client = MongoClient(mongodb_uri)   
        db = client[mongodb_database]

        # Extract query parameters from the request
        query_params = dict(request.query_params)
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')

        if start_date is None or end_date is None:
            dataset = db.inputed_data.find({"model_name": model_name, "version": version})
        else:
            dataset = db.inputed_data.find({"model_name": model_name, "version": version, "timestamp": {"$gte": start_date, "$lte": end_date}})
        rows = _clean_dataset(dataset)
        if not rows:
            return Response(content="", media_type="text/csv")
        df = pd.DataFrame(rows)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        return StreamingResponse(stream, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={model_name}-{version}-dataset.csv"})
    except Exception as e:
        logger.error(f"Error retrieving dataset for model {model_name} version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _save_inputed_data_to_mongo(model_name, version, data):
    """
    Save the inputed data to MongoDB.
    """
    try:
        mongodb_uri = os.environ.get('MONGODB_URI')
        mongodb_user = os.environ.get('MONGODB_USER')
        mongodb_password = os.environ.get('MONGODB_PASSWORD')
        mongodb_database = os.environ.get('MONGODB_DATABASE', 'mlflow')
        
        # If we have credentials, use them
        if mongodb_user and mongodb_password:
            # Build the connection string with authentication
            mongodb_uri = f"mongodb://{mongodb_user}:{mongodb_password}@mongodb:27017/{mongodb_database}?authSource=admin"
        
        client = MongoClient(mongodb_uri)
        db = client[mongodb_database]

        # Decode the data from bytes to JSON
        try:
            decoded_data = json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Could not decode data as JSON, storing as string: {e}")
            decoded_data = data.decode('utf-8', errors='ignore')

        # Save the decoded data to MongoDB
        result = db.inputed_data.insert_one({
            "model_name": model_name,
            "version": version,
            "data": decoded_data,
            "timestamp": time.time()
        })
        
        logger.info(f"Data saved to MongoDB with ID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"Error saving inputed data to MongoDB: {e}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the service is running.
    """

    try:
        response = {
            "status": "ok",
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/{model_name}-{version}/metrics")
async def get_metrics(model_name: str, version: str):
    """
    Get the metrics of a model.
    """
    try:
        with open(f"/app/models/{model_name}-{version}/initial_report/base_metrics.json", "r") as f:
            metrics = json.load(f)
        return metrics

    except Exception as e:
        logger.error(f"Error getting metrics for model {model_name} version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating metrics for model {model_name} version {version}: {str(e)}")

@app.get("/model/{model_name}-{version}/new_metrics_file_name")
async def get_new_metrics_files(model_name: str, version: str):
    """
    Get the list of new metrics files for a model.
    """
    try:
        report_path = f"/app/models/{model_name}-{version}/report"
        if not os.path.exists(report_path):
            return {"files": []}
            
        files = [
            file for file in os.listdir(report_path)
            if file.startswith("metrics_at_") and file.endswith(".json")
        ]
        return {"files": files}

    except Exception as e:
        logger.error(f"Error getting new metrics files for model {model_name} version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting new metrics files for model {model_name} version {version}: {str(e)}")

@app.get("/model/{model_name}-{version}/new_metrics/{filename}")
async def get_new_metrics_file(model_name: str, version: str, filename: str):
    """
    Get a specific new metrics file content for a model.
    """
    try:
        file_path = f"/app/models/{model_name}-{version}/report/{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Metrics file {filename} not found for model {model_name} version {version}")
            
        with open(file_path, "r") as f:
            metrics = json.load(f)
        return metrics

    except Exception as e:
        logger.error(f"Error getting new metrics file {filename} for model {model_name} version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting new metrics file {filename} for model {model_name} version {version}: {str(e)}")

@app.post("/model/{model_name}-{version}/set_new_metrics")
async def update_metrics(model_name: str, version: str, request: Request):
    """
    Update the metrics of a model.
    """
    try:
        model_name_and_version = f"{model_name}-{version}"
        if model_name_and_version not in deployed_models:
            raise HTTPException(status_code=404, detail=f"Model {model_name_and_version} not found")

        request_body = await request.body()
        logger.info(f"Request body: {request_body}")
        # Parse the request body as JSON and extract 'instances'
        body_json = json.loads(request_body)
        logger.info(f"Parsed body JSON: {body_json}")
        instances = body_json.get("instances", [])
        logger.info(f"Instances: {instances}")
        results = body_json.get("results", [])
        logger.info(f"Results: {results}")

        # Redirect the call to /{model_name}-{version}/invocations using the correct port
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                f"http://localhost:8000/{model_name}-{version}/invocations",
                headers={"Content-Type": "application/json"},
                content=json.dumps({"instances": instances}).encode('utf-8')
            )
        predictions = Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )

        expected = np.array(results)
        logger.info(f"Expected results: {expected}")
        # Parse the predictions response as JSON and extract "predictions"
        predictions_json = json.loads(response.content)
        obtain = np.array(predictions_json.get("predictions", []))
        logger.info(f"Obtained results: {obtain}")

        # Calculate metrics
        with open(f"/app/models/{model_name}-{version}/initial_report/base_metrics.json", "r") as f:
            base_metrics = json.load(f)
        logger.info(f"Base metrics: {base_metrics}")

        # Get the name of the metric in base_metrics
        metric_names = list(base_metrics.keys())
        
        calculated_metrics = {}
        for name in metric_names:
            metric_fn = metric_function_mapping.get(name)
            if metric_fn is not None:
                try:
                    score = metric_fn(expected, obtain)
                    calculated_metrics[name] = score
                    logger.info(f"Metric {name}: {score}")
                except Exception as metric_error:
                    logger.warning(f"Could not calculate metric {name}: {metric_error}")
            else:
                logger.warning(f"Metric function for {name} not found.")

        timestamp = body_json.get("timestamp", time.time())
        metrics_at_path = f"/app/models/{model_name}-{version}/report/metrics_at_{timestamp}.json"
        with open(metrics_at_path, "w") as f:
            json.dump(calculated_metrics, f, indent=4)

        return calculated_metrics

    except Exception as e:
        logger.error(f"Error updating metrics for model {model_name} version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating metrics for model {model_name} version {version}: {str(e)}")

@app.get("/model/{model_name}-{version}/degradation_report")
async def get_degradation_report(model_name: str, version: str):
    """
    Get the degradation report of a model.
    """
    try:
        model_name_and_version = f"{model_name}-{version}"
        if model_name_and_version not in deployed_models:
            raise HTTPException(status_code=404, detail=f"Model {model_name_and_version} not found")
        
        timestamp = time.strftime("%y_%m_%d")
        report_path = f"/app/models/{model_name}-{version}/report_degradation_{timestamp}"

        if os.path.exists(report_path):
            # If the report already exists, return it as a zip file
            zip_stream = open(f"{report_path}.zip", "rb")
            return StreamingResponse(zip_stream, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={os.path.basename(report_path)}.zip"})

        original_dataset = pd.read_csv(f"/app/models/{model_name}-{version}/initial_report/data/dataset.csv")

        with open(f"/app/models/{model_name}-{version}/initial_report/kmeans_clusters.json", "r") as f:
            original_cluster_stats = mv.get_cluster_info_from_json(json.load(f))
        # Generate datasets for last week, month, year, and ever

        now = datetime.utcnow()
        date_ranges = {
            "week": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
            "month": (now - timedelta(days=30)).strftime("%Y-%m-%d"),
            "year": (now - timedelta(days=365)).strftime("%Y-%m-%d"),
            "ever": None
        }

        datasets = []
        for _period, start_date in date_ranges.items():
            if start_date:
                # Query for this period
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.get(
                        f"http://localhost:8000/model/{model_name}-{version}/dataset",
                        params={"start_date": start_date, "end_date": now.strftime("%Y-%m-%d")}
                    )
                if response.status_code == 200 and response.content:
                    datasets.append(pd.read_csv(io.StringIO(response.text)))
            else:
                # "ever" means all data
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.get(
                        f"http://localhost:8000/model/{model_name}-{version}/dataset"
                    )
                if response.status_code == 200 and response.content:
                    datasets.append(pd.read_csv(io.StringIO(response.text)))

        with open(f"/app/models/{model_name}-{version}/initial_report/base_metrics.json", "r") as f:
            metrics = json.load(f)

        new_metrics = []
        for file in os.listdir(f"/app/models/{model_name}-{version}/report"):
            if file.startswith("metrics_at_") and file.endswith(".json"):
                with open(f"/app/models/{model_name}-{version}/report/{file}", "r") as f:
                    new_metrics.append(json.load(f))

        report.create_report(original_dataset, original_cluster_stats, datasets, metrics, report_path, new_metrics)

        # Create a zip file of the report
        os.system(f"zip -r {report_path}.zip {report_path}")

        # Return the zip file as a download
        zip_stream = open(f"{report_path}.zip", "rb")
        return StreamingResponse(zip_stream, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={os.path.basename(report_path)}.zip"})
    except Exception as e:
        logger.error(f"Error getting degradation report for model {model_name} version {version}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting degradation report for model {model_name} version {version}: {str(e)}")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_model(request: Request, path: str):
    """
    Dynamic routing to deployed models.
    Expects URL format: /{model_name}-{version}/{rest_of_path}
    """
    try:
        # Parse the path to extract model name and version
        path_parts = path.lstrip('/').split('/', 1)
        model_key = path_parts[0]
        
        logger.info(f"Path: {path}")
        logger.info(f"Model key: {model_key}")

        if model_key not in deployed_models:
            raise HTTPException(status_code=404, detail=f"Model {model_key} not deployed")
        
        model_info = deployed_models[model_key]
        target_port = model_info["port"]
        
        # Construct the target URL
        target_path = f"/{path_parts[1]}" if len(path_parts) > 1 else "/"
        target_url = f"http://localhost:{target_port}{target_path}"

        # Get the request body
        body = await request.body()
        # Forward the request to the deployed model
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                params=dict(request.query_params),
                content=body
            )
        
        logger.info(f"Proxy response status: {response.status_code}")
        logger.info(f"Proxy response content: {response.content}")
        logger.info(f"Proxy response headers: {response.headers}")

        if request.method == "POST" and path.endswith("/invocations"):
            model_name = model_key.split("-")[0]
            model_version = model_key.split("-")[1]
            _save_inputed_data_to_mongo(model_name, model_version, body)
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
