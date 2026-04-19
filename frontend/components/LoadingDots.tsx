export function LoadingDots() {
  return (
    <div className="mr-auto flex animate-rise items-center gap-3 border border-line bg-paper/[0.035] px-5 py-4 text-paper-muted">
      <span>Generating governed query</span>
      <span className="flex gap-1">
        <span className="h-1.5 w-1.5 animate-pulse-soft rounded-full bg-brass" />
        <span className="h-1.5 w-1.5 animate-pulse-soft rounded-full bg-brass [animation-delay:150ms]" />
        <span className="h-1.5 w-1.5 animate-pulse-soft rounded-full bg-brass [animation-delay:300ms]" />
      </span>
    </div>
  )
}
