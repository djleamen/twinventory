import type { User } from "@/lib/types"
import { apiFetch } from "./client"

/** GET /users/{username} */
export function getUser(username: string): Promise<User> {
  return apiFetch<User>(`/users/${encodeURIComponent(username)}`)
}

/** GET /users — every preset profile on the "Who's shopping?" screen. */
export function getUsers(): Promise<User[]> {
  return apiFetch<User[]>("/users")
}

/** PATCH /users/{username}/preferences */
export function updatePreferences(username: string, preferences: string): Promise<User> {
  return apiFetch<User>(`/users/${encodeURIComponent(username)}/preferences`, {
    method: "PATCH",
    body: JSON.stringify({ preferences }),
  })
}
