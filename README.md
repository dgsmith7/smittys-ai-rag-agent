# SARA - Smitty's AI RAG Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

SARA is a fully local Retrieval-Augmented Generation (RAG) system that allows you to query your documents using the power of AI, without sending your data to external services.

## Overview

SARA (Smitty's AI RAG Agent) is an optimized LLM pipeline that combines document processing, vector embeddings, and local language models to provide accurate, context-aware responses based on your documents. The system runs entirely on your machine, ensuring data privacy and reducing operational costs.

## Features

- **100% Local Processing**: All computations happen on your device
- **Document Indexing**: Load and process PDF files efficiently
- **Intelligent Chunking**: Optimized text splitting for better retrieval
- **Semantic Search**: Find relevant information using embeddings
- **Configurable Models**: Use different Ollama models based on your hardware
- **CPU & GPU Support**: Optimized for different hardware environments
- **Memory Efficient**: Works on systems with limited resources
- **Asynchronous Support**: Ready for web application integration

## System Requirements

### Minimum Requirements

- Python 3.9+
- 8GB RAM
- CPU with 4+ cores
- 2GB disk space (plus space for your documents)

### Recommended

- 16GB+ RAM
- Modern CPU with 8+ cores or Apple Silicon
- GPU support (for faster processing)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/dgsmith7/smittys-ai-rag-agent.git
   cd smittys-ai-rag-agent
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install [Ollama](https://ollama.com/):

   ```bash
   # macOS / Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

4. Download the required models:
   ```bash
   ollama pull phi3:mini
   ollama pull nomic-embed-text
   ```

## Usage

### Basic Operation

1. Place your PDF documents in the `data/` directory

2. Run the RAG pipeline:

   ```bash
   python rag_local.py
   ```

3. The system will:
   - Load your documents
   - Split them into chunks
   - Create embeddings
   - Index them in a vector database
   - Start an interactive query session

### Advanced Configuration

You can modify the following parameters in `rag_local.py`:

- **Model Selection**: Choose between `phi3:mini` (faster, lower resource usage) or `qwen3:14b` (better quality)
- **Chunking Strategy**: Adjust chunk size and overlap for different document types
- **Retrieval Parameters**: Configure number of chunks to retrieve and search strategy

### Web Application Integration

The system includes `query_rag_async()` for easy integration with web frameworks:

```python
from rag_local import create_optimized_rag_chain, get_vector_store, get_embedding_function, query_rag_async

# Initialize components
embedding_function = get_embedding_function()
vector_store = get_vector_store(embedding_function)
rag_chain = create_optimized_rag_chain(vector_store)

# Use in async web framework (FastAPI, etc.)
async def get_answer(question: str):
    return await query_rag_async(rag_chain, question)
```

## Performance Optimization

The repository includes two main configurations:

1. **High-Quality Mode**: Using `qwen3:14b` with larger context window (16,384 tokens)
2. **Resource-Efficient Mode**: Using `phi3:mini` with optimized parameters for CPU-only environments

Use the `count_tokens.py` utility to analyze your documents and determine the best configuration:

```bash
python count_tokens.py data/your_document.pdf
```

## Web API Integration

SARA includes a Node.js Express API for web integration:

### Node.js Express API Setup

1. Install Node.js dependencies:

   ```bash
   npm install
   ```

2. Start the Express API:
   ```bash
   npm start
   ```

The API will start a Python RAG service and expose the following endpoints:

- `POST /api/query`: Submit questions to the RAG system
- `GET /api/health`: Check API and RAG service health

### Example API Usage

```javascript
// Query the RAG system
fetch("http://localhost:3000/api/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ question: "What is this document about?" }),
})
  .then((response) => response.json())
  .then((data) => console.log(data.response));
```

### Quick Setup

The repository includes helper scripts to set up and run the system:

```bash
# Set up all components (Python and Node.js)
./setup.sh

# Alternatively, manually initialize the database
python initialize_db.py

# Start the Express API server
./start-api.sh  # or npm start

# Serve the client example on http://localhost:8080
./serve-client.sh
```

You can then access the client example at http://localhost:8080/client-example.html to test the API.

### Performance Testing

To evaluate how well the system performs on your hardware:

```bash
# Install psutil for memory tracking
pip install psutil

# Run the benchmark
python benchmark.py --runs 5
```

This will report average response times and memory usage for sample queries.

### Docker Deployment

You can deploy the system using Docker:

```bash
docker-compose up -d
```

This will:

1. Build the Docker image with Node.js, Python, and Ollama
2. Start the container with the API running on port 3000
3. Mount the `chroma_db` and `data` directories for persistence

## Project Structure

- `rag_local.py`: Main RAG implementation
- `rag_service.py`: Python service for Node.js integration
- `app.js`: Node.js Express API server
- `count_tokens.py`: Utility for analyzing document size
- `initialize_db.py`: Script to index documents before API usage
- `benchmark.py`: Performance testing utility
- `data/`: Directory for source documents
- `chroma_db/`: Vector store persistence
- `Dockerfile` & `docker-compose.yml`: Container configuration
- `client-example.html`: Simple web UI example for API testing

## Credits

This project was inspired by and adapted from [this freeCodeCamp article](https://www.freecodecamp.org/news/build-a-local-ai/#heading-how-to-build-a-local-rag-system-with-qwen-3).

## License

MIT License - See [LICENSE](LICENSE) for details
