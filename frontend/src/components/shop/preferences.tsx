"use client"

import { useState } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useUpdatePreferences } from "@/hooks/queries"
import type { User } from "@/lib/types"

export function Preferences({ user }: { user: User }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(user.preferences)
  const save = useUpdatePreferences(user.username)

  function onSave() {
    save.mutate(draft.trim(), {
      onSuccess: () => {
        setEditing(false)
        toast.success("Preferences saved")
      },
      onError: (e) => toast.error(`Couldn't save preferences: ${e.message}`),
    })
  }

  return (
    <section aria-labelledby="prefs-heading" className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h2 id="prefs-heading" className="font-heading text-lg font-semibold">
          Preferences
        </h2>
        {!editing && (
          <Button
            variant="link"
            className="h-auto px-0"
            onClick={() => {
              setDraft(user.preferences)
              setEditing(true)
            }}
          >
            Edit
          </Button>
        )}
      </div>
      {editing ? (
        <div className="flex flex-col gap-2">
          <label htmlFor="prefs" className="sr-only">
            Your style preferences
          </label>
          <Textarea id="prefs" value={draft} onChange={(e) => setDraft(e.target.value)} rows={3} className="bg-card text-[15px]" />
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setEditing(false)}>
              Cancel
            </Button>
            <Button onClick={onSave} disabled={save.isPending}>
              {save.isPending ? "Saving…" : "Save preferences"}
            </Button>
          </div>
        </div>
      ) : (
        <p className="text-[15px] leading-relaxed">
          {user.preferences || <span className="text-muted-foreground">No preferences yet. Add a few words about your style.</span>}
        </p>
      )}
    </section>
  )
}
