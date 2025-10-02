import Link from "next/link";

const links = [
  { href: "/", label: "Home" },
  { href: "/observability", label: "Observability" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 border-r min-h-screen p-4 space-y-2">
      <h2 className="text-lg font-semibold">Dashboard</h2>
      <nav className="flex flex-col space-y-2">
        {links.map((link) => (
          <Link key={link.href} href={link.href} className="text-sm text-blue-600 hover:underline">
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
