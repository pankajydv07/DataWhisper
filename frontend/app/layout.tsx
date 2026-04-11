import { ClerkProvider } from "@clerk/nextjs"
import type { Metadata } from "next"

import "./globals.css"

export const metadata: Metadata = {
  title: "DataWhisper",
  description: "Ask natural language questions and get SQL-backed answers.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
