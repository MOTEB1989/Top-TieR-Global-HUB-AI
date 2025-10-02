export default function Table({ columns, rows }: { columns: string[]; rows: any[] }) {
  return (
    <div className="overflow-auto border rounded">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50">
        <tr>{columns.map(c => <th key={c} className="px-3 py-2 text-left">{c}</th>)}</tr>
        </thead>
        <tbody>
        {rows.map((r, i) => (
          <tr key={i} className="odd:bg-white even:bg-gray-50">
            {columns.map(c => <td key={c} className="px-3 py-2">{String(r[c] ?? "")}</td>)}
          </tr>
        ))}
        </tbody>
      </table>
    </div>
  );
}
