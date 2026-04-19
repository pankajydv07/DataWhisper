import { SignIn } from "@clerk/nextjs"

export default function SignInPage() {
  return (
    <main className="relative isolate flex min-h-screen items-center justify-center overflow-hidden px-6 py-12 text-paper">
      <div className="grain-overlay pointer-events-none absolute inset-0 -z-10" />
      <div className="pointer-events-none absolute inset-0 -z-20 bg-[radial-gradient(circle_at_24%_18%,rgba(216,166,63,0.22),transparent_28rem),radial-gradient(circle_at_78%_72%,rgba(86,111,82,0.18),transparent_26rem),linear-gradient(130deg,#060b12,#0b141f_52%,#060b12)]" />
      <div className="grid w-full max-w-6xl items-center gap-12 lg:grid-cols-[0.9fr_1.1fr]">
        <section className="hidden lg:block">
          <p className="text-xs uppercase tracking-[0.38em] text-brass">
            DataWhisper access
          </p>
          <h1 className="mt-5 font-display text-7xl leading-none tracking-tight">
            Return to the analyst desk.
          </h1>
          <p className="mt-6 max-w-md text-lg leading-8 text-paper-muted">
            Sign in to continue governed retail conversations with SQL, charts,
            and metric context intact.
          </p>
        </section>
        <div className="mx-auto w-full max-w-md border border-line bg-paper/[0.035] p-4 shadow-2xl shadow-black/30 backdrop-blur">
          <SignIn fallbackRedirectUrl="/chat" />
        </div>
      </div>
    </main>
  )
}
