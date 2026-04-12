"use client"

import { Plus } from "lucide-react"

import { SessionList } from "./SessionList"

import type { ChatSessionSummary } from "@/lib/types"

export function SessionSidebar({
  sessions,
  activeSessionId,
  onNewChat,
  onSelect,
  onRename,
  onDelete,
}: {
  sessions: ChatSessionSummary[]
  activeSessionId: string | null
  onNewChat: () => void
  onSelect: (sessionId: string) => void
  onRename: (session: ChatSessionSummary) => void
  onDelete: (session: ChatSessionSummary) => void
}) {
  return (
    <aside className="flex h-full flex-col border-r border-white/10 bg-black/12 px-3 py-4 backdrop-blur-xl">
      <button
        className="mb-5 flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-stone-100 transition hover:bg-white/[0.08]"
        onClick={onNewChat}
        type="button"
      >
        <Plus size={16} />
        New Chat
      </button>

      <div className="mb-5 px-3">
        <p className="text-xs uppercase tracking-[0.34em] text-brass">DataWhisper</p>
        <p className="mt-2 text-sm leading-6 text-stone-400">
          Persistent retail analytics conversations, grouped by time.
        </p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        <SessionList
          activeSessionId={activeSessionId}
          onDelete={onDelete}
          onRename={onRename}
          onSelect={onSelect}
          sessions={sessions}
        />
      </div>
    </aside>
  )
}
