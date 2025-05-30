#!/usr/bin/env python3
"""
RAG service module - Exposes RAG functionality for Node.js Express API
"""
import os
import asyncio
from rag_local import (
    get_embedding_function, 
    get_vector_store, 
    create_optimized_rag_chain,
    query_rag_async
)

# Initialize pipeline components once
print("Initializing RAG pipeline components...")
embedding_function = get_embedding_function(model_name="nomic-embed-text")
vector_store = get_vector_store(embedding_function)
rag_chain = create_optimized_rag_chain(
    vector_store, 
    llm_model_name="phi3:mini", 
    context_window=4096
)
print("RAG pipeline ready to serve requests!", flush=True)

async def process_query(question):
    """Process a single query and return the response"""
    try:
        response = await query_rag_async(rag_chain, question)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# Helper to run async functions from sync code
def run_query(question):
    return asyncio.run(process_query(question))

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
                    
                    # Process the query asynchronously
                    response = loop.run_until_complete(process_query(question))
                    
                    # Send the response back with the request ID
                    # Format: "RESPONSE:requestId:result"
                    print(f"RESPONSE:{request_id}:{response}")
                    sys.stdout.flush()  # Ensure output is sent immediately
    except KeyboardInterrupt:
        print("RAG service shutting down...")
    finally:
        loop.close()
