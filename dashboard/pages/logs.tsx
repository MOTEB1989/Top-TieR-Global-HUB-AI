import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function Logs() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6">
          <h1 className="text-2xl font-bold">Logs</h1>
          <p>عرض السجلات والمراقبة الحية</p>
        </div>
      </div>
    </div>
  );
}
