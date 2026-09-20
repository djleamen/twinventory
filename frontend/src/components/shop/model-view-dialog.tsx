"use client"

import { useEffect, useState } from "react"
import { BoxIcon, Loader2Icon } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useModel } from "@/hooks/queries"

const MESHY_ASSETS = "https://assets.meshy.ai/"

/** Routes Meshy links through /meshy-assets (see next.config.ts) to get around CORS. */
function toProxiedUrl(url: string): string {
  return url.startsWith(MESHY_ASSETS) ? `/meshy-assets/${url.slice(MESHY_ASSETS.length)}` : url
}

type Props = {
  /** Public image URL or data URI of the image to turn into a model. */
  imageUrl: string
  /** Try-on outfit cache key, so the same outfit reuses its 3D model. */
  cacheKey?: string | null
  title: string
}

/** A "View in 3D" button for the bottom-right corner of an image, plus the dialog it opens. */
export function ModelViewButton({ imageUrl, cacheKey, title }: Props) {
  const [open, setOpen] = useState(false)
  const model = useModel(imageUrl, open, cacheKey)

  // model-viewer is a browser-only web component, so load it on the client.
  useEffect(() => {
    import("@google/model-viewer")
  }, [])

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="absolute right-3 bottom-3 flex h-10 items-center gap-2 rounded-full bg-card/90 px-4 text-sm font-medium text-foreground shadow-xs outline-none backdrop-blur hover:bg-card focus-visible:ring-3 focus-visible:ring-ring/50"
      >
        <BoxIcon className="size-4.5" aria-hidden="true" />
        View in 3D
      </button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
            <DialogDescription>Drag to rotate. Scroll or pinch to zoom.</DialogDescription>
          </DialogHeader>

          <div className="flex h-[min(70dvh,560px)] min-h-64 w-full items-center justify-center overflow-hidden rounded-xl bg-secondary">
            {model.isPending && (
              <div className="flex flex-col items-center gap-3 px-6 text-center" role="status">
                <Loader2Icon className="size-7 animate-spin text-primary" aria-hidden="true" />
                <p className="font-medium">Building the 3D model…</p>
                <p className="text-sm text-muted-foreground">This can take a minute or two. You can close this and come back.</p>
              </div>
            )}

            {model.isError && (
              <p className="px-6 text-center text-sm">Couldn&apos;t build the 3D model: {model.error.message}</p>
            )}

            {model.data && (
              <model-viewer
                src={toProxiedUrl(model.data.model_url)}
                alt={title}
                camera-controls
                auto-rotate
                shadow-intensity="1"
                style={{ width: "100%", height: "100%" }}
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
