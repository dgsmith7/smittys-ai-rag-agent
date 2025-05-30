# SARA - Smitty's AI RAG Agent

SARA is a Retrieval-Augmented Generation (RAG) agent that combines an Express.js API with a Python backend service to provide intelligent responses based on your data.

## Architecture

SARA consists of two main components:

1. **Express.js API Server** - Handles HTTP requests and manages communication with the RAG service
2. **Python RAG Service** - Long-running process that powers the RAG pipeline using phi3:mini model

The system uses inter-process communication to pass queries from the API to the Python service and receive responses.

## Features

- RESTful API for submitting questions to the RAG system
- Long-running Python process to maintain the RAG pipeline in memory
- Unique request ID tracking for asynchronous processing
- Health check endpoint for monitoring system status

## API Endpoints

### Query the RAG System

- **POST /api/query**
  - Request body: `{ "question": "Your question here" }`
  - Response: `{ "response": "Answer from RAG system", "processingTime": "123ms" }`

### Check System Health

- **GET /api/health**
  - Response: `{ "status": "ready" or "initializing", "model": "phi3:mini" }`

## Setup and Installation

1. Clone the repository:

   ```
   git clone https://github.com/dgsmith7/smittys-ai-rag-agent.git
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

4. Start the server:
   ```
   node app.js
   ```

## Requirements

- Node.js
- Python 3
- Express.js
- Required Python packages (see requirements.txt)

## Usage Example

```javascript
// Example API call using fetch
const response = await fetch("http://localhost:3000/api/query", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    question: "What information can you provide about this topic?",
  }),
});

const result = await response.json();
console.log(result.response);
```

## Technical Details

The system establishes a bidirectional communication channel between the Express server and the Python RAG service using Node.js child processes. Queries are tagged with unique request IDs to match responses with the corresponding requests asynchronously.

## License

[Add your license information here]

## Author

Created by David G. Smith (dgsmith7)
