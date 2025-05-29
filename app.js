// Express API for SARA RAG Agent
const express = require("express");
const { spawn } = require("child_process");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

// Start the Python RAG service as a long-running process
console.log("Starting RAG service...");
const ragService = spawn("python3", ["rag_service.py"]);

let serviceReady = false;

ragService.stdout.on("data", (data) => {
  console.log(`RAG service: ${data}`);
  if (data.toString().includes("ready to serve requests")) {
    serviceReady = true;
  }
});

ragService.stderr.on("data", (data) => {
  console.error(`RAG service error: ${data}`);
});

// Handle query with Python subprocess
async function queryRag(question) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python3", [
      "-c",
      `
import sys
from rag_service import run_query
question = """${question.replace(/"""/g, '\\"\\"\\"')}"""
print(run_query(question))
      `,
    ]);

    let result = "";

    pythonProcess.stdout.on("data", (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      console.error(`Error: ${data}`);
    });

    pythonProcess.on("close", (code) => {
      if (code === 0) {
        resolve(result.trim());
      } else {
        reject(`Process exited with code ${code}`);
      }
    });
  });
}

// API endpoint for queries
app.post("/api/query", async (req, res) => {
  if (!serviceReady) {
    return res.status(503).json({
      error: "RAG service is still initializing. Please try again in a moment.",
    });
  }

  const { question } = req.body;
  if (!question) {
    return res.status(400).json({ error: "Question is required" });
  }

  try {
    // Query the RAG service
    const startTime = Date.now();
    const response = await queryRag(question);
    const processingTime = Date.now() - startTime;

    res.json({
      response,
      processingTime: `${processingTime}ms`,
    });
  } catch (error) {
    res.status(500).json({ error: error.toString() });
  }
});

// Health check endpoint
app.get("/api/health", (req, res) => {
  res.json({
    status: serviceReady ? "ready" : "initializing",
    model: "phi3:mini",
  });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Express server running on port ${PORT}`);
});

// Handle graceful shutdown
process.on("SIGINT", () => {
  console.log("Shutting down...");
  if (ragService) {
    ragService.kill();
  }
  process.exit();
});
