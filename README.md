# SARA RAG Agent

SARA (Smart AI Retrieval Assistant) is a Retrieval-Augmented Generation (RAG) service that provides multiple specialized endpoints for different use cases.

## Overview

This service combines the power of local LLMs with vector databases to provide context-aware responses based on your own document collections. The system supports multiple specialized endpoints, each with its own document collection and response style.

## Features

- Multiple specialized endpoints for different use cases
- Each endpoint has its own:
  - Document collection (PDFs)
  - Vector store
  - Custom response style via query blurbs
- Fast responses with pre-loaded vector stores
- RESTful API interface
- Local execution with no data sent to external services

## Available Endpoints

- `/api/query` - General purpose queries
- `/api/paisley` - Psychedelic AI Song Lyric Engine
- `/api/sofia` - Sofia-specific services
- `/api/screenplay` - Screenplay writing and analysis
- `/api/haiku` - Haiku poetry generation
- `/api/arlene` - Arlene-specific services

See the [API documentation](docs.md) for detailed information about each endpoint.

## Installation

### Prerequisites

- Node.js v14+
- Python 3.8+
- Ollama with appropriate models installed

### Setup

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/smittys-ai-rag-agent.git
   cd smittys-ai-rag-agent
   ```

2. Install Node.js dependencies:

   ```
   npm install
   ```

3. Install Python dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Ensure Ollama is installed and running with required models:

   ```
   ollama pull phi3:mini
   ollama pull nomic-embed-text
   ```

5. Create the data directories (these will be created automatically on first run):

   ```
   mkdir -p data/general/pdfs
   mkdir -p data/paisley/pdfs
   mkdir -p data/sofia/pdfs
   mkdir -p data/screenplay/pdfs
   mkdir -p data/haiku/pdfs
   mkdir -p data/arlene/pdfs
   ```

6. Place your PDF documents in the appropriate directories.

## Usage

1. Start the service:

   ```
   npm start
   ```

2. The service will initialize vector stores for each endpoint based on the PDFs in their respective directories.

3. Make API requests to the desired endpoint:
   ```
   curl -X POST http://localhost:3000/api/paisley \
     -H "Content-Type: application/json" \
     -d '{"question": "Write me a song about moonlight"}'
   ```

## Customization

To customize each endpoint's behavior, edit the configuration in `src/config.js`. You can modify:

- Query blurbs to change how the AI responds
- Add new endpoints with unique behaviors
- Change document paths

## Directory Structure

```
smittys-ai-rag-agent/
├── app.js                # Main application file
├── rag_service.py        # Python RAG service
├── rag_local.py          # RAG utilities
├── src/
│   └── config.js         # Endpoint configurations
├── data/                 # Data directories
│   ├── general/pdfs/     # General PDFs
│   ├── paisley/pdfs/     # Paisley PDFs
│   ├── sofia/pdfs/       # Sofia PDFs
│   └── ...               # Other endpoint PDFs
├── docs.md               # API documentation
└── README.md             # This file
```

## License

[Your chosen license]
