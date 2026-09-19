"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { ChevronDownIcon } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useUsers } from "@/hooks/queries"
import type { User } from "@/lib/types"

export function UserAvatar({ user, size = 36 }: { user: User; size?: number }) {
  return user.image_url ? (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={user.image_url} alt="" width={size} height={size} className="rounded-full object-cover" style={{ width: size, height: size }} />
  ) : (
    <span
      className="flex items-center justify-center rounded-full bg-accent font-semibold text-accent-foreground uppercase"
      style={{ width: size, height: size, fontSize: size * 0.4 }}
      aria-hidden="true"
    >
      {user.username.slice(0, 1)}
    </span>
  )
}

export function Header({ user }: { user?: User }) {
  const router = useRouter()
  const { data: users } = useUsers()

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-border px-5 lg:px-8">
      <Link href="/" className="font-heading text-2xl font-semibold tracking-tight text-foreground">
        Twinventory
      </Link>
      {user && (
        <DropdownMenu>
          <DropdownMenuTrigger className="flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-[15px] font-medium outline-none hover:bg-accent focus-visible:ring-3 focus-visible:ring-ring/50">
            <UserAvatar user={user} />
            {user.username}
            <ChevronDownIcon className="size-4 text-muted-foreground" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="min-w-44">
            {users
              ?.filter((u) => u.id !== user.id)
              .map((u) => (
                <DropdownMenuItem key={u.id} onClick={() => router.push(`/u/${u.id}`)}>
                  <UserAvatar user={u} size={24} />
                  Switch to {u.username}
                </DropdownMenuItem>
              ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </header>
  )
}
