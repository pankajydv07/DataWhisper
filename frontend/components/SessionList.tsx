import { SessionListItem } from "./SessionListItem"

import type { ChatSessionSummary } from "@/lib/types"
import { groupSessions } from "@/lib/session-groups"

export function SessionList({
  sessions,
  activeSessionId,
  onSelect,
  onRename,
  onDelete,
}: {
  sessions: ChatSessionSummary[]
  activeSessionId: string | null
  onSelect: (sessionId: string) => void
  onRename: (session: ChatSessionSummary) => void
  onDelete: (session: ChatSessionSummary) => void
}) {
  const groups = groupSessions(sessions)

  return (
    <div className="space-y-6">
      {groups.map((group) => (
        <section key={group.label}>
          <p className="mb-2 px-3 text-[11px] uppercase tracking-[0.24em] text-paper-muted/[0.65]">
            {group.label}
          </p>
          <div className="space-y-1">
            {group.sessions.map((session) => (
              <SessionListItem
                active={activeSessionId === session.session_id}
                key={session.session_id}
                onDelete={onDelete}
                onRename={onRename}
                onSelect={onSelect}
                session={session}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
