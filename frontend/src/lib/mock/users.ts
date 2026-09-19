import type { User } from "@/lib/types"

/**
 * image_url must be a PUBLIC url (http/https) — the backend passes it straight to
 * OpenAI, which can't read localhost. Paste a hosted full-body photo for each user.
 * Leave it empty to show the placeholder silhouette (Try On is disabled then).
 */
export const MOCK_USERS: User[] = [
  {
    id: "maya",
    username: "maya",
    image_url: "",
    preferences: "Relaxed fits, earthy neutrals, nothing too formal. Mostly linen and cotton.",
  },
  {
    id: "jordan",
    username: "jordan",
    image_url: "",
    preferences: "Clean streetwear, hoodies and sneakers. Muted colors.",
  },
  {
    id: "sam",
    username: "sam",
    image_url: "",
    preferences: "Office-ready but comfortable. Blazers, trousers, a good watch.",
  },
]
