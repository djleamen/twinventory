"use client"

import { cn } from "@/lib/utils"

type Props = { categories: string[]; value: string | null; onChange: (c: string | null) => void }

export function CategoryChips({ categories, value, onChange }: Props) {
  const chips: (string | null)[] = [null, ...categories]
  return (
    <div className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1" role="group" aria-label="Filter by category">
      {chips.map((c) => {
        const on = value === c
        return (
          <button
            key={c ?? "all"}
            type="button"
            aria-pressed={on}
            onClick={() => onChange(c)}
            className={cn(
              "h-9 shrink-0 rounded-full border px-4 text-sm whitespace-nowrap outline-none transition-colors focus-visible:ring-3 focus-visible:ring-ring/50",
              on ? "border-foreground bg-foreground text-background" : "border-input bg-transparent hover:bg-accent",
            )}
          >
            {c ?? "All"}
          </button>
        )
      })}
    </div>
  )
}
