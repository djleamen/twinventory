import type { Product, TryOnResponse } from "@/lib/types"
import { apiFetch } from "./client"

function qs(params: Record<string, string | undefined>) {
  const sp = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) if (v) sp.set(k, v)
  const s = sp.toString()
  return s ? `?${s}` : ""
}

/** Accepts a plain array, or an object wrapping one (e.g. { products: [...] }). */
function toProducts(data: unknown): Product[] {
  if (Array.isArray(data)) return data
  if (data && typeof data === "object") {
    const list = Object.values(data).find(Array.isArray)
    if (list) return list as Product[]
  }
  console.error("Unexpected products response:", data)
  throw new Error("The products response wasn't a list. Check the browser console for what came back.")
}

/** GET /products — up to 20 products, optional exact category filter. */
export async function listProducts(category?: string): Promise<Product[]> {
  return toProducts(await apiFetch<unknown>(`/products${qs({ category })}`))
}

/** GET /products/search — semantic search, optional exact category filter. */
export async function searchProducts(query: string, category?: string): Promise<Product[]> {
  return toProducts(await apiFetch<unknown>(`/products/search${qs({ q: query, category })}`))
}

/** POST /products/try — user image first, then the product images. */
export function tryOn(imageUrls: string[]): Promise<TryOnResponse> {
  return apiFetch<TryOnResponse>("/products/try", {
    method: "POST",
    body: JSON.stringify({ image_urls: imageUrls }),
  })
}
