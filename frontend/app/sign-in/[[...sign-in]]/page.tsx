import { SignIn } from "@clerk/nextjs"

export default function SignInPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(115deg,rgba(9,17,31,0.96),rgba(27,38,47,0.92)),radial-gradient(circle_at_30%_20%,rgba(216,166,63,0.28),transparent_28rem)]" />
      <SignIn fallbackRedirectUrl="/chat" />
    </main>
  )
}
