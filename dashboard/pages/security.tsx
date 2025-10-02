import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function Security() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6">
          <h1 className="text-2xl font-bold">Security</h1>
          <p>إدارة OAuth / JWT / API Keys</p>
        </div>
      </div>
    </div>
  );
}
