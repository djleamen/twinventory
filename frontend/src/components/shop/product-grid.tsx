"use client"

import { ExternalLinkIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import type { Product } from "@/lib/types"
import { cn } from "@/lib/utils"

type Props = {
  products: Product[]
  isLoading: boolean
  error: Error | null
  onRetry: () => void
  isSelected: (p: Product) => boolean
  onToggle: (p: Product) => void
  emptyHint: string
}

const price = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 })

export function ProductGrid({ products, isLoading, error, onRetry, isSelected, onToggle, emptyHint }: Props) {
  if (error)
    return (
      <div className="rounded-xl border border-border bg-card p-6 text-sm">
        <p className="font-medium">Products didn&apos;t load.</p>
        <p className="mt-1 text-muted-foreground">{error.message}</p>
        <Button variant="outline" className="mt-4" onClick={onRetry}>
          Try again
        </Button>
      </div>
    )

  if (isLoading && !products.length)
    return (
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 2xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="aspect-[3/4] rounded-xl" />
        ))}
      </div>
    )

  if (!products.length)
    return (
      <div className="rounded-xl border border-dashed border-input p-8 text-center text-sm text-muted-foreground">
        {emptyHint}
      </div>
    )

  return (
    <ul className="grid grid-cols-2 gap-4 md:grid-cols-3 2xl:grid-cols-4">
      {products.map((p) => {
        const selected = isSelected(p)
        return (
          <li
            key={p.id}
            className={cn(
              "flex flex-col overflow-hidden rounded-xl border bg-card",
              selected ? "border-primary ring-1 ring-primary" : "border-border",
            )}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={p.image} alt={p.title} loading="lazy" className="aspect-square w-full bg-secondary object-cover" />
            <div className="flex flex-1 flex-col gap-1 p-3">
              <p className="text-xs text-muted-foreground">{p.category}</p>
              <h3 className="line-clamp-2 text-sm leading-snug font-medium">{p.title}</h3>
              <div className="mt-auto flex items-center justify-between gap-2 pt-2">
                <span className="text-sm font-medium">{price.format(p.price)}</span>
                <div className="flex items-center gap-1">
                  <a
                    href={p.url}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={`View ${p.title} in store`}
                    className="flex size-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground"
                  >
                    <ExternalLinkIcon className="size-4" />
                  </a>
                  <Button
                    size="sm"
                    variant={selected ? "default" : "outline"}
                    aria-pressed={selected}
                    onClick={() => onToggle(p)}
                    className={cn("min-w-16", !selected && "border-primary text-primary hover:text-primary")}
                  >
                    {selected ? "Added" : "Add"}
                  </Button>
                </div>
              </div>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
