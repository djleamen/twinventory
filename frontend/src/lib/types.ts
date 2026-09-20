/** Matches the backend's Product (services/elastic_client.py). */
export type Product = {
  id: string
  title: string
  description: string
  image: string
  price: number
  category: string
  url: string
}

/** Matches the backend's User (services/mongo_client.py). */
export type User = {
  username: string
  image_url: string
  preferences: string
}

export type TryOnResponse = {
  /** base64-encoded image, no data: prefix */
  image: string
}
