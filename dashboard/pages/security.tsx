import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function Security() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6 space-y-4">
          <div className="bg-white p-4 border rounded space-y-2">
            <h2 className="font-semibold">Security</h2>
            <ul className="list-disc pl-6 text-sm">
              <li>OAuth (Google/GitHub/Facebook) — إضافة لاحقة.</li>
              <li>API Keys / JWT — عبر Gateway.</li>
              <li>Secrets — من GitHub/Codespaces أو .env.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
