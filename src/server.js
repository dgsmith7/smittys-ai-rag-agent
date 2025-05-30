const express = require("express");
const cors = require("cors");
const { Ollama } = require("langchain/llms/ollama");
const { RetrievalQAChain } = require("langchain/chains");
const fs = require("fs");
const path = require("path");

// Import our new modules
const { ENDPOINTS } = require("./config");
const { initializeVectorStores, getVectorStore } = require("./vectorStore");
const { setupFileWatchers } = require("./fileWatcher");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Generic query handler that works with any endpoint
async function handleQuery(req, res, endpoint) {
  try {
    const { query } = req.body;

    if (!query) {
      return res.status(400).json({ error: "Query is required" });
    }

    const vectorStoreData = getVectorStore(endpoint);

    if (!vectorStoreData || !vectorStoreData.store) {
      return res.status(500).json({
        error: `No vector store available for ${endpoint}. Make sure PDFs are loaded in the corresponding directory.`,
      });
    }

    const model = new Ollama({
      model: "llama3",
    });

    const chain = RetrievalQAChain.fromLLM(
      model,
      vectorStoreData.store.asRetriever()
    );

    // Use the endpoint-specific query blurb
    const fullQuery = `${vectorStoreData.queryBlurb}\n\nQuestion: ${query}`;

    const response = await chain.call({
      query: fullQuery,
    });

    res.json({
      answer: response.text,
      sourceEndpoint: endpoint,
    });
  } catch (error) {
    console.error("Error processing query:", error);
    res
      .status(500)
      .json({ error: "An error occurred while processing the query" });
  }
}

// Set up route handlers for each endpoint
Object.values(ENDPOINTS).forEach((endpointConfig) => {
  app.post(endpointConfig.endpoint, (req, res) => {
    handleQuery(req, res, endpointConfig.endpoint);
  });
});

// Start the server
async function startServer() {
  try {
    // Initialize vector stores for all endpoints
    await initializeVectorStores(ENDPOINTS);

    // Setup file watchers to monitor PDF changes
    setupFileWatchers();

    // Start the server
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
      console.log(
        `Available endpoints: ${Object.values(ENDPOINTS)
          .map((e) => e.endpoint)
          .join(", ")}`
      );
    });
  } catch (error) {
    console.error("Failed to start server:", error);
  }
}

startServer();
