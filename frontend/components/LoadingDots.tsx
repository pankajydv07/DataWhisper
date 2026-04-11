export function LoadingDots() {
  return (
    <div className="mr-auto flex animate-rise items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.055] px-5 py-4 text-stone-300">
      <span>Generating query</span>
      <span className="flex gap-1">
        <span className="h-1.5 w-1.5 animate-blink rounded-full bg-brass" />
        <span className="h-1.5 w-1.5 animate-blink rounded-full bg-brass [animation-delay:150ms]" />
        <span className="h-1.5 w-1.5 animate-blink rounded-full bg-brass [animation-delay:300ms]" />
      </span>
    </div>
  )
}
