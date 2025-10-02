import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function RAG() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6">
          <h1 className="text-2xl font-bold">RAG Query</h1>
          <p>هنا لاحقاً نربط /v1/rag/query API</p>
        </div>
      </div>
    </div>
  );
}
