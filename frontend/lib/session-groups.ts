import type { ChatSessionSummary } from "./types"

export function groupSessions(sessions: ChatSessionSummary[]) {
  const now = new Date()
  const today = startOfDay(now)

  return [
    {
      label: "Today",
      sessions: sessions.filter((session) => daysDiff(session.last_message_at, today) === 0),
    },
    {
      label: "Yesterday",
      sessions: sessions.filter((session) => daysDiff(session.last_message_at, today) === 1),
    },
    {
      label: "Previous 7 Days",
      sessions: sessions.filter((session) => {
        const diff = daysDiff(session.last_message_at, today)
        return diff >= 2 && diff <= 7
      }),
    },
    {
      label: "Older",
      sessions: sessions.filter((session) => daysDiff(session.last_message_at, today) > 7),
    },
  ].filter((group) => group.sessions.length > 0)
}

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

function daysDiff(value: string, todayStart: Date) {
  const target = startOfDay(new Date(value))
  const diffMs = todayStart.getTime() - target.getTime()
  return Math.floor(diffMs / (1000 * 60 * 60 * 24))
}
