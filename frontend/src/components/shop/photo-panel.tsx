"use client"

import { Loader2Icon } from "lucide-react"
import { Silhouette } from "./silhouette"
import { ModelViewButton } from "./model-view-dialog"
import { toApiUrl } from "@/lib/api/client"
import type { Product, User } from "@/lib/types"

type Props = {
  user: User
  result: string | null
  resultItems: Product[]
  resultCacheKey: string | null
  showResult: boolean
  onToggleResult: () => void
  isGenerating: boolean
}

export function PhotoPanel({ user, result, resultItems, resultCacheKey, showResult, onToggleResult, isGenerating }: Props) {
  const showingResult = !!result && showResult
  const shownImage = showingResult ? result : user.image_url

  return (
    <section aria-label="Your photo" className="flex flex-col gap-3">
      <div className="relative aspect-[4/5] w-full overflow-hidden rounded-2xl border border-border bg-secondary">
        {showingResult ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={result!} alt={`${user.username} wearing the selected outfit`} className="h-full w-full object-contain" />
        ) : user.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={toApiUrl(user.image_url)} alt={`Photo of ${user.username}`} className="h-full w-full object-contain" />
        ) : (
          <Silhouette className="h-full w-full" />
        )}

        <span className="absolute top-3 left-3 rounded-full bg-card px-3 py-1 text-[13px] font-medium shadow-xs">
          {showingResult ? "Try-on result" : "Your photo"}
        </span>

        {shownImage && !isGenerating && (
          <ModelViewButton
            key={shownImage}
            imageUrl={shownImage}
            cacheKey={showingResult ? resultCacheKey : null}
            title={showingResult ? "Your try-on in 3D" : `${user.username} in 3D`}
          />
        )}

        {isGenerating && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-background/85" role="status">
            <Loader2Icon className="size-7 animate-spin text-primary" aria-hidden="true" />
            <p className="font-heading text-2xl">Dressing you up…</p>
            <p className="text-sm text-muted-foreground">This usually takes a few seconds.</p>
          </div>
        )}
      </div>

      {result && !isGenerating && (
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              {resultItems.length} {resultItems.length === 1 ? "item" : "items"} in this try-on
            </span>
            <button type="button" onClick={onToggleResult} className="font-medium text-primary underline-offset-4 hover:underline">
              {showResult ? "Show original" : "Show try-on"}
            </button>
          </div>
          <ul className="flex flex-col gap-1.5">
            {resultItems.map((p) => (
              <li key={p.id} className="flex items-center justify-between gap-3 text-sm">
                <span className="truncate">{p.title}</span>
                <a href={p.url} target="_blank" rel="noreferrer" className="shrink-0 font-medium text-primary underline-offset-4 hover:underline">
                  View in store
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
