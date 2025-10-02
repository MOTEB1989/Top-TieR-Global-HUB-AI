import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function Models() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6">
          <h1 className="text-2xl font-bold">Models</h1>
          <p>هنا إدارة مزودي النماذج (OpenAI / HF / Anthropic)</p>
        </div>
      </div>
    </div>
  );
}
