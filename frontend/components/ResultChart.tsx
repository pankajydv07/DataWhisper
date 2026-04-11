"use client"

import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

export function ResultChart({
  chart,
  table,
}: {
  chart: { type: "bar" | "line"; x: string; y: string }
  table: { columns: string[]; rows: unknown[][] }
}) {
  const data = table.rows.map((row) =>
    Object.fromEntries(table.columns.map((column, index) => [column, row[index]]))
  )

  return (
    <div className="mt-4 h-72 rounded-2xl border border-white/10 p-4">
      <ResponsiveContainer height="100%" width="100%">
        {chart.type === "line" ? (
          <LineChart data={data}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
            <XAxis dataKey={chart.x} stroke="#a8a29e" />
            <YAxis stroke="#a8a29e" />
            <Tooltip
              contentStyle={{
                background: "#09111f",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: "14px",
              }}
            />
            <Line
              dataKey={chart.y}
              dot={false}
              stroke="#d8a63f"
              strokeWidth={3}
              type="monotone"
            />
          </LineChart>
        ) : (
          <BarChart data={data}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
            <XAxis dataKey={chart.x} stroke="#a8a29e" />
            <YAxis stroke="#a8a29e" />
            <Tooltip
              contentStyle={{
                background: "#09111f",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: "14px",
              }}
            />
            <Bar dataKey={chart.y} fill="#d8a63f" radius={[8, 8, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}
