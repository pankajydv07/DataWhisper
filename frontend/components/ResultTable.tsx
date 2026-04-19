export function ResultTable({
  table,
}: {
  table: { columns: string[]; rows: unknown[][] }
}) {
  return (
    <div className="mt-5 overflow-x-auto border border-line bg-black/10">
      <table className="w-full min-w-[42rem] text-sm">
        <thead className="bg-paper/[0.055] text-xs uppercase tracking-[0.18em] text-paper-muted">
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
            <tr className="border-t border-line transition hover:bg-paper/[0.025]" key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <td className="px-4 py-3 text-paper" key={cellIndex}>
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
