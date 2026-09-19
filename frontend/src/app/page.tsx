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
      <main className="mx-auto w-full max-w-4xl flex-1 px-5 py-14">
        <h1 className="font-heading text-4xl font-semibold tracking-tight md:text-5xl">Who&apos;s shopping?</h1>
        <p className="mt-3 max-w-xl text-lg text-muted-foreground">
          Pick a profile. You&apos;ll see clothes from the catalog on that person&apos;s photo.
        </p>

        {error && <p className="mt-8 text-destructive">Couldn&apos;t load profiles: {error.message}</p>}

        <ul className="mt-10 grid grid-cols-2 gap-5 sm:grid-cols-3">
          {isLoading &&
            Array.from({ length: 3 }).map((_, i) => (
              <li key={i}>
                <Skeleton className="aspect-[3/4] w-full rounded-2xl" />
              </li>
            ))}
          {users?.map((u) => (
            <li key={u.id}>
              <Link
                href={`/u/${u.id}`}
                className="group block rounded-2xl outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                <div className="aspect-[3/4] overflow-hidden rounded-2xl border border-border">
                  {u.image_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={u.image_url} alt="" className="h-full w-full object-cover" />
                  ) : (
                    <Silhouette className="h-full w-full" />
                  )}
                </div>
                <div className="mt-3 text-lg font-semibold group-hover:text-primary">{u.username}</div>
                <p className="line-clamp-2 text-sm text-muted-foreground">{u.preferences}</p>
              </Link>
            </li>
          ))}
        </ul>
      </main>
    </>
  )
}
