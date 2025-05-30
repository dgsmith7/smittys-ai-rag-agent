#!/usr/bin/env python3
"""
RAG service module - Exposes RAG functionality for Node.js Express API
"""
import os
import asyncio
import glob
from rag_local import (
    get_embedding_function, 
    get_vector_store,
    split_documents,
    create_optimized_rag_chain,
    query_rag_async
)
from langchain_community.document_loaders import PyPDFLoader

# Store vector stores and RAG chains by endpoint
vector_stores = {}
rag_chains = {}
endpoint_pdf_dirs = {}

# Initialize embedding function once
print("Initializing RAG pipeline components...")
embedding_function = get_embedding_function(model_name="nomic-embed-text")

# Default data directory (for backward compatibility)
DEFAULT_DATA_DIR = "data"

def load_documents_for_endpoint(pdf_dir):
    """Loads all PDF documents from the specified PDF directory."""
    documents = []
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return documents
        
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            pdf_documents = loader.load()
            documents.extend(pdf_documents)
            print(f"Loaded {len(pdf_documents)} page(s) from {pdf_path}")
        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")
    
    print(f"Loaded a total of {len(documents)} page(s) from {len(pdf_files)} PDF file(s)")
    return documents

def initialize_endpoint_vector_store(endpoint, pdf_dir):
    """Initialize vector store for a specific endpoint."""
    print(f"Initializing vector store for endpoint: {endpoint}, PDF dir: {pdf_dir}")
    
    # Create a unique persist directory for this endpoint
    persist_dir = f"chroma_db_{endpoint.replace('/', '_')}"
    
    # Load and index documents
    documents = load_documents_for_endpoint(pdf_dir)
    chunks = split_documents(documents)
    
    if not chunks:
        print(f"No documents to index for {endpoint}")
        # Initialize empty vector store
        vector_store = get_vector_store(embedding_function, persist_directory=persist_dir)
    else:
        # Index documents
        print(f"Indexing {len(chunks)} chunks for {endpoint}...")
        from langchain_community.vectorstores import Chroma
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_function,
            persist_directory=persist_dir
        )
        vector_store.persist()
    
    # Create RAG chain for this endpoint
    rag_chain = create_optimized_rag_chain(
        vector_store, 
        llm_model_name="phi3:mini", 
        context_window=4096
    )
    
    # Store in dictionaries
    vector_stores[endpoint] = vector_store
    rag_chains[endpoint] = rag_chain
    endpoint_pdf_dirs[endpoint] = pdf_dir
    
    print(f"Vector store for endpoint {endpoint} initialized successfully")
    return vector_store, rag_chain

# Initialize default vector store for backward compatibility
default_pdf_dir = os.path.join(DEFAULT_DATA_DIR, "general/pdfs")
if os.path.exists(default_pdf_dir):
    initialize_endpoint_vector_store("/api/query", default_pdf_dir)
else:
    print(f"Default PDF directory {default_pdf_dir} doesn't exist, creating empty vector store")
    os.makedirs(default_pdf_dir, exist_ok=True)
    initialize_endpoint_vector_store("/api/query", default_pdf_dir)

print("RAG pipeline ready to serve requests!", flush=True)

async def process_query(endpoint, question):
    """Process a single query using the appropriate endpoint's RAG chain"""
    try:
        # Use the specific endpoint's RAG chain if available, otherwise use default
        if endpoint in rag_chains:
            chain = rag_chains[endpoint]
        else:
            print(f"No RAG chain for endpoint {endpoint}, using default")
            chain = rag_chains.get("/api/query")
            
            # If even default is not available, create it
            if not chain:
                print("Default RAG chain not found, creating it")
                default_pdf_dir = os.path.join(DEFAULT_DATA_DIR, "general/pdfs")
                os.makedirs(default_pdf_dir, exist_ok=True)
                _, chain = initialize_endpoint_vector_store("/api/query", default_pdf_dir)
        
        if chain:
            response = await query_rag_async(chain, question)
            return response
        else:
            return "Error: No RAG chain available to process your query"
    except Exception as e:
        return f"Error: {str(e)}"

# Helper to run async functions from sync code
def run_query(endpoint, question):
    return asyncio.run(process_query(endpoint, question))

if __name__ == "__main__":
    # Run as a service that processes commands from stdin
    import sys
    
    print("RAG service is running and ready to process queries...", flush=True)
    
    # Create event loop for async operations
    loop = asyncio.get_event_loop()
    
    try:
        # Process input lines as they come in
        for line in sys.stdin:
            line = line.strip()
            
            # Command format: "QUERY:requestId:question"
            if line.startswith("QUERY:"):
                parts = line.split(":", 2)
                if len(parts) == 3:
                    command, request_id, question = parts
                    
                    # Extract endpoint from requestId if it includes it (format: endpoint|uniqueId)
                    if "|" in request_id:
                        endpoint, unique_id = request_id.split("|", 1)
                        request_id = unique_id  # Use only the unique part for the response
                    else:
                        endpoint = "/api/query"  # Default endpoint
                    
                    # Process the query asynchronously
                    response = loop.run_until_complete(process_query(endpoint, question))
                    
                    # Send the response back with the request ID
                    # Format: "RESPONSE:requestId:result"
                    print(f"RESPONSE:{request_id}:{response}")
                    sys.stdout.flush()  # Ensure output is sent immediately
            
            # Command format: "INIT:endpoint:pdfDir"
            elif line.startswith("INIT:"):
                parts = line.split(":", 2)
                if len(parts) == 3:
                    command, endpoint, pdf_dir = parts
                    
                    print(f"Received initialization command for {endpoint} with PDF dir {pdf_dir}")
                    
                    # Make sure the PDF directory exists
                    if not os.path.exists(pdf_dir):
                        os.makedirs(pdf_dir, exist_ok=True)
                        print(f"Created PDF directory: {pdf_dir}")
                    
                    # Initialize vector store for this endpoint
                    initialize_endpoint_vector_store(endpoint, pdf_dir)
                    
                    print(f"Initialization complete for {endpoint}")
                    sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("RAG service shutting down...")
    finally:
        loop.close()
