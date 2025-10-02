import { useState } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import Table from "../components/Table";

export default function KB() {
  const GW = process.env.NEXT_PUBLIC_GATEWAY_URL || process.env.GATEWAY_URL || "http://localhost:3000";

  const [query, setQuery] = useState("ما هي FastAPI؟");
  const [mode, setMode] = useState<"search" | "ask">("search");
  const [resp, setResp] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    try {
      const r = await axios.post(`${GW}/v1/kb/${mode}`, { query, top_k: 5 });
      setResp(r.data);
    } catch (e: any) {
      setResp({ error: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6 space-y-6">
          <h1 className="text-xl font-semibold">📚 Knowledge Base</h1>

          <div className="bg-white border rounded p-4 space-y-4">
            <div className="flex gap-3">
              <select className="border rounded px-2 py-1" value={mode} onChange={e => setMode(e.target.value as any)}>
                <option value="search">Search</option>
                <option value="ask">Ask (RAG)</option>
              </select>
              <button
                onClick={run}
                disabled={loading}
                className="px-3 py-1 rounded bg-black text-white"
              >
                {loading ? "Loading..." : "Run"}
              </button>
            </div>
            <input
              className="w-full border rounded p-2"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="اكتب استعلامك هنا..."
            />
          </div>

          {resp && (
            <div className="bg-white border rounded p-4">
              <h2 className="font-semibold mb-2">Results</h2>

              {resp.error && <p className="text-red-600">Error: {resp.error}</p>}

              {mode === "search" && resp.results && (
                <Table
                  columns={["id", "path", "chunk", "score"]}
                  rows={resp.results[0]?.map((_: any, i: number) => ({
                    id: resp.results.ids[0][i],
                    path: resp.results.metadatas[0][i]?.path,
                    chunk: resp.results.metadatas[0][i]?.chunk,
                    score: resp.results.distances[0][i]?.toFixed(4),
                  })) || []}
                />
              )}

              {mode === "ask" && (
                <div className="space-y-2">
                  <p className="text-gray-700 whitespace-pre-line">{resp.context}</p>
                  <details className="mt-2">
                    <summary className="cursor-pointer text-sm text-blue-600">Raw Data</summary>
                    <pre className="text-xs overflow-auto">{JSON.stringify(resp, null, 2)}</pre>
                  </details>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
