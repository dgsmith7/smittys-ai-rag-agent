#!/usr/bin/env python3
"""
Performance monitoring script for SARA RAG
"""
import time
import os
import psutil
import argparse
import asyncio
from rag_local import (
    get_embedding_function,
    get_vector_store,
    create_optimized_rag_chain,
    query_rag_async
)

def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # Convert to MB

async def run_benchmark(questions, num_runs=3):
    print("Initializing RAG pipeline...")
    start_time = time.time()
    
    # Initialize components
    embedding_function = get_embedding_function()
    vector_store = get_vector_store(embedding_function)
    rag_chain = create_optimized_rag_chain(vector_store)
    
    setup_time = time.time() - start_time
    print(f"Pipeline initialized in {setup_time:.2f} seconds")
    
    results = []
    for question in questions:
        print(f"\nBenchmarking question: {question}")
        question_times = []
        
        for i in range(num_runs):
            start_memory = get_memory_usage()
            start_time = time.time()
            
            response = await query_rag_async(rag_chain, question)
            
            end_time = time.time()
            end_memory = get_memory_usage()
            
            elapsed = end_time - start_time
            memory_delta = end_memory - start_memory
            
            print(f"Run {i+1}: {elapsed:.2f} seconds, Memory change: {memory_delta:.2f} MB")
            question_times.append(elapsed)
        
        avg_time = sum(question_times) / len(question_times)
        results.append({
            "question": question,
            "avg_time": avg_time,
            "min_time": min(question_times),
            "max_time": max(question_times)
        })
    
    return results

def display_results(results):
    print("\n=== BENCHMARK RESULTS ===")
    for r in results:
        print(f"\nQuestion: {r['question']}")
        print(f"Average processing time: {r['avg_time']:.2f} seconds")
        print(f"Min: {r['min_time']:.2f}s, Max: {r['max_time']:.2f}s")
    
    # Calculate overall average
    overall_avg = sum(r['avg_time'] for r in results) / len(results)
    print(f"\nOverall average: {overall_avg:.2f} seconds per question")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SARA RAG Performance Benchmark')
    parser.add_argument('--runs', type=int, default=3, 
                        help='Number of runs per question')
    args = parser.parse_args()
    
    # Sample questions for benchmarking
    sample_questions = [
        "What is the main topic of the document?",
        "Summarize the key points in the document.",
        "Extract the most important entities mentioned in the text."
    ]
    
    print("Starting SARA RAG benchmark...")
    results = asyncio.run(run_benchmark(sample_questions, args.runs))
    display_results(results)
