"use client"

import { X } from "lucide-react"

import { SessionSidebar } from "./SessionSidebar"

import type { ChatSessionSummary } from "@/lib/types"

export function MobileSidebar({
  open,
  sessions,
  activeSessionId,
  onClose,
  onNewChat,
  onSelect,
  onRename,
  onDelete,
}: {
  open: boolean
  sessions: ChatSessionSummary[]
  activeSessionId: string | null
  onClose: () => void
  onNewChat: () => void
  onSelect: (sessionId: string) => void
  onRename: (session: ChatSessionSummary) => void
  onDelete: (session: ChatSessionSummary) => void
}) {
  if (!open) {
    return null
  }

  return (
    <div className="fixed inset-0 z-40 bg-black/55 backdrop-blur-sm md:hidden">
      <div className="absolute inset-y-0 left-0 w-[20rem] bg-ink shadow-2xl">
        <div className="flex justify-end p-3">
          <button onClick={onClose} type="button">
            <X className="text-stone-300" size={18} />
          </button>
        </div>
        <SessionSidebar
          activeSessionId={activeSessionId}
          onDelete={(session) => {
            onDelete(session)
            onClose()
          }}
          onNewChat={() => {
            onNewChat()
            onClose()
          }}
          onRename={onRename}
          onSelect={(sessionId) => {
            onSelect(sessionId)
            onClose()
          }}
          sessions={sessions}
        />
      </div>
    </div>
  )
}
