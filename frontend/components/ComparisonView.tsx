import type { ComparisonPayload } from "@/lib/types"

export function ComparisonView({ comparison }: { comparison: ComparisonPayload }) {
  return (
    <div className="mt-5 overflow-x-auto border border-line bg-paper/[0.025]">
      <table className="w-full min-w-[34rem] text-sm">
        <thead className="bg-paper/[0.055] text-xs uppercase tracking-[0.18em] text-paper-muted">
          <tr>
            {comparison.columns.map((column) => (
              <th className="px-4 py-3 text-left font-medium" key={column}>
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {comparison.rows.map((row, index) => (
            <tr className="border-t border-line" key={index}>
              {comparison.columns.map((column) => {
                const value = row[column]
                const isFocus = comparison.focus === column
                const numericValue =
                  typeof value === "number"
                    ? value
                    : typeof value === "string"
                      ? Number(value)
                      : NaN
                const focusClass =
                  isFocus && !Number.isNaN(numericValue)
                    ? numericValue > 0
                      ? "text-emerald-300"
                      : numericValue < 0
                        ? "text-danger"
                        : "text-paper"
                    : "text-paper"

                return (
                  <td className={`px-4 py-3 ${focusClass}`} key={column}>
                    {String(value ?? "")}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
