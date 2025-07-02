import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
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

# Initialize the database and load deployed models
_init_database()
app = FastAPI()
client = MlflowClient()
deployed_models = _load_deployed_models()
_check_database_mongo()

def _reload_deployed_models():
    for model in deployed_models:
        # Check if the port is actually being used by the model service
        if os.system(f"nmap -p {deployed_models[model]['port']} localhost") != 0:
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
                # Wait a moment and verify it started
                time.sleep(2)
                if os.system(f"lsof -i :{deployed_models[model]['port']}") != 0:
                    print(f"Warning: Model {model} failed to start on port {deployed_models[model]['port']}")

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

@app.post("/deploy/{model_name}/{version}")
def deploy(model_name: str, version: str):
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
        
        port = _get_free_port()

        # Create the virtual environment
        os.system(f"""mkdir -p /app/{model_name}-{version} && 
            python -m venv /app/{model_name}-{version}/venv && 
            source /app/{model_name}-{version}/venv/bin/activate && 
            pip install mlflow""")
        
        # Start the model service and check if it actually started
        # Use the existing virtual environment and set MLflow to not create new environments
        env_vars = {
            'VIRTUAL_ENV': f'/app/{model_name}-{version}/venv',
            'PATH': f'/app/{model_name}-{version}/venv/bin:' + os.environ.get('PATH', ''),
            'MLFLOW_DISABLE_ENV_CREATION': 'true'
        }
        env_str = ' '.join([f'{k}={v}' for k, v in env_vars.items()])
        
        result = os.system(f"bash -c '{env_str} mlflow models serve -m runs:/{run_uuid}/model -p {port} --host 0.0.0.0 --no-conda &'")
        print(f"Result: {result}")
        if result != 0:
            raise HTTPException(status_code=500, detail=f"Failed to start model service for {model_name} version {version}")
        
        # Wait a moment for the service to start and check if it's actually running
        time.sleep(2)
        
        # Check if the port is actually being used
        if os.system(f"nmap -p {port} localhost") != 0:
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
        
        return {"message": f"Model {model_name} version {version} deployed on port {port}"}
    except Exception as e:
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
        
        return {"message": f"Model {model_name_and_version} undeployed"}
    except Exception as e:
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

@app.post("/model/{model_name}-{version}")
async def call_model(model_name: str, version: str, request: Request):
    """
    Call a model.
    """

    logger.info(f"Calling model {model_name}-{version}")
    return await proxy_to_model(request, f"/{model_name}-{version}/invocations")

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
            _save_inputed_data_to_mongo(model_key, model_info["version"], body)
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
