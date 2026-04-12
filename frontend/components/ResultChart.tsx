"use client"

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

const PIE_COLORS = ["#d8a63f", "#4f6f52", "#b36f42", "#7e91b7", "#e1c98d", "#7e5c6d"]

export function ResultChart({
  chart,
  table,
}: {
  chart: { type: "bar" | "line" | "pie" | "stacked_bar"; x: string; y: string; series: string[] }
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
            <Tooltip contentStyle={tooltipStyle} />
            <Line dataKey={chart.y} dot={false} stroke="#d8a63f" strokeWidth={3} type="monotone" />
          </LineChart>
        ) : chart.type === "pie" ? (
          <PieChart>
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            <Pie
              data={data}
              dataKey={chart.y}
              nameKey={chart.x}
              outerRadius={96}
              stroke="rgba(255,255,255,0.1)"
            >
              {data.map((_, index) => (
                <Cell fill={PIE_COLORS[index % PIE_COLORS.length]} key={index} />
              ))}
            </Pie>
          </PieChart>
        ) : (
          <BarChart data={data}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
            <XAxis dataKey={chart.x} stroke="#a8a29e" />
            <YAxis stroke="#a8a29e" />
            <Tooltip contentStyle={tooltipStyle} />
            {chart.type === "stacked_bar" ? (
              <>
                <Legend />
                <Bar dataKey={chart.y} fill="#d8a63f" radius={[8, 8, 0, 0]} stackId="total" />
                {chart.series.map((series, index) => (
                  <Bar
                    dataKey={series}
                    fill={PIE_COLORS[(index + 1) % PIE_COLORS.length]}
                    key={series}
                    radius={[8, 8, 0, 0]}
                    stackId="total"
                  />
                ))}
              </>
            ) : (
              <Bar dataKey={chart.y} fill="#d8a63f" radius={[8, 8, 0, 0]} />
            )}
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}

const tooltipStyle = {
  background: "#09111f",
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: "14px",
}
