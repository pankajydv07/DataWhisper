export type QueryIntent =
  | "change"
  | "compare"
  | "breakdown"
  | "summarize"
  | "general"
  | "clarify"

export interface MetricDefinitionRef {
  key: string
  label: string
  definition: string
  formula?: string | null
  source_tables: string[]
  default_time_grain?: string | null
}

export interface ComparisonPayload {
  columns: string[]
  rows: Record<string, unknown>[]
  focus?: string | null
}

export interface QueryResponse {
  session_id?: string | null
  session_title?: string | null
  intent: QueryIntent
  sql: string
  sql_explanation: string
  result_summary: string
  table: { columns: string[]; rows: unknown[][] } | null
  chart: {
    type: "bar" | "line" | "pie" | "stacked_bar"
    x: string
    y: string
    series: string[]
  } | null
  comparison?: ComparisonPayload | null
  data_sources: string[]
  metric_definitions: MetricDefinitionRef[]
  assumptions: string[]
  clarification_question?: string | null
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

export interface ChatSessionSummary {
  session_id: string
  user_id: string
  title: string
  created_at: string
  updated_at: string
  last_message_at: string
}

export interface StoredMessage {
  message_id: string
  session_id: string
  user_id: string
  role: "user" | "assistant"
  content: string
  response?: QueryResponse | null
  created_at: string
}

export interface SessionListResponse {
  sessions: ChatSessionSummary[]
}

export interface SessionDetailResponse {
  session: ChatSessionSummary
  messages: StoredMessage[]
}

export interface MetricDictionaryResponse {
  metrics: MetricDefinitionRef[]
}
