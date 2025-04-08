#!/bin/bash

# ========================
# OPEA Router Deploy Script
# ========================

# Load environment variables from a .env file if present
if [ -f .env ]; then
  echo "[INFO] Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

# Required variables
REQUIRED_VARS=("HF_TOKEN" "OPENAI_API_KEY")

# Validate that all required variables are set
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR}" ]; then
    echo "[ERROR] $VAR is not set. Please set it in your environment or .env file."
    exit 1
  fi
done

# Default values for Docker image
REGISTRY_AND_REPO=${REGISTRY_AND_REPO:-sapdai/refd}
TAG=${TAG:-agent-routing-service}

# Print summary
echo "[INFO] Starting deployment with the following config:"
echo "  Image: ${REGISTRY_AND_REPO}:${TAG}"
echo "  HF_TOKEN: ***${HF_TOKEN: -4}"
echo "  OPENAI_API_KEY: ***${OPENAI_API_KEY: -4}"
echo ""

# Compose up
echo "[INFO] Launching Docker Compose service..."
docker compose -f deployment/docker_compose/compose.yaml up --build -d

# Wait a moment then check status
sleep 2
docker ps --filter "name=opea_router"

echo "[SUCCESS] Router service deployed and running on http://localhost:6000"
