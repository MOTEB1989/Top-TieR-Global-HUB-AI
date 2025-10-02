import { useState } from "react";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import Table from "../components/Table";

export default function Databases() {
  const GW = process.env.NEXT_PUBLIC_GATEWAY_URL || process.env.GATEWAY_URL || "http://localhost:3000";
  const [db, setDb] = useState("sqlite");
  const [sql, setSql] = useState("SELECT name FROM sqlite_master;");
  const [rows, setRows] = useState<any[]>([]);
  const [cols, setCols] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    const r = await axios.post(`${GW}/v1/db/sql`, { db, sql });
    setRows(r.data.rows || []);
    setCols(r.data.columns || []);
    setLoading(false);
  };

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6 space-y-4">
          <div className="bg-white p-4 border rounded space-y-3">
            <div className="flex gap-3">
              <select className="border rounded px-2 py-1" value={db} onChange={e => setDb(e.target.value)}>
                {["sqlite","postgres","mysql"].map(x => <option key={x}>{x}</option>)}
              </select>
              <button onClick={run} className="px-3 py-1 rounded bg-black text-white" disabled={loading}>
                {loading ? "Running..." : "Run SQL"}
              </button>
            </div>
            <textarea className="w-full border rounded p-2 font-mono text-sm" rows={6}
                      value={sql} onChange={e => setSql(e.target.value)} />
          </div>
          <Table columns={cols} rows={rows} />
        </div>
      </div>
    </div>
  );
}
