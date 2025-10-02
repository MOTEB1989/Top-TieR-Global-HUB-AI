const Table = () => (
  <table className="w-full border">
    <thead>
      <tr className="bg-gray-200">
        <th className="p-2">ID</th>
        <th className="p-2">Name</th>
        <th className="p-2">Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td className="p-2">1</td>
        <td className="p-2">Example</td>
        <td className="p-2 text-green-500">Active</td>
      </tr>
    </tbody>
  </table>
);
export default Table;
