import Link from "next/link";
import clsx from "clsx";

const items = [
  { href: "/", label: "Overview" },
  { href: "/databases", label: "Databases" },
  { href: "/rag", label: "RAG" },
  { href: "/models", label: "Models" },
  { href: "/security", label: "Security" },
  { href: "/logs", label: "Logs" }
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-gray-100 min-h-screen p-4">
      <h1 className="text-xl font-semibold mb-6">LexCode Admin</h1>
      <nav className="space-y-2">
        {items.map(it => (
          <Link key={it.href} href={it.href} className={clsx(
            "block rounded px-3 py-2 hover:bg-gray-800"
          )}>{it.label}</Link>
        ))}
      </nav>
    </aside>
  );
}
