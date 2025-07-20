#!/bin/bash

# Build script for Render deployment
set -o errexit  # exit on error

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
