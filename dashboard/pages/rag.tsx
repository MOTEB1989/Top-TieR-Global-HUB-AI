import { useState } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function RAG() {
  const GW = process.env.NEXT_PUBLIC_GATEWAY_URL || process.env.GATEWAY_URL || "http://localhost:3000";
  const [query, setQuery] = useState("ما هو LexCode؟");
  const [provider, setProvider] = useState("openai");
  const [resp, setResp] = useState<any>(null);

  const run = async () => {
    const r = await axios.post(`${GW}/v1/rag/query`, { query, provider, top_k: 3 });
    setResp(r.data);
  };

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6 space-y-4">
          <div className="bg-white p-4 border rounded space-y-3">
            <div className="flex gap-3">
              <select className="border rounded px-2 py-1" value={provider} onChange={e => setProvider(e.target.value)}>
                {["openai","anthropic","huggingface"].map(x => <option key={x}>{x}</option>)}
              </select>
              <button onClick={run} className="px-3 py-1 rounded bg-black text-white">Ask</button>
            </div>
            <input className="w-full border rounded p-2" value={query} onChange={e => setQuery(e.target.value)} />
          </div>
          <pre className="bg-white p-4 border rounded text-xs overflow-auto">{JSON.stringify(resp, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
}
