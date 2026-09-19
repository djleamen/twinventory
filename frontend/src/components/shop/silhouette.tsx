import { cn } from "@/lib/utils"

/** Stand-in for a user photo when image_url is empty. */
export function Silhouette({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-end justify-center bg-secondary", className)}>
      <svg viewBox="0 0 260 420" className="h-[88%] w-auto" fill="none" stroke="#8fb39c" strokeWidth="2" aria-hidden="true">
        <circle cx="130" cy="70" r="42" />
        <path d="M40 420 L52 190 Q60 130 130 125 Q200 130 208 190 L220 420" />
      </svg>
    </div>
  )
}
