const fs = require("fs");
const path = require("path");
const chokidar = require("chokidar"); // You may need to install this: npm install chokidar
const { ENDPOINTS } = require("./config");
const { loadVectorStore } = require("./vectorStore");

// Function to setup file watchers for all endpoint PDF directories
function setupFileWatchers() {
  console.log("Setting up file watchers for PDF directories...");

  Object.values(ENDPOINTS).forEach((endpointConfig) => {
    // Make sure directory exists
    if (!fs.existsSync(endpointConfig.pdfsDir)) {
      fs.mkdirSync(endpointConfig.pdfsDir, { recursive: true });
    }

    // Watch the PDF directory for changes
    const watcher = chokidar.watch(`${endpointConfig.pdfsDir}/**/*.pdf`, {
      persistent: true,
      ignoreInitial: true,
    });

    // When files are added, changed, or removed, update the vector store
    watcher
      .on("add", () => updateVectorStore(endpointConfig))
      .on("change", () => updateVectorStore(endpointConfig))
      .on("unlink", () => updateVectorStore(endpointConfig));

    console.log(`Watching ${endpointConfig.pdfsDir} for changes`);
  });
}

// Update the vector store when files change
async function updateVectorStore(endpointConfig) {
  console.log(
    `PDF changes detected for ${endpointConfig.endpoint}, updating vector store...`
  );
  await loadVectorStore(endpointConfig);
  console.log(`Vector store updated for ${endpointConfig.endpoint}`);
}

module.exports = {
  setupFileWatchers,
};
