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
print("RAG pipeline ready to serve requests!")

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
    # Test the service
    question = "What is this document about?"
    response = run_query(question)
    print(f"Question: {question}")
    print(f"Response: {response}")
