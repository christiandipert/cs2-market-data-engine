#!/bin/bash

# kill all services if they are running
pkill -f "uvicorn routes:app"
pkill -f "npm start"

# start api services
echo "Starting FastAPI backend..."
cd data_fetch
uvicorn routes:app --reload &
BACKEND_PID=$!

# start webapp
echo "Starting React frontend..."
cd ../webapp
npm start &
FRONTEND_PID=$!

# handle script termination
trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM EXIT

# keep script running
wait 