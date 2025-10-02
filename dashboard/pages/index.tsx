import useSWR from "swr";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import ChartMini from "../components/Chart";

const fetcher = (url: string) => axios.get(url).then(r => r.data);

export default function Home() {
  const GW = process.env.NEXT_PUBLIC_GATEWAY_URL || process.env.GATEWAY_URL || "http://localhost:3000";
  const { data } = useSWR(`${GW}/v1/db/healthmap`, fetcher, { refreshInterval: 5000 });

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 min-h-screen bg-gray-100">
        <Navbar />
        <div className="p-6 grid gap-6 md:grid-cols-2">
          <div className="bg-white p-4 rounded border">
            <h2 className="font-semibold mb-2">Services Health</h2>
            <pre className="text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>
          </div>
          <div className="bg-white p-4 rounded border h-64">
            <h2 className="font-semibold mb-2">Traffic</h2>
            <div className="h-48"><ChartMini data={[5,9,7,12,8,13,11]} /></div>
          </div>
        </div>
      </div>
    </div>
  );
}
