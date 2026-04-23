#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'


echo ${GREEN} "Applying migrations..." ${NC}
alembic upgrade head


echo ${GREEN} "Starting application in $ENVIRONMENT mode..." ${NC}
echo ${GREEN} "Host: 0.0.0.0, Port: $BACKEND_PORT" ${NC}

case "$ENVIRONMENT" in
  development)
    echo ${GREEN} "Development mode with auto-reload enabled" ${NC}
    exec uvicorn src.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload
    ;;
    
  production)
    echo ${GREEN} "Production mode with $BACKEND_WORKERS workers" ${NC}
    exec uvicorn src.main:app --host 0.0.0.0 --port $BACKEND_PORT --workers $BACKEND_WORKERS
    ;;
    
  *)
    echo "Unknown ENVIRONMENT: $ENVIRONMENT"
    exit 1
    ;;
esac
