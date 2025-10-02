import Link from "next/link";

const Sidebar = () => {
  const links = [
    { href: "/", label: "Home" },
    { href: "/databases", label: "Databases" },
    { href: "/rag", label: "RAG" },
    { href: "/models", label: "Models" },
    { href: "/security", label: "Security" },
    { href: "/logs", label: "Logs" }
  ];
  return (
    <div className="w-60 h-screen bg-gray-800 text-white p-4">
      <h1 className="text-2xl font-bold mb-6">LexCode</h1>
      <ul className="space-y-2">
        {links.map((link) => (
          <li key={link.href}>
            <Link href={link.href} className="hover:text-blue-400">{link.label}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
