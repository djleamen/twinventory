import { getUser } from "@/lib/api/users"
import type { User } from "@/lib/types"

const STORAGE_KEY = "twinventory-ephemeral-user"
const MAX_DIMENSION = 1024

/**
 * Session-only profile. The photo lives in sessionStorage as a data URI —
 * nothing is uploaded or persisted, and it's gone when the tab closes.
 */
export function getEphemeralUser(): User | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

export function saveEphemeralUser(user: User): void {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(user))
}

/** Downscale so the data URI fits sessionStorage and API payload limits. */
async function fileToDataUri(file: File): Promise<string> {
  const bitmap = await createImageBitmap(file)
  const scale = Math.min(1, MAX_DIMENSION / Math.max(bitmap.width, bitmap.height))
  const canvas = document.createElement("canvas")
  canvas.width = Math.round(bitmap.width * scale)
  canvas.height = Math.round(bitmap.height * scale)
  canvas.getContext("2d")!.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  return canvas.toDataURL("image/jpeg", 0.85)
}

export async function createEphemeralUser(username: string, photo: File): Promise<User> {
  const name = username.trim().toLowerCase()
  if (!/^[a-z0-9][a-z0-9._-]{0,29}$/.test(name))
    throw new Error("Name must be 1-30 characters: letters, numbers, . _ or -")
  const existing = await getUser(name).catch(() => null)
  if (existing) throw new Error("That name is already taken")

  const user: User = { username: name, image_url: await fileToDataUri(photo), preferences: "" }
  try {
    saveEphemeralUser(user)
  } catch {
    throw new Error("Couldn't keep your photo in this browser session — try a smaller image.")
  }
  return user
}
