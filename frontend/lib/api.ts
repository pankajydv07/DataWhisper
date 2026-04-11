import type { QueryResponse } from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function submitQuery(params: {
  question: string
  sessionId: string
  token: string
  refresh?: boolean
}): Promise<QueryResponse> {
  const response = await fetch(
    `${API_URL}/api/query?refresh=${params.refresh ?? false}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${params.token}`,
      },
      body: JSON.stringify({
        question: params.question,
        session_id: params.sessionId,
      }),
    }
  )

  if (!response.ok) {
    throw new Error(`Query failed with status ${response.status}`)
  }

  return response.json()
}
