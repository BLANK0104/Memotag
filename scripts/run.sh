#!/bin/bash
# Script to run the Memotag API locally

# Load environment variables
set -a
source .env
set +a

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
  echo "No virtual environment detected. Activating..."
  if [ -d "venv" ]; then
    source venv/bin/activate
  else
    echo "No virtual environment found. Create one with:"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    exit 1
  fi
fi

# Create required directories if they don't exist
mkdir -p data/db data/recordings reports

# Run the application
echo "Starting Memotag API on $API_HOST:$API_PORT"
uvicorn src.api.main:app --reload --host $API_HOST --port $API_PORT
