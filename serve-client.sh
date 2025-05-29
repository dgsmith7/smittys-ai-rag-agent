#!/bin/bash
# Simple script to serve the client example HTML file on port 8080

echo "Starting a local HTTP server for client-example.html on port 8080..."
echo "You can access the example at: http://localhost:8080/client-example.html"
echo "Press Ctrl+C to stop the server."

# Check if Python 3 is available
if command -v python3 &>/dev/null; then
    python3 -m http.server 8080
elif command -v python &>/dev/null; then
    # Try regular python, which might be python3 on some systems
    python -m http.server 8080
else
    echo "Error: Python is not installed. Please install Python to use this script."
    exit 1
fi
