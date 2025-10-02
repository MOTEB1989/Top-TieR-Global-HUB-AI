import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import axios from "axios";
import { pipeline } from "@xenova/transformers";
import { ChromaClient } from "chromadb";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const port = Number(process.env.PORT || 3000);

const client = new ChromaClient({ path: process.env.KB_PATH || ".kb_store" });
const collectionName = process.env.KB_COLLECTION || "lexcode_kb";

let embedder: any = null;
async function getEmbedder() {
  if (!embedder) {
    embedder = await pipeline("feature-extraction", "Xenova/all-MiniLM-L6-v2");
  }
  return embedder;
}

app.post("/v1/kb/search", async (req, res) => {
  try {
    const { query, top_k = 5 } = req.body as { query?: string; top_k?: number };

    if (!query) {
      return res.status(400).json({ error: "query required" });
    }

    const coll = await client.getOrCreateCollection({ name: collectionName });
    const embModel = await getEmbedder();
    const embedding = await embModel(query, { pooling: "mean", normalize: true });
    const data = (embedding.data ?? []) as Iterable<number>;
    const vector = Array.from(data);

    const results = await coll.query({
      queryEmbeddings: [vector],
      nResults: top_k
    });

    return res.json({ query, results });
  } catch (error: any) {
    const message = error?.message ?? "kb_search_failed";
    return res.status(500).json({ error: message });
  }
});

app.post("/v1/kb/ask", async (req, res) => {
  try {
    const { query, top_k = 5 } = req.body as { query?: string; top_k?: number };

    if (!query) {
      return res.status(400).json({ error: "query required" });
    }

    const searchResponse = await axios.post(
      `http://localhost:${port}/v1/kb/search`,
      { query, top_k }
    );

    const documents = searchResponse.data?.results?.documents ?? [];
    const context = Array.isArray(documents[0]) ? documents[0].join("\n\n") : "";

    return res.json({
      query,
      context,
      refs: searchResponse.data?.results
    });
  } catch (error: any) {
    const message = error?.message ?? "kb_ask_failed";
    return res.status(500).json({ error: message });
  }
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.listen(port, () => {
  console.log(`Gateway listening on port ${port}`);
});
