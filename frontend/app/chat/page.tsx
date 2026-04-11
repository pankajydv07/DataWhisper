"use client"

import { useMemo, useState } from "react"
import { useAuth, UserButton } from "@clerk/nextjs"

import { ChatInput } from "@/components/ChatInput"
import { ChatMessage } from "@/components/ChatMessage"
import { LoadingDots } from "@/components/LoadingDots"
import { SuggestedQueries } from "@/components/SuggestedQueries"
import { submitQuery } from "@/lib/api"
import type { ChatMessage as ChatMessageType } from "@/lib/types"

export default function ChatPage() {
  const { getToken } = useAuth()
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const sessionId = useMemo(() => crypto.randomUUID(), [])

  async function sendQuestion(question: string) {
    const userMessage: ChatMessageType = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
      timestamp: new Date(),
    }

    setMessages((current) => [...current, userMessage])
    setIsLoading(true)

    try {
      const token = await getToken()
      if (!token) {
        throw new Error("Missing Clerk token")
      }

      const response = await submitQuery({ question, sessionId, token })

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.error ?? response.result_summary,
          response,
          timestamp: new Date(),
        },
      ])
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Something went wrong while asking your data."

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: message,
          timestamp: new Date(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen overflow-hidden text-stone-50">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[linear-gradient(140deg,rgba(9,17,31,0.96),rgba(22,35,43,0.94)_45%,rgba(12,23,32,0.98)),radial-gradient(circle_at_18%_14%,rgba(216,166,63,0.22),transparent_24rem),radial-gradient(circle_at_82%_8%,rgba(79,111,82,0.24),transparent_22rem)]" />

      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 md:px-8">
        <div>
          <p className="text-xs uppercase tracking-[0.36em] text-brass">
            DataWhisper
          </p>
          <h1 className="font-display text-3xl text-stone-100 md:text-5xl">
            Ask the warehouse.
          </h1>
        </div>
        <UserButton />
      </header>

      <section className="mx-auto grid max-w-7xl gap-6 px-5 pb-36 md:grid-cols-[18rem_1fr] md:px-8">
        <aside className="hidden border-r border-white/10 pr-6 text-sm text-stone-300 md:block">
          <p className="font-medium text-stone-100">Retail Sales</p>
          <p className="mt-2 leading-6 text-stone-400">
            Natural language questions become scoped PostgreSQL queries,
            summaries, tables, and chart-ready responses.
          </p>
          <div className="mt-8 space-y-3 text-xs uppercase tracking-[0.28em] text-stone-500">
            <p>Clerk JWT</p>
            <p>Groq SQL</p>
            <p>Supabase RLS</p>
          </div>
        </aside>

        <section className="flex min-h-[calc(100vh-12rem)] flex-col gap-4">
          {messages.length === 0 && <SuggestedQueries onSelect={sendQuestion} />}
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isLoading && <LoadingDots />}
        </section>
      </section>

      <div className="fixed inset-x-0 bottom-0 border-t border-white/10 bg-ink/90 p-4 backdrop-blur-xl">
        <div className="mx-auto max-w-4xl">
          <ChatInput disabled={isLoading} onSend={sendQuestion} />
        </div>
      </div>
    </main>
  )
}
