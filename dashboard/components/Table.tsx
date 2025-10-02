import { ReactNode } from "react";

type TableRow = Record<string, ReactNode>;

type TableProps = {
  columns: string[];
  rows: TableRow[];
};

export default function Table({ columns, rows }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {columns.map(column => (
              <th key={column} className="px-4 py-2 text-left font-medium text-gray-600 uppercase tracking-wider">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {rows.length === 0 ? (
            <tr>
              <td className="px-4 py-3 text-center text-gray-500" colSpan={columns.length}>
                No results yet.
              </td>
            </tr>
          ) : (
            rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {columns.map(column => (
                  <td key={column} className="px-4 py-2 text-gray-700 align-top whitespace-pre-wrap">
                    {row[column] as ReactNode}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
