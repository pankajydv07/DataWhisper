import type {
  QueryResponse,
  SessionDetailResponse,
  SessionListResponse,
} from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function apiFetch<T>(
  path: string,
  token: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init?.headers ?? {}),
    },
  })

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  return response.json()
}

export async function submitQuery(params: {
  question: string
  sessionId: string
  token: string
  refresh?: boolean
}): Promise<QueryResponse> {
  return apiFetch<QueryResponse>(
    `/api/query?refresh=${params.refresh ?? false}`,
    params.token,
    {
      method: "POST",
      body: JSON.stringify({
        question: params.question,
        session_id: params.sessionId,
      }),
    }
  )
}

export function listSessions(token: string): Promise<SessionListResponse> {
  return apiFetch<SessionListResponse>("/api/sessions", token)
}

export function getSession(token: string, sessionId: string): Promise<SessionDetailResponse> {
  return apiFetch<SessionDetailResponse>(`/api/sessions/${sessionId}`, token)
}

export function createSession(
  token: string,
  title?: string
): Promise<SessionDetailResponse> {
  return apiFetch<SessionDetailResponse>("/api/sessions", token, {
    method: "POST",
    body: JSON.stringify({ title }),
  })
}

export function renameSession(
  token: string,
  sessionId: string,
  title: string
): Promise<SessionDetailResponse> {
  return apiFetch<SessionDetailResponse>(`/api/sessions/${sessionId}`, token, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  })
}

export function deleteSession(token: string, sessionId: string): Promise<{ deleted: boolean }> {
  return apiFetch<{ deleted: boolean }>(`/api/sessions/${sessionId}`, token, {
    method: "DELETE",
  })
}
