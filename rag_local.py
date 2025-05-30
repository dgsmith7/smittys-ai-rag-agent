# rag_local.py
import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader # Or UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# Add imports for caching
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

# Set up in-memory cache for LLM responses
set_llm_cache(InMemoryCache())
# For persistent caching between restarts, use SQLiteCache instead:
# from langchain.cache import SQLiteCache
# set_llm_cache(SQLiteCache(database_path=".langchain.db"))

CHROMA_PATH = "chroma_db" # Directory to store ChromaDB data

load_dotenv() # Optional: Loads environment variables from.env file

DATA_PATH = "data/"

def load_documents():
    """Loads all PDF documents from the specified data path."""
    documents = []
    pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {DATA_PATH}")
        return documents
        
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            # loader = UnstructuredPDFLoader(pdf_path) # Alternative
            pdf_documents = loader.load()
            documents.extend(pdf_documents)
            print(f"Loaded {len(pdf_documents)} page(s) from {pdf_path}")
        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")
    
    print(f"Loaded a total of {len(documents)} page(s) from {len(pdf_files)} PDF file(s)")
    return documents

def split_documents(documents):
    """Splits documents into smaller chunks optimized for phi3:mini."""
    if not documents:
        print("No documents to split")
        return []
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Smaller chunks for phi3:mini's context window
        chunk_overlap=50,  # Reduced overlap for efficiency
        length_function=len,
        is_separator_regex=False,
    )
    all_splits = text_splitter.split_documents(documents)
    print(f"Split into {len(all_splits)} chunks")
    return all_splits

def get_embedding_function(model_name="nomic-embed-text"):
    """Initializes the Ollama embedding function."""
    # Ensure Ollama server is running (ollama serve)
    embeddings = OllamaEmbeddings(model=model_name)
    print(f"Initialized Ollama embeddings with model: {model_name}")
    return embeddings

def get_vector_store(embedding_function, persist_directory=CHROMA_PATH):
    """Initializes or loads the Chroma vector store."""
    if os.path.exists(persist_directory):
        try:
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_function
            )
            print(f"Vector store loaded from: {persist_directory}")
            return vectorstore
        except Exception as e:
            print(f"Error loading vector store: {e}")
            print("Creating a new vector store...")
            # If loading fails, we'll create a new one
    
    # Handle case where we need to create a new empty vectorstore
    # (either the directory doesn't exist or loading failed)
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function
    )
    vectorstore.persist()
    print(f"New empty vector store initialized at: {persist_directory}")
    return vectorstore

def index_documents(chunks, embedding_function, persist_directory=CHROMA_PATH):
    """Indexes document chunks into the Chroma vector store."""
    if not chunks:
        print("No document chunks to index")
        # Return an empty vector store
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_function
        )
        vectorstore.persist()
        return vectorstore
        
    print(f"Indexing {len(chunks)} chunks...")
    # Use from_documents for initial creation.
    # This will overwrite existing data if the directory exists but isn't a valid Chroma DB.
    # For incremental updates, initialize Chroma first and use vectorstore.add_documents().
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=persist_directory
    )
    vectorstore.persist() # Ensure data is saved
    print(f"Indexing complete. Data saved to: {persist_directory}")
    return vectorstore

def create_rag_chain(vector_store, llm_model_name="qwen3:14b", context_window=16384):
    """Creates the RAG chain."""
    # Initialize the LLM
    llm = ChatOllama(
        model=llm_model_name,
        temperature=0, # Lower temperature for more factual RAG answers 
        # you might want to experiment with other parameters (e.g., top_p, top_k) to optimize the behavior of the larger model.
        num_ctx=context_window # IMPORTANT: Set context window size
    )
    print(f"Initialized ChatOllama with model: {llm_model_name}, context window: {context_window}")

    # Create the retriever
    retriever = vector_store.as_retriever(
        search_type="similarity", # Or "mmr"
        search_kwargs={'k': 5} # Retrieve top 3 relevant chunks
    )
    print("Retriever initialized.")

    # Define the prompt template
    template = """Answer the question based ONLY on the following context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    print("Prompt template created.")

    # Define the RAG chain using LCEL
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG chain created.")
    return rag_chain

def create_optimized_rag_chain(vector_store, llm_model_name="phi3:mini", context_window=4096):
    """Creates an optimized RAG chain for CPU-only environments."""
    # Initialize the LLM with settings optimized for CPU
    llm = ChatOllama(
        model=llm_model_name,
        temperature=0,
        num_ctx=context_window,
        num_thread=4  # Limit threads for stable web serving
    )
    print(f"Initialized ChatOllama with model: {llm_model_name}, context window: {context_window}")
    
    # Use MMR retrieval with modest parameters for better relevance while controlling performance
    retriever = vector_store.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance for better diversity
        search_kwargs={
            'k': 3,         # Retrieve only 3 chunks for efficiency
            'fetch_k': 8,   # Consider 8 candidates initially
            'lambda_mult': 0.7  # Balance between relevance and diversity
        }
    )
    print("MMR Retriever initialized with performance settings.")
    
    # Use a simpler template that requires less computation
    template = """Answer the question based ONLY on this context:
{context}

Question: {question}

Keep your answer concise but informative.
"""
    prompt = ChatPromptTemplate.from_template(template)
    print("Prompt template created.")
    
    # Standard RAG chain without additional components
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("Optimized RAG chain created for CPU environment.")
    
    return rag_chain

def query_rag(chain, question):
    """Queries the RAG chain and prints the response."""
    print("\nQuerying RAG chain...")
    print(f"Question: {question}")
    response = chain.invoke(question)
    print("\nResponse:")
    print(response)

async def query_rag_async(chain, question):
    """Asynchronous version of query_rag for web applications."""
    print(f"Processing question asynchronously: {question}")
    response = await chain.ainvoke(question)
    return response

def initialize_rag_pipeline(model_name="phi3:mini", context_window=4096):
    """Pre-initializes the entire RAG pipeline for quick responses in web applications."""
    # 1. Get Embedding Function
    embedding_function = get_embedding_function()
    
    # 2. Load existing vector store (assumes documents are already indexed)
    vector_store = get_vector_store(embedding_function)
    
    # 3. Create optimized RAG chain
    rag_chain = create_optimized_rag_chain(
        vector_store, 
        llm_model_name=model_name, 
        context_window=context_window
    )
    
    return rag_chain

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Load Documents
    docs = load_documents()
    # 2. Split Documents
    chunks = split_documents(docs)
    # 3. Get Embedding Function
    embedding_function = get_embedding_function() # Using Ollama nomic-embed-text
    # 4. Index Documents (Only needs to be done once per document set)
    # Check if DB exists, if not, index. For simplicity, we might re-index here.
    # A more robust approach would check if indexing is needed.
    print("Attempting to index documents...")
    vector_store = index_documents(chunks, embedding_function)
    # To load existing DB instead:
    # vector_store = get_vector_store(embedding_function)
    # 5. Create RAG Chain - Using optimized chain with phi3:mini for CPU efficiency
    rag_chain = create_optimized_rag_chain(vector_store, llm_model_name="phi3:mini", context_window=4096)
    # 6. Query
    if docs:  # Only query if we have documents
        query_question = "Write the lyrics for a short psychedlic song or poem using the ones in the document for inspiration.  Be sure not to use too many phrases from one song - the inspiration should always be from more than one song.  And don't reveal the name of the inspiration source.  The only output should be the lyrics or poem itself." # Replace with a specific question
        query_rag(rag_chain, query_question)
    else:
        print("No documents loaded. RAG system is ready but has no knowledge base.")

    # query_question = "What is the main topic of the document?" # Replace with a specific question
    # query_rag(rag_chain, query_question)

    # query_question_2 = "Write the lyrics for a psychedlic poem using the ones in the document for inspiration." # Another example
    # query_rag(rag_chain, query_question_2)


# documents = load_documents() # Call this later
# loaded_docs = load_documents()
# chunks = split_documents(loaded_docs) # Call this later
# embedding_function = get_embedding_function() # Call this later
# embedding_function = get_embedding_function()
# vector_store = get_vector_store(embedding_function) # Call this later
# ... (previous function calls)
# vector_store = index_documents(chunks, embedding_function) # Call this for initial indexing
# ...To load an existing persistent database later:
# embedding_function = get_embedding_function()
# vector_store = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
#... (previous function calls)
# vector_store = get_vector_store(embedding_function) # Assuming DB is already indexed
# rag_chain = create_rag_chain(vector_store) # Call this later



