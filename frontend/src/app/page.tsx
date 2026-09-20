"use client"

import Link from "next/link"
import { Header } from "@/components/shop/header"
import { Silhouette } from "@/components/shop/silhouette"
import { Skeleton } from "@/components/ui/skeleton"
import { useUsers } from "@/hooks/queries"

export default function PickUserPage() {
  const { data: users, isLoading, error } = useUsers()

  return (
    <>
      <Header />
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col items-center px-5 py-14 text-center">
        <h1 className="font-heading text-4xl font-semibold tracking-tight md:text-5xl">Who&apos;s shopping?</h1>
        <p className="mt-3 max-w-md text-lg text-muted-foreground">Pick your profile to start trying things on.</p>

        {error && <p className="mt-8 text-destructive">Couldn&apos;t load profiles: {error.message}</p>}

        <ul className="mt-10 flex flex-wrap justify-center gap-6">
          {isLoading && (
            <li>
              <Skeleton className="aspect-[3/4] w-56 rounded-2xl" />
            </li>
          )}
          {users?.map((u) => (
            <li key={u.username} className="w-56">
              <Link
                href={`/u/${encodeURIComponent(u.username)}`}
                className="group block rounded-2xl outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                <div className="aspect-[3/4] overflow-hidden rounded-2xl border border-border bg-secondary group-hover:border-primary">
                  {u.image_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={u.image_url} alt={`Photo of ${u.username}`} className="h-full w-full object-cover" />
                  ) : (
                    <Silhouette className="h-full w-full" />
                  )}
                </div>
                <div className="mt-3 text-lg font-semibold group-hover:text-primary">{u.username}</div>
              </Link>
            </li>
          ))}
        </ul>
      </main>
    </>
  )
}
