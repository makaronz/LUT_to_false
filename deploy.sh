#!/bin/bash

# Simple deployment script for LUTcompareTool
# This script should be run on the server where you want to deploy the application

# Update repository
echo "Updating repository..."
git pull

# Install or update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Check if the Gunicorn process is already running
PID=$(pgrep -f "gunicorn.*lutcomparetool_app:app" || echo "")

if [ -n "$PID" ]; then
    echo "Stopping existing Gunicorn process (PID: $PID)..."
    kill $PID
    sleep 2
fi

# Create necessary directories if they don't exist
mkdir -p uploads reports

# Start the Gunicorn server in the background
echo "Starting Gunicorn server..."
nohup gunicorn --bind 0.0.0.0:8080 --workers 4 lutcomparetool_app:app > gunicorn.log 2>&1 &

echo "Deployment completed. The application should be available at http://your-server-ip:8080"
echo "Check gunicorn.log for any errors."
