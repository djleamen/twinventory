/**
 * MOCK user service. The backend has no user endpoints yet.
 * Replace each function body with an apiFetch call when these exist:
 *   GET   /users              -> User[]
 *   GET   /users/{id}         -> User
 *   PATCH /users/{id}         -> User   body: { preferences }
 */
import type { User } from "@/lib/types"
import { sleep } from "./client"
import { MOCK_USERS } from "@/lib/mock/users"

const users = new Map<string, User>(MOCK_USERS.map((u) => [u.id, { ...u }]))

export async function getUsers(): Promise<User[]> {
  await sleep(150)
  return [...users.values()]
}

export async function getUser(id: string): Promise<User> {
  await sleep(150)
  const user = users.get(id)
  if (!user) throw new Error(`No user with id "${id}"`)
  return { ...user }
}

export async function updatePreferences(id: string, preferences: string): Promise<User> {
  await sleep(200)
  const user = users.get(id)
  if (!user) throw new Error(`No user with id "${id}"`)
  const next = { ...user, preferences }
  users.set(id, next)
  return { ...next }
}
