export interface QueryResponse {
  session_id?: string | null
  session_title?: string | null
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
