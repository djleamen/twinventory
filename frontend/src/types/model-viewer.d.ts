import type { DetailedHTMLProps, HTMLAttributes } from "react"

type ModelViewerAttributes = DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> & {
  src?: string
  alt?: string
  poster?: string
  "camera-controls"?: boolean
  "auto-rotate"?: boolean
  "shadow-intensity"?: string
  exposure?: string
}

declare module "react" {
  namespace JSX {
    interface IntrinsicElements {
      "model-viewer": ModelViewerAttributes
    }
  }
}
