import Link from "next/link";
import { useRouter } from "next/router";

const items = [
  { href: "/", label: "Overview" },
  { href: "/databases", label: "Databases" },
  { href: "/rag", label: "RAG" },
  { href: "/models", label: "Models" },
  { href: "/security", label: "Security" },
  { href: "/logs", label: "Logs" },
  { href: "/repo", label: "Repo Status" },
  { href: "/kb", label: "Knowledge Base" },
];

export default function Sidebar() {
  const router = useRouter();

  return (
    <aside className="w-64 min-h-screen border-r bg-gray-50 p-4 space-y-4">
      <h2 className="text-lg font-semibold">Top-TieR Dashboard</h2>
      <nav className="space-y-2">
        {items.map(item => {
          const active = router.pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded px-3 py-2 text-sm transition-colors ${
                active ? "bg-black text-white" : "text-gray-700 hover:bg-gray-200"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
