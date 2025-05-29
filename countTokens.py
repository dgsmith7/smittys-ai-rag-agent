import tiktoken

def count_tokens(filename):
    # Load the text from file
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # While phi3:mini has its own tokenizer, you can use cl100k_base for an approximation
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    return len(tokens)

token_count = count_tokens("./data/master.txt")
print(f"Approximate token count: {token_count}")