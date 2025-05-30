const fs = require("fs");
const path = require("path");
const { DirectoryLoader } = require("langchain/document_loaders/fs/directory");
const { PDFLoader } = require("langchain/document_loaders/fs/pdf");
const { OllamaEmbeddings } = require("langchain/embeddings/ollama");
const { MemoryVectorStore } = require("langchain/vectorstores/memory");

// Store the vector stores in memory
const vectorStores = {};

// Function to create or update vector store for a specific endpoint
async function loadVectorStore(endpointConfig) {
  try {
    // Ensure the directories exist
    if (!fs.existsSync(endpointConfig.dataDir)) {
      fs.mkdirSync(endpointConfig.dataDir, { recursive: true });
    }

    if (!fs.existsSync(endpointConfig.pdfsDir)) {
      fs.mkdirSync(endpointConfig.pdfsDir, { recursive: true });
    }

    // Check if there are PDFs to load
    const pdfFiles = fs
      .readdirSync(endpointConfig.pdfsDir)
      .filter((file) => file.toLowerCase().endsWith(".pdf"));

    if (pdfFiles.length === 0) {
      console.log(`No PDFs found in ${endpointConfig.pdfsDir}`);
      return null;
    }

    // Load PDFs from directory
    const directoryLoader = new DirectoryLoader(endpointConfig.pdfsDir, {
      ".pdf": (path) => new PDFLoader(path),
    });

    console.log(`Loading PDFs from ${endpointConfig.pdfsDir}`);
    const docs = await directoryLoader.load();
    console.log(`Loaded ${docs.length} documents`);

    // Create vector store
    const vectorStore = await MemoryVectorStore.fromDocuments(
      docs,
      new OllamaEmbeddings({
        model: "nomic-embed-text",
      })
    );

    // Store the vector store with endpoint info
    vectorStores[endpointConfig.endpoint] = {
      store: vectorStore,
      queryBlurb: endpointConfig.queryBlurb,
    };

    console.log(`Vector store created for ${endpointConfig.endpoint}`);
    return vectorStore;
  } catch (error) {
    console.error(
      `Error creating vector store for ${endpointConfig.endpoint}:`,
      error
    );
    return null;
  }
}

// Initialize all vector stores
async function initializeVectorStores(endpoints) {
  console.log("Initializing vector stores for all endpoints...");
  const initPromises = Object.values(endpoints).map((endpointConfig) =>
    loadVectorStore(endpointConfig)
  );

  await Promise.all(initPromises);
  console.log("All vector stores initialized");
}

// Get a specific vector store by endpoint
function getVectorStore(endpoint) {
  return vectorStores[endpoint];
}

module.exports = {
  loadVectorStore,
  initializeVectorStores,
  getVectorStore,
};
