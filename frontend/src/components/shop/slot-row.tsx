"use client"

import { XIcon } from "lucide-react"
import { SLOTS, type Outfit, type SlotId } from "@/lib/slots"
import { cn } from "@/lib/utils"

type Props = {
  outfit: Outfit
  activeSlot: SlotId | null
  onSelect: (slot: SlotId | null) => void
  onRemove: (slot: SlotId) => void
}

export function SlotRow({ outfit, activeSlot, onSelect, onRemove }: Props) {
  return (
    <section aria-labelledby="outfit-heading" className="flex flex-col gap-2.5">
      <h2 id="outfit-heading" className="text-sm font-medium text-muted-foreground">
        Your outfit. Pick a slot to browse it, then add an item.
      </h2>
      <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 xl:grid-cols-6">
        {SLOTS.map((slot) => {
          const item = outfit[slot.id]
          const active = activeSlot === slot.id
          return (
            <div
              key={slot.id}
              className={cn(
                "relative rounded-xl border bg-card transition-colors",
                active ? "border-primary ring-1 ring-primary" : "border-border",
              )}
            >
              <button
                type="button"
                aria-pressed={active}
                onClick={() => onSelect(active ? null : slot.id)}
                className="flex h-16 w-full items-center gap-2.5 rounded-xl px-2.5 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                {item ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={item.image} alt="" className="size-11 shrink-0 rounded-lg object-cover" />
                ) : (
                  <span className="size-11 shrink-0 rounded-lg border-[1.5px] border-dashed border-input" aria-hidden="true" />
                )}
                <span className="flex min-w-0 flex-col">
                  <span className="text-sm font-semibold">{slot.label}</span>
                  <span className="truncate text-xs text-muted-foreground">{item ? item.title : "Empty"}</span>
                </span>
              </button>
              {item && (
                <button
                  type="button"
                  onClick={() => onRemove(slot.id)}
                  aria-label={`Remove ${item.title} from ${slot.label}`}
                  className="absolute -top-2 -right-2 flex size-6 items-center justify-center rounded-full border border-border bg-card text-muted-foreground hover:text-foreground focus-visible:ring-3 focus-visible:ring-ring/50 outline-none"
                >
                  <XIcon className="size-3.5" />
                </button>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
