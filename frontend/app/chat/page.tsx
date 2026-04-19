"use client"

import { Home, PanelLeft, Scale } from "lucide-react"
import { useEffect, useState } from "react"
import { useAuth, UserButton } from "@clerk/nextjs"
import Link from "next/link"

import { ChatInput } from "@/components/ChatInput"
import { ChatMessage } from "@/components/ChatMessage"
import { LoadingDots } from "@/components/LoadingDots"
import { MetricDictionary } from "@/components/MetricDictionary"
import { MobileSidebar } from "@/components/MobileSidebar"
import { SessionSidebar } from "@/components/SessionSidebar"
import { SuggestedQueries } from "@/components/SuggestedQueries"
import {
  createSession,
  deleteSession,
  getMetrics,
  getSession,
  listSessions,
  renameSession,
  submitQuery,
} from "@/lib/api"
import type {
  ChatMessage as ChatMessageType,
  ChatSessionSummary,
  MetricDefinitionRef,
  StoredMessage,
} from "@/lib/types"

export default function ChatPage() {
  const { getToken } = useAuth()
  const [sessions, setSessions] = useState<ChatSessionSummary[]>([])
  const [messagesBySessionId, setMessagesBySessionId] = useState<
    Record<string, ChatMessageType[]>
  >({})
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)
  const [isLoadingSessions, setIsLoadingSessions] = useState(true)
  const [isLoadingMessages, setIsLoadingMessages] = useState(false)
  const [isSendingMessage, setIsSendingMessage] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [dictionaryOpen, setDictionaryOpen] = useState(false)
  const [metrics, setMetrics] = useState<MetricDefinitionRef[]>([])

  useEffect(() => {
    void loadInitialState()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function withToken<T>(task: (token: string) => Promise<T>) {
    const token = await getToken()
    if (!token) {
      throw new Error("Missing Clerk token")
    }
    return task(token)
  }

  async function loadInitialState() {
    setIsLoadingSessions(true)
    try {
      const [sessionResponse, metricResponse] = await Promise.all([
        withToken((token) => listSessions(token)),
        withToken((token) => getMetrics(token)),
      ])

      setSessions(sessionResponse.sessions)
      setMetrics(metricResponse.metrics)

      if (sessionResponse.sessions[0]) {
        await selectSession(sessionResponse.sessions[0].session_id)
      }
    } finally {
      setIsLoadingSessions(false)
    }
  }

  function mapStoredMessages(messages: StoredMessage[]): ChatMessageType[] {
    return messages.map((message) => ({
      id: message.message_id,
      role: message.role,
      content: message.content,
      response: message.response ?? undefined,
      timestamp: new Date(message.created_at),
    }))
  }

  function upsertSession(session: ChatSessionSummary) {
    setSessions((current) =>
      [session, ...current.filter((item) => item.session_id !== session.session_id)].sort(
        (a, b) =>
          new Date(b.last_message_at).getTime() - new Date(a.last_message_at).getTime()
      )
    )
  }

  async function selectSession(sessionId: string) {
    setActiveSessionId(sessionId)

    if (messagesBySessionId[sessionId]) {
      return
    }

    setIsLoadingMessages(true)
    try {
      const detail = await withToken((token) => getSession(token, sessionId))
      setMessagesBySessionId((current) => ({
        ...current,
        [sessionId]: mapStoredMessages(detail.messages),
      }))
      upsertSession(detail.session)
    } finally {
      setIsLoadingMessages(false)
    }
  }

  async function handleNewChat() {
    const detail = await withToken((token) => createSession(token))
    upsertSession(detail.session)
    setMessagesBySessionId((current) => ({
      ...current,
      [detail.session.session_id]: [],
    }))
    setActiveSessionId(detail.session.session_id)
  }

  async function handleRename(session: ChatSessionSummary) {
    const nextTitle = window.prompt("Rename chat", session.title)?.trim()
    if (!nextTitle || nextTitle === session.title) {
      return
    }

    const detail = await withToken((token) =>
      renameSession(token, session.session_id, nextTitle)
    )
    upsertSession(detail.session)
  }

  async function handleDelete(session: ChatSessionSummary) {
    const confirmed = window.confirm(`Delete "${session.title}"?`)
    if (!confirmed) {
      return
    }

    await withToken((token) => deleteSession(token, session.session_id))

    setSessions((current) =>
      current.filter((item) => item.session_id !== session.session_id)
    )
    setMessagesBySessionId((current) => {
      const next = { ...current }
      delete next[session.session_id]
      return next
    })

    if (activeSessionId === session.session_id) {
      const remaining = sessions.filter((item) => item.session_id !== session.session_id)
      setActiveSessionId(remaining[0]?.session_id ?? null)
      if (remaining[0]) {
        await selectSession(remaining[0].session_id)
      }
    }
  }

  async function ensureActiveSession(question: string) {
    if (activeSessionId) {
      return activeSessionId
    }

    const detail = await withToken((token) => createSession(token, question))
    upsertSession(detail.session)
    setMessagesBySessionId((current) => ({
      ...current,
      [detail.session.session_id]: [],
    }))
    setActiveSessionId(detail.session.session_id)
    return detail.session.session_id
  }

  async function sendQuestion(question: string) {
    const sessionId = await ensureActiveSession(question)

    const userMessage: ChatMessageType = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
      timestamp: new Date(),
    }

    setMessagesBySessionId((current) => ({
      ...current,
      [sessionId]: [...(current[sessionId] ?? []), userMessage],
    }))
    setIsSendingMessage(true)

    try {
      const token = await getToken()
      if (!token) {
        throw new Error("Missing Clerk token")
      }

      const response = await submitQuery({ question, sessionId, token })

      const assistantMessage: ChatMessageType = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          response.clarification_question ??
          response.error ??
          response.result_summary,
        response,
        timestamp: new Date(),
      }

      setMessagesBySessionId((current) => ({
        ...current,
        [sessionId]: [...(current[sessionId] ?? []), assistantMessage],
      }))

      const existing = sessions.find((item) => item.session_id === sessionId)
      if (existing) {
        upsertSession({
          ...existing,
          title: response.session_title || existing.title,
          updated_at: new Date().toISOString(),
          last_message_at: new Date().toISOString(),
        })
      }
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Something went wrong while asking your data."

      setMessagesBySessionId((current) => ({
        ...current,
        [sessionId]: [
          ...(current[sessionId] ?? []),
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: message,
            timestamp: new Date(),
          },
        ],
      }))
    } finally {
      setIsSendingMessage(false)
    }
  }

  const activeSession = sessions.find((session) => session.session_id === activeSessionId)
  const activeMessages = activeSessionId ? messagesBySessionId[activeSessionId] ?? [] : []

  return (
    <main className="min-h-screen overflow-hidden bg-ink text-paper">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(circle_at_16%_8%,rgba(216,166,63,0.13),transparent_24rem),radial-gradient(circle_at_88%_12%,rgba(86,111,82,0.18),transparent_26rem),linear-gradient(145deg,#060b12,#0b141f_48%,#060b12)]" />
      <div className="grain-overlay pointer-events-none fixed inset-0 -z-10 opacity-70" />

      <MetricDictionary
        metrics={metrics}
        onClose={() => setDictionaryOpen(false)}
        open={dictionaryOpen}
      />

      <MobileSidebar
        activeSessionId={activeSessionId}
        onClose={() => setSidebarOpen(false)}
        onDelete={handleDelete}
        onNewChat={() => void handleNewChat()}
        onRename={handleRename}
        onSelect={(sessionId) => void selectSession(sessionId)}
        open={sidebarOpen}
        sessions={sessions}
      />

      <div className="grid min-h-screen md:grid-cols-[17rem_1fr]">
        <div className="hidden md:block">
          <SessionSidebar
            activeSessionId={activeSessionId}
            onDelete={handleDelete}
            onNewChat={() => void handleNewChat()}
            onRename={handleRename}
            onSelect={(sessionId) => void selectSession(sessionId)}
            sessions={sessions}
          />
        </div>

        <section className="flex min-h-screen min-w-0 flex-col">
          <header className="flex items-center justify-between border-b border-line bg-ink/[0.72] px-4 py-4 backdrop-blur-xl md:px-8">
            <div className="flex min-w-0 items-center gap-3">
              <button
                className="rounded-full border border-line p-2 text-paper-muted transition hover:border-brass/50 hover:text-paper md:hidden"
                onClick={() => setSidebarOpen(true)}
                type="button"
              >
                <PanelLeft size={18} />
              </button>
              <div className="min-w-0">
                <p className="text-[11px] uppercase tracking-[0.34em] text-brass">
                  Analyst workspace
                </p>
                <h1 className="truncate font-display text-2xl tracking-tight text-paper md:text-4xl">
                  {activeSession?.title ?? "Chat"}
                </h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Link
                className="hidden items-center gap-2 rounded-full border border-line bg-paper/[0.03] px-4 py-2 text-sm text-paper-muted transition hover:border-brass/40 hover:text-paper sm:inline-flex"
                href="/"
              >
                <Home size={15} />
                Home
              </Link>
              <button
                className="inline-flex items-center gap-2 rounded-full border border-line bg-paper/[0.03] px-4 py-2 text-sm text-paper-muted transition hover:border-brass/40 hover:text-paper"
                onClick={() => setDictionaryOpen(true)}
                type="button"
              >
                <Scale size={16} />
                <span className="hidden sm:inline">Metric dictionary</span>
              </button>
              <UserButton />
            </div>
          </header>

          <section className="flex-1 overflow-y-auto px-4 pb-36 pt-6 md:px-8">
            <div className="mx-auto flex max-w-6xl flex-col gap-5">
              {isLoadingSessions || isLoadingMessages ? <LoadingDots /> : null}

              {!activeSession && !isLoadingSessions ? (
                <SuggestedQueries onSelect={(query) => void sendQuestion(query)} />
              ) : null}

              {activeSession && activeMessages.length === 0 && !isLoadingMessages ? (
                <SuggestedQueries onSelect={(query) => void sendQuestion(query)} />
              ) : null}

              {activeMessages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}

              {isSendingMessage ? <LoadingDots /> : null}
            </div>
          </section>

          <div className="fixed inset-x-0 bottom-0 border-t border-line bg-ink/[0.88] p-4 backdrop-blur-xl md:left-[17rem]">
            <div className="mx-auto max-w-6xl">
              <ChatInput
                disabled={isSendingMessage}
                onSend={(question) => void sendQuestion(question)}
              />
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
