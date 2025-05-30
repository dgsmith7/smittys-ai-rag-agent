# SARA RAG API Documentation

This document outlines the available endpoints for the SARA RAG (Retrieval-Augmented Generation) API service.

## Overview

SARA RAG API is a service that provides AI-generated responses based on document queries. The service maintains separate vector stores for different domains, each with its own specialized knowledge and response style.

## Base URL

All endpoints are relative to the base URL of the deployed service, typically: `http://localhost:3000`

## Authentication

Currently, the API does not require authentication.

## Technical Implementation

The service architecture consists of:

1. A Node.js Express server (app.js) that handles HTTP endpoints
2. A Python service (rag_service.py) that manages the RAG functionality
3. Separate vector stores for each endpoint's document collection
4. Pre-initialized vector stores to minimize query latency

When the service starts:

- It creates all necessary data directories
- It sends initialization commands to prepare vector stores for each endpoint
- Vector stores are built from PDFs in each endpoint's directory

This architecture ensures fast response times while maintaining separation between different knowledge domains.

## Endpoints

### General Query Endpoint

- **Endpoint**: `/api/query`
- **Method**: POST
- **Description**: General purpose query endpoint for retrieving information from the default knowledge base.
- **Request Body**:
  ```json
  {
    "question": "Your question here"
  }
  ```
- **Response**:
  ```json
  {
    "response": "AI generated response",
    "processingTime": "1234ms",
    "endpoint": "/api/query"
  }
  ```
- **Data Directory**: `data/general/pdfs/`
- **Query Style**: General informative responses based on the provided documents.

### Paisley Endpoint

- **Endpoint**: `/api/paisley`
- **Method**: POST
- **Description**: Specialized endpoint for generating psychedelic song lyrics and poetry.
- **Request Body**:
  ```json
  {
    "question": "Write a song about cosmic rainbows"
  }
  ```
- **Response**: Same structure as general endpoint
- **Data Directory**: `data/paisley/pdfs/`
- **Query Style**: Generates psychedelic song lyrics and poetry based on provided documents for inspiration.

### Sofia Endpoint

- **Endpoint**: `/api/sofia`
- **Method**: POST
- **Description**: Specialized endpoint for Sofia-specific queries, using a custom knowledge base.
- **Request Body**:
  ```json
  {
    "question": "Your Sofia-related question here"
  }
  ```
- **Response**: Same structure as general endpoint
- **Data Directory**: `data/sofia/pdfs/`
- **Query Style**: Provides responses specific to Sofia services.

### Screenplay Endpoint

- **Endpoint**: `/api/screenplay`
- **Method**: POST
- **Description**: Specialized endpoint for screenplay writing and analysis queries.
- **Request Body**:
  ```json
  {
    "question": "Your screenplay-related question here"
  }
  ```
- **Response**: Same structure as general endpoint
- **Data Directory**: `data/screenplay/pdfs/`
- **Query Style**: Provides responses related to screenplay writing and analysis.

### Haiku Endpoint

- **Endpoint**: `/api/haiku`
- **Method**: POST
- **Description**: Specialized endpoint for haiku poetry queries. Responses may be formatted in haiku style.
- **Request Body**:
  ```json
  {
    "question": "Write a haiku about cherry blossoms"
  }
  ```
- **Response**: Same structure as general endpoint
- **Data Directory**: `data/haiku/pdfs/`
- **Query Style**: Generates responses in haiku style or about haiku poetry.

### Arlene Endpoint

- **Endpoint**: `/api/arlene`
- **Method**: POST
- **Description**: Specialized endpoint for Arlene-specific queries, using a custom knowledge base.
- **Request Body**:
  ```json
  {
    "question": "Your Arlene-related question here"
  }
  ```
- **Response**: Same structure as general endpoint
- **Data Directory**: `data/arlene/pdfs/`
- **Query Style**: Provides responses specific to Arlene services.

### Health Check Endpoint

- **Endpoint**: `/api/health`
- **Method**: GET
- **Description**: Provides information about the service status.
- **Response**:
  ```json
  {
    "status": "ready",
    "model": "phi3:mini",
    "endpoints": [
      "/api/query",
      "/api/paisley",
      "/api/sofia",
      "/api/screenplay",
      "/api/haiku",
      "/api/arlene"
    ]
  }
  ```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Missing or invalid parameters
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: Service is still initializing

Error responses will include a JSON object with an `error` field describing the issue.

## Document Management

Each endpoint has its own knowledge base, stored as PDFs in the corresponding directory:

- General: `data/general/pdfs/`
- Paisley: `data/paisley/pdfs/`
- Sofia: `data/sofia/pdfs/`
- Screenplay: `data/screenplay/pdfs/`
- Haiku: `data/haiku/pdfs/`
- Arlene: `data/arlene/pdfs/`

To update the knowledge base:

1. Add, remove, or modify PDFs in the appropriate directory
2. Restart the service to rebuild the vector stores
3. The changes will be automatically detected and indexed

## Example Usage

Using curl:

```bash
curl -X POST http://localhost:3000/api/haiku \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the elements of a haiku?"}'
```

Using JavaScript:

```javascript
fetch("http://localhost:3000/api/screenplay", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    question: "How do I format dialogue in a screenplay?",
  }),
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## Performance Considerations

- Vector stores are pre-initialized at startup to minimize query latency
- For very large PDF collections, initial startup time may be longer
- Changes to PDFs require a service restart to update the vector stores
