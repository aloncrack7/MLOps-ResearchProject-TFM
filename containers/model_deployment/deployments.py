import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from mlflow.tracking import MlflowClient
import os
import socket
import httpx
import re
import sqlite3
import time

def _get_free_port():
    """
    Get a free port within the exposed range (8001-8100)
    """
    for port in range(8001, 8101):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                s.listen(1)
                s.close()
                return port
        except OSError:
            continue
    raise RuntimeError("No free ports available in range 8001-8100")

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

# Initialize the database and load deployed models
_init_database()
app = FastAPI()
client = MlflowClient()
deployed_models = _load_deployed_models()

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
            
            result = os.system(f"{env_str} mlflow models serve -m runs:/{deployed_models[model]['run_uuid']}/model -p {deployed_models[model]['port']} --host 0.0.0.0 --no-conda &")
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
        
        result = os.system(f"{env_str} mlflow models serve -m runs:/{run_uuid}/model -p {port} --host 0.0.0.0 --no-conda &")
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

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_model(request: Request, path: str):
    """
    Dynamic routing to deployed models.
    Expects URL format: /{model_name}-{version}/{rest_of_path}
    """
    try:
        # Parse the path to extract model name and version
        path_parts = path.split('/', 1)
        model_key = path_parts[0]
        
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
        
        return response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

