#!/bin/bash

# Start script for Render deployment
echo "Starting Summer Siege API..."

# Use PORT environment variable provided by Render, default to 8000
PORT=${PORT:-8000}

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
