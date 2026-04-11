export interface QueryResponse {
  sql: string
  sql_explanation: string
  result_summary: string
  table: { columns: string[]; rows: unknown[][] } | null
  chart: { type: "bar" | "line"; x: string; y: string } | null
  cached: boolean
  execution_time_ms: number
  error?: string
  suggested_queries?: string[]
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  response?: QueryResponse
  timestamp: Date
}
