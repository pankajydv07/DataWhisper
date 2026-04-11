export function ResultTable({
  table,
}: {
  table: { columns: string[]; rows: unknown[][] }
}) {
  return (
    <div className="mt-4 overflow-x-auto rounded-2xl border border-white/10">
      <table className="w-full min-w-[42rem] text-sm">
        <thead className="bg-white/[0.07] text-xs uppercase tracking-[0.18em] text-stone-400">
          <tr>
            {table.columns.map((column) => (
              <th className="px-4 py-3 text-left font-medium" key={column}>
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, rowIndex) => (
            <tr className="border-t border-white/10" key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <td className="px-4 py-3 text-stone-200" key={cellIndex}>
                  {String(cell ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
