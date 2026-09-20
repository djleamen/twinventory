"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Loader2Icon, PlusIcon, UserRoundIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useCreateUser } from "@/hooks/queries"

/** A "Create your own" card for the profile picker, plus the dialog it opens. */
export function CreateProfileCard() {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [username, setUsername] = useState("")
  const [photo, setPhoto] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const createUser = useCreateUser()

  function onPhotoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null
    setPhoto(file)
    setPreview((old) => {
      if (old) URL.revokeObjectURL(old)
      return file ? URL.createObjectURL(file) : null
    })
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!photo || createUser.isPending) return
    createUser.mutate(
      { username: username.trim().toLowerCase(), photo },
      { onSuccess: (user) => router.push(`/u/${encodeURIComponent(user.username)}`) },
    )
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="group block w-full rounded-2xl outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
      >
        <div className="flex aspect-[3/4] flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-border bg-secondary/50 text-muted-foreground group-hover:border-primary group-hover:text-primary">
          <PlusIcon className="size-10" aria-hidden="true" />
        </div>
        <div className="mt-3 text-lg font-semibold group-hover:text-primary">Create your own</div>
      </button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Create your profile</DialogTitle>
            <DialogDescription>
              Pick a name and upload a full-body photo — it becomes your try-on twin. Your photo stays
              in this browser tab and is never stored.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={onSubmit} className="flex flex-col gap-4">
            <label className="group mx-auto block w-40 cursor-pointer">
              <span className="sr-only">Profile photo</span>
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={onPhotoChange}
                className="sr-only"
              />
              <span className="flex aspect-[3/4] items-center justify-center overflow-hidden rounded-xl border-2 border-dashed border-border bg-secondary group-hover:border-primary">
                {preview ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={preview} alt="Your photo" className="h-full w-full object-cover" />
                ) : (
                  <span className="flex flex-col items-center gap-2 px-4 text-center text-sm text-muted-foreground">
                    <UserRoundIcon className="size-8" aria-hidden="true" />
                    Upload a photo
                  </span>
                )}
              </span>
            </label>

            <Input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Your name"
              required
              maxLength={30}
              autoFocus
            />

            {createUser.isError && (
              <p className="text-sm text-destructive">{createUser.error.message}</p>
            )}

            <Button type="submit" disabled={!photo || !username.trim() || createUser.isPending}>
              {createUser.isPending && <Loader2Icon className="size-4 animate-spin" aria-hidden="true" />}
              {createUser.isPending ? "Creating…" : "Start shopping"}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}
