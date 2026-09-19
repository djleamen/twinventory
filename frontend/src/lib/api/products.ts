import type { Product, TryOnResponse } from "@/lib/types"
import { apiFetch, MOCK_PRODUCTS, sleep } from "./client"
import { MOCK_PRODUCT_LIST, MOCK_TRY_ON_IMAGE } from "@/lib/mock/products"

function qs(params: Record<string, string | undefined>) {
  const sp = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) if (v) sp.set(k, v)
  const s = sp.toString()
  return s ? `?${s}` : ""
}

/** GET /products/list — up to 20 products, optional exact category filter. */
export async function listProducts(category?: string): Promise<Product[]> {
  if (MOCK_PRODUCTS) {
    await sleep(300)
    return MOCK_PRODUCT_LIST.filter((p) => !category || p.category === category).slice(0, 20)
  }
  return apiFetch<Product[]>(`/products/list${qs({ category })}`)
}

/** GET /products/search — semantic search, optional exact category filter. */
export async function searchProducts(query: string, category?: string): Promise<Product[]> {
  if (MOCK_PRODUCTS) {
    await sleep(400)
    const words = query.toLowerCase().split(/\s+/).filter(Boolean)
    return MOCK_PRODUCT_LIST.filter(
      (p) =>
        (!category || p.category === category) &&
        words.some((w) => `${p.title} ${p.description} ${p.category}`.toLowerCase().includes(w)),
    ).slice(0, 20)
  }
  return apiFetch<Product[]>(`/products/search${qs({ query, category })}`)
}

/** POST /products/try — user image first, then the product images. */
export async function tryOn(imageUrls: string[]): Promise<TryOnResponse> {
  if (MOCK_PRODUCTS) {
    await sleep(2000)
    return { image: MOCK_TRY_ON_IMAGE }
  }
  return apiFetch<TryOnResponse>("/products/try", {
    method: "POST",
    body: JSON.stringify({ image_urls: imageUrls }),
  })
}
