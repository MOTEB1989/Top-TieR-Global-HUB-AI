import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import axios from "axios";

export default function Logs() {
  const GW = process.env.NEXT_PUBLIC_GATEWAY_URL || process.env.GATEWAY_URL || "http://localhost:3000";
  const [healthmap, setHealthmap] = useState<any>(null);

  useEffect(() => {
    const id = setInterval(async () => {
      const r = await axios.get(`${GW}/v1/db/healthmap`);
      setHealthmap(r.data);
    }, 4000);
    return () => clearInterval(id);
  }, [GW]);

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6">
          <pre className="bg-white p-4 border rounded text-xs overflow-auto">{JSON.stringify(healthmap, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
}
