#!/usr/bin/env python3
"""
Initialize RAG Database - Run this script once to index your documents before using the API.
"""
import os
from rag_local import (
    load_documents,
    split_documents,
    get_embedding_function,
    index_documents
)

print("SARA RAG Indexing Script")
print("========================")

# Check if data directory exists
if not os.path.exists("data"):
    print("Creating data directory...")
    os.makedirs("data")
    print("Please place your documents in the 'data/' directory and run this script again.")
    exit(0)

# Check if there are documents to index
files = [f for f in os.listdir("data") if f.endswith(".pdf")]
if not files:
    print("No PDF files found in 'data/' directory.")
    print("Please add PDF files to the 'data/' directory and run this script again.")
    exit(0)

print(f"Found {len(files)} PDF files in data directory.")
print("Starting indexing process...")

try:
    # Initialize embedding function
    embedding_function = get_embedding_function()

    # Load documents
    docs = load_documents()
    
    # Split documents
    chunks = split_documents(docs)
    
    # Index documents
    vector_store = index_documents(chunks, embedding_function)
    
    print("\nIndexing complete! Your documents are now ready for querying via the API.")
    print("You can start the API with: npm start")

except Exception as e:
    print(f"Error during indexing: {str(e)}")
    exit(1)
