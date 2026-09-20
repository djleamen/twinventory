import type { User } from "@/lib/types"
import { apiFetch } from "./client"

/**
 * Usernames shown on the "Who's shopping?" screen.
 * Must match the usernames in the backend's users.json.
 */
export const USERNAMES = ["steve"]

/** GET /users/{username} */
export function getUser(username: string): Promise<User> {
  return apiFetch<User>(`/users/${encodeURIComponent(username)}`)
}

/** Fetches every user in USERNAMES, skipping any that don't exist. */
export async function getUsers(): Promise<User[]> {
  const results = await Promise.allSettled(USERNAMES.map(getUser))
  const users = results.flatMap((r) => (r.status === "fulfilled" ? [r.value] : []))
  if (!users.length) {
    const failed = results.find((r) => r.status === "rejected")
    if (failed?.status === "rejected") throw failed.reason
  }
  return users
}

/** PATCH /users/{username}/preferences */
export function updatePreferences(username: string, preferences: string): Promise<User> {
  return apiFetch<User>(`/users/${encodeURIComponent(username)}/preferences`, {
    method: "PATCH",
    body: JSON.stringify({ preferences }),
  })
}
