import { auth } from "@clerk/nextjs/server"
import Link from "next/link"

const proofPoints = [
  {
    label: "Governed SQL",
    copy: "Every answer is backed by validated, user-scoped Postgres queries.",
  },
  {
    label: "Metric Memory",
    copy: "Definitions, source tables, and assumptions stay attached to the answer.",
  },
  {
    label: "Conversation Ledger",
    copy: "Sessions persist so teams can revisit the path from question to evidence.",
  },
]

const workflow = [
  "Ask a retail question in plain English",
  "Classify intent and generate safe SQL",
  "Execute against scoped Supabase data",
  "Return summary, table, chart, and trust context",
]

export default async function HomePage() {
  const { userId } = await auth()
  const ctaHref = userId ? "/chat" : "/sign-in"

  return (
    <main className="min-h-screen overflow-hidden bg-ink text-paper">
      <section className="relative isolate min-h-screen overflow-hidden">
        <div className="grain-overlay pointer-events-none absolute inset-0 -z-10" />
        <div className="pointer-events-none absolute inset-0 -z-20 bg-[radial-gradient(circle_at_12%_10%,rgba(216,166,63,0.22),transparent_24rem),radial-gradient(circle_at_86%_18%,rgba(86,111,82,0.24),transparent_27rem),linear-gradient(140deg,#060b12_0%,#0c1724_48%,#060b12_100%)]" />
        <div className="pointer-events-none absolute -right-28 top-20 h-[34rem] w-[34rem] rounded-full border border-brass/10 blur-sm" />

        <header className="relative z-10 flex items-center justify-between px-5 py-5 sm:px-8 lg:px-12">
          <Link className="font-display text-2xl tracking-tight text-paper" href="/">
            DataWhisper
          </Link>
          <nav className="hidden items-center gap-8 text-sm text-paper-muted md:flex">
            <a className="transition hover:text-paper" href="#proof">
              Proof
            </a>
            <a className="transition hover:text-paper" href="#workflow">
              Workflow
            </a>
            <Link className="transition hover:text-paper" href="/sign-in">
              Sign in
            </Link>
          </nav>
          <Link
            className="rounded-full border border-brass/[0.45] px-4 py-2 text-sm font-medium text-brass transition hover:border-brass hover:bg-brass hover:text-ink"
            href={ctaHref}
          >
            Start asking
          </Link>
        </header>

        <div className="grid min-h-[calc(100svh-5.5rem)] items-center gap-12 px-5 pb-16 pt-6 sm:px-8 lg:grid-cols-[0.86fr_1.14fr] lg:px-12">
          <div className="max-w-3xl animate-reveal">
            <p className="text-xs uppercase tracking-[0.42em] text-brass">
              Governed conversational analytics
            </p>
            <h1 className="mt-5 font-display text-[4.5rem] leading-[0.86] tracking-[-0.07em] text-paper sm:text-[6.5rem] lg:text-[8.4rem]">
              DataWhisper
            </h1>
            <p className="mt-8 max-w-xl text-2xl leading-tight text-paper md:text-3xl">
              Ask the revenue question. See the SQL. Trust the answer.
            </p>
            <p className="mt-5 max-w-lg text-base leading-7 text-paper-muted">
              A quiet analyst workspace for retail teams that need natural language,
              governed queries, and evidence in the same conversation.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link
                className="inline-flex items-center justify-center rounded-full bg-brass px-6 py-3 text-sm font-semibold text-ink transition hover:bg-brass-soft hover:shadow-[0_0_42px_rgba(216,166,63,0.24)]"
                href={ctaHref}
              >
                Start asking
              </Link>
              <a
                className="inline-flex items-center justify-center rounded-full border border-line px-6 py-3 text-sm font-semibold text-paper transition hover:border-paper/40 hover:bg-paper/5"
                href="#workflow"
              >
                View workflow
              </a>
            </div>
          </div>

          <HeroCanvas />
        </div>
      </section>

      <section id="proof" className="px-5 py-20 sm:px-8 lg:px-12">
        <div className="mx-auto grid max-w-6xl gap-10 border-y border-line py-14 md:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.38em] text-brass">Proof layer</p>
            <h2 className="mt-4 font-display text-4xl leading-none tracking-tight text-paper md:text-6xl">
              Answers carry their evidence.
            </h2>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            {proofPoints.map((point) => (
              <article className="border-l border-line pl-5" key={point.label}>
                <h3 className="text-lg font-semibold text-paper">{point.label}</h3>
                <p className="mt-3 text-sm leading-6 text-paper-muted">{point.copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="workflow" className="px-5 pb-24 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs uppercase tracking-[0.38em] text-brass">Workflow</p>
          <div className="mt-7 grid gap-10 lg:grid-cols-[0.95fr_1.05fr]">
            <h2 className="font-display text-4xl leading-none tracking-tight text-paper md:text-6xl">
              From question to governed result in four moves.
            </h2>
            <div className="divide-y divide-line border-y border-line">
              {workflow.map((item, index) => (
                <div className="grid grid-cols-[3rem_1fr] gap-5 py-6" key={item}>
                  <span className="font-display text-3xl text-brass">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <p className="text-xl leading-7 text-paper">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="px-5 pb-8 sm:px-8 lg:px-12">
        <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-8 border-t border-line py-14 md:flex-row md:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.38em] text-brass">Ready</p>
            <h2 className="mt-4 font-display text-4xl tracking-tight text-paper md:text-5xl">
              Open the analyst desk.
            </h2>
          </div>
          <Link
            className="rounded-full bg-paper px-7 py-3 text-sm font-semibold text-ink transition hover:bg-brass"
            href={ctaHref}
          >
            {userId ? "Enter chat" : "Sign in to start"}
          </Link>
        </div>
      </section>
    </main>
  )
}

function HeroCanvas() {
  return (
    <div className="relative min-h-[34rem] animate-reveal [animation-delay:140ms]">
      <div className="absolute inset-0 rounded-[2rem] border border-line bg-paper/[0.035] shadow-2xl shadow-black/30 backdrop-blur" />
      <div className="absolute inset-5 overflow-hidden rounded-[1.5rem] border border-line bg-ink-soft/80">
        <div className="absolute inset-0 grain-overlay opacity-70" />
        <div className="absolute left-6 right-6 top-6 flex items-center justify-between border-b border-line pb-4">
          <span className="text-xs uppercase tracking-[0.32em] text-brass">Revenue query</span>
          <span className="rounded-full border border-moss/40 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-paper-muted">
            scoped
          </span>
        </div>

        <div className="absolute left-6 top-24 w-[72%] animate-drift rounded-3xl border border-line bg-black/[0.22] p-5">
          <p className="font-mono text-xs leading-6 text-paper-muted">
            SELECT SUM(oi.quantity * p.unit_price)
            <br />
            FROM orders o JOIN order_items oi
            <br />
            WHERE o.user_id = current_user
          </p>
        </div>

        <div className="absolute bottom-10 left-6 right-6 rounded-3xl border border-brass/20 bg-brass/[0.08] p-6">
          <p className="text-xs uppercase tracking-[0.26em] text-brass">Answer</p>
          <p className="mt-3 text-2xl leading-tight text-paper">
            Revenue declined 12.4%, led by fewer completed orders in South.
          </p>
          <div className="mt-5 h-24 rounded-2xl border border-line bg-[linear-gradient(180deg,rgba(216,166,63,0.16),transparent)] p-4">
            <div className="flex h-full items-end gap-2">
              {[42, 64, 52, 78, 46, 35, 58, 71].map((height, index) => (
                <span
                  className="flex-1 rounded-t-full bg-brass/75"
                  key={index}
                  style={{ height: `${height}%` }}
                />
              ))}
            </div>
          </div>
        </div>

        <div className="absolute right-6 top-28 grid gap-3">
          {["orders", "order_items", "products"].map((token) => (
            <span
              className="rounded-full border border-line bg-paper/[0.04] px-4 py-2 text-xs text-paper-muted"
              key={token}
            >
              {token}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
