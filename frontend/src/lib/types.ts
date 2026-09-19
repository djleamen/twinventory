/** Matches the backend's Product schema (services/elastic_client.py). */
export type Product = {
  id: string
  title: string
  description: string
  image: string
  price: number
  category: string
  url: string
}

/** Not in the backend yet — served by the mock in lib/api/users.ts. */
export type User = {
  id: string
  username: string
  image_url: string
  preferences: string
}

export type TryOnResponse = {
  /** base64-encoded image, no data: prefix */
  image: string
}
