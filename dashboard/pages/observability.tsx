import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function Observability() {
  const grafana = process.env.NEXT_PUBLIC_GRAFANA_URL || "http://localhost:3001";
  const dash = `${grafana}/d/-/home?orgId=1&refresh=10s`;

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6 space-y-4">
          <h1 className="text-xl font-semibold">Observability</h1>
          <iframe src={dash} className="w-full h-[80vh] border rounded" />
        </div>
      </div>
    </div>
  );
}
