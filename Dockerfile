FROM node:18-slim

# Install Python and required libraries
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

# Copy package.json and install Node dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy Python requirements and install Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start Ollama service and the Node.js app
CMD bash -c "ollama serve & sleep 5 && node app.js"
