import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function Models() {
  const [cfg, setCfg] = useState({ openai_model: "gpt-4o-mini", hf_model: "gpt2", anthropic_model: "claude-3-opus-20240229" });

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <div className="p-6 space-y-4">
          <div className="bg-white p-4 border rounded space-y-3">
            <h2 className="font-semibold">Models Config (local state)</h2>
            <div className="grid md:grid-cols-3 gap-3">
              <input className="border rounded p-2" value={cfg.openai_model} onChange={e => setCfg({ ...cfg, openai_model: e.target.value })}/>
              <input className="border rounded p-2" value={cfg.hf_model} onChange={e => setCfg({ ...cfg, hf_model: e.target.value })}/>
              <input className="border rounded p-2" value={cfg.anthropic_model} onChange={e => setCfg({ ...cfg, anthropic_model: e.target.value })}/>
            </div>
            <p className="text-sm text-gray-500">يمكن لاحقًا ربط هذه الحقول بواجهة إعدادات حقيقية في الـ Gateway.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
