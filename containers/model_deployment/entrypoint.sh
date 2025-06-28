#!/bin/bash

set -e

. /app/venv/bin/activate

# Run the FastAPI application with uvicorn
uvicorn deployments:app --host 0.0.0.0 --port 8000 --reload --workers 1
