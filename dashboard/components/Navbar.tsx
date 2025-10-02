export default function Navbar() {
  return (
    <header className="w-full bg-white border-b px-4 py-3 flex items-center justify-between">
      <span className="font-medium">Dashboard</span>
      <div className="text-sm text-gray-500">Gateway ↔ {process.env.NEXT_PUBLIC_GATEWAY_URL || "env.GATEWAY_URL"}</div>
    </header>
  );
}
