"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Header } from "./header"
import { PhotoPanel } from "./photo-panel"
import { Preferences } from "./preferences"
import { SlotRow } from "./slot-row"
import { CategoryChips } from "./category-chips"
import { ProductGrid } from "./product-grid"
import { VoiceSearchBar } from "./voice-search-bar"
import { useProducts, useTryOn, useUser } from "@/hooks/queries"
import { useDebouncedValue } from "@/hooks/use-debounced-value"
import {
  ALL_CATEGORIES,
  SLOTS,
  addToOutfit,
  outfitItems,
  removeFromOutfit,
  slotForCategory,
  type Outfit,
  type SlotId,
} from "@/lib/slots"
import type { Product } from "@/lib/types"

export function ShopScreen({ username }: { username: string }) {
  const { data: user, isLoading: userLoading, error: userError } = useUser(username)

  const [search, setSearch] = useState("")
  const query = useDebouncedValue(search.trim())
  const [activeSlot, setActiveSlot] = useState<SlotId | null>(null)
  const [category, setCategory] = useState<string | null>(null)
  const [outfit, setOutfit] = useState<Outfit>({})
  const [result, setResult] = useState<{ image: string; items: Product[]; cacheKey: string | null } | null>(null)
  const [showResult, setShowResult] = useState(true)

  const slot = SLOTS.find((s) => s.id === activeSlot)
  const chipCategories = slot ? slot.categories : ALL_CATEGORIES
  const categories = category ? [category] : slot?.categories
  const products = useProducts(query, categories)
  const tryOn = useTryOn()

  const items = useMemo(() => outfitItems(outfit), [outfit])
  const hasPhoto = !!user?.image_url

  function selectSlot(id: SlotId | null) {
    setActiveSlot(id)
    setCategory(null)
  }

  function toggleProduct(p: Product) {
    const s = slotForCategory(p.category)
    if (!s) return
    setOutfit((o) => (o[s]?.id === p.id ? removeFromOutfit(o, s) : addToOutfit(o, p)))
  }

  function runTryOn() {
    if (!user) return
    const selected = items
    tryOn.mutate([user.image_url, ...selected.map((p) => p.image)], {
      onSuccess: (res) => {
        setResult({ image: `data:image/png;base64,${res.image}`, items: selected, cacheKey: res.cache_key })
        setShowResult(true)
      },
      onError: (e) => toast.error(`Try-on failed: ${e.message}`),
    })
  }

  if (userError)
    return (
      <>
        <Header />
        <main className="mx-auto max-w-xl flex-1 px-5 py-16">
          <p className="text-lg">
            {userError.message === "User not found" ? `There's no user called "${username}".` : userError.message}
          </p>
          <Link href="/" className="mt-4 inline-block font-medium text-primary underline-offset-4 hover:underline">
            Choose a profile
          </Link>
        </main>
      </>
    )

  const emptyHint = query
    ? `Nothing matches "${query}"${category ? ` in ${category}` : ""}. Try different words or another category.`
    : "No items in this category yet."

  return (
    <>
      <Header user={user} />
      <div className="flex flex-1 flex-col lg:flex-row lg:min-h-0">
        <aside className="flex flex-col gap-6 border-border px-5 py-6 lg:sticky lg:top-0 lg:h-[calc(100vh-4rem)] lg:w-[420px] lg:shrink-0 lg:overflow-y-auto lg:border-r lg:px-8 xl:w-[460px]">
          {userLoading || !user ? (
            <>
              <Skeleton className="aspect-[4/5] w-full rounded-2xl" />
              <Skeleton className="h-20 w-full" />
            </>
          ) : (
            <>
              <PhotoPanel
                user={user}
                result={result?.image ?? null}
                resultItems={result?.items ?? []}
                resultCacheKey={result?.cacheKey ?? null}
                showResult={showResult}
                onToggleResult={() => setShowResult((v) => !v)}
                isGenerating={tryOn.isPending}
              />
              <Preferences key={user.username} user={user} />
            </>
          )}
        </aside>

        <main className="flex min-w-0 flex-1 flex-col gap-5 px-5 pt-6 lg:px-8">
          <VoiceSearchBar value={search} onChange={setSearch} isLoading={products.isLoading} />

          <SlotRow
            outfit={outfit}
            activeSlot={activeSlot}
            onSelect={selectSlot}
            onRemove={(s) => setOutfit((o) => removeFromOutfit(o, s))}
          />

          <CategoryChips categories={chipCategories} value={category} onChange={setCategory} />

          <ProductGrid
            products={products.products}
            isLoading={products.isLoading}
            error={products.error}
            onRetry={products.refetch}
            isSelected={(p) => {
              const s = slotForCategory(p.category)
              return !!s && outfit[s]?.id === p.id
            }}
            onToggle={toggleProduct}
            emptyHint={emptyHint}
          />

          <div className="sticky bottom-0 -mx-5 mt-auto flex items-center justify-end gap-4 border-t border-border bg-background/95 px-5 py-4 backdrop-blur lg:-mx-8 lg:px-8">
            <span className="text-sm text-muted-foreground">
              {!hasPhoto
                ? "This profile has no photo yet. Add one to try things on."
                : items.length === 0
                  ? "Add at least one item to try it on."
                  : `${items.length} ${items.length === 1 ? "item" : "items"} selected`}
            </span>
            <Button
              size="lg"
              className="h-12 px-8 text-base"
              disabled={!user || !hasPhoto || items.length === 0 || tryOn.isPending}
              onClick={runTryOn}
            >
              {tryOn.isPending ? "Trying on…" : "Try on"}
            </Button>
          </div>
        </main>
      </div>
    </>
  )
}
