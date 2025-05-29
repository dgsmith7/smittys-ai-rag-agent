#!/bin/bash

# Check if Ollama is running, start if not
if ! pgrep -x "ollama" > /dev/null
then
    echo "Starting Ollama service..."
    ollama serve &
    # Wait for Ollama to initialize
    sleep 5
fi

# Start the Node.js Express API
echo "Starting SARA RAG Express API..."
node app.js
