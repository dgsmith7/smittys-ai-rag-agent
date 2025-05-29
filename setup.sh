#!/bin/bash

# Setup script for SARA RAG Agent (both Python and Node.js components)
echo "Setting up SARA RAG Agent..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Check if Ollama is installed
if ! command -v ollama &> /dev/null
then
    echo "Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "Ollama installed successfully."
fi

# Pull required models
echo "Pulling required models (if needed)..."
ollama pull phi3:mini
ollama pull nomic-embed-text

# Ask if the user wants to initialize the database
read -p "Do you want to initialize the document database now? (y/n): " initialize
if [[ $initialize == "y" || $initialize == "Y" ]]; then
    # Check if Ollama is running
    if ! pgrep -x "ollama" > /dev/null; then
        echo "Starting Ollama service..."
        ollama serve &
        # Wait for Ollama to initialize
        sleep 5
    fi
    
    # Run the initialization script
    python initialize_db.py
fi

echo "Setup complete! You can now start the API with: npm start"
echo "Or run the Python version directly with: python rag_local.py"
