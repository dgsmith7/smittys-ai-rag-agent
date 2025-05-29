"""
Utility to count tokens in text files for RAG pipeline.
Helps determine if content will fit within model context windows.
"""

def count_tokens_rough(text):
    """
    Get a rough estimate of tokens in text.
    For English text, this is approximately 4 characters per token on average.
    """
    return len(text) // 4

def count_tokens_by_words(text):
    """
    Count tokens based on word count.
    This is a simple approximation - tokens are typically 0.75 × words.
    """
    words = text.split()
    return int(len(words) * 1.3)  # Adding 30% to account for punctuation, etc.

def analyze_file_for_rag(file_path):
    """
    Analyze a text file for RAG pipeline compatibility.
    Provides token estimates and recommendations.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        char_count = len(text)
        word_count = len(text.split())
        token_estimate = count_tokens_by_words(text)
        
        # Model context windows
        phi3_mini_ctx = 4096
        qwen3_14b_ctx = 16384
        
        print(f"File: {file_path}")
        print(f"Character count: {char_count:,}")
        print(f"Word count: {word_count:,}")
        print(f"Estimated token count: {token_estimate:,}")
        print("\nContext window compatibility:")
        print(f"phi3:mini (4,096 tokens): {'EXCEEDS LIMIT' if token_estimate > phi3_mini_ctx else 'Compatible'}")
        print(f"qwen3:14b (16,384 tokens): {'EXCEEDS LIMIT' if token_estimate > qwen3_14b_ctx else 'Compatible'}")
        
        if token_estimate > phi3_mini_ctx:
            print("\nRecommendation for phi3:mini:")
            print(f"- Use chunking with max size of 500 tokens")
            print(f"- Expected chunks: ~{token_estimate // 500 + 1}")
            print("- Consider using MMR retrieval to reduce redundancy")
            
    except Exception as e:
        print(f"Error analyzing file: {e}")
        
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        analyze_file_for_rag(sys.argv[1])
    else:
        print("Usage: python count_tokens.py <file_path>")
        print("Example: python count_tokens.py data/master.txt")
