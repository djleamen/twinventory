"use client"

import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query"
import { listProducts, searchProducts, tryOn } from "@/lib/api/products"
import { getUser, getUsers, updatePreferences } from "@/lib/api/users"
import { convertToModel } from "@/lib/api/models"
import { createEphemeralUser, getEphemeralUser, saveEphemeralUser } from "@/lib/ephemeral-user"
import { HIDDEN_CATEGORIES } from "@/lib/slots"
import type { Product, User } from "@/lib/types"

export const keys = {
  users: ["users"] as const,
  user: (username: string) => ["users", username] as const,
  products: (query: string, category?: string) => ["products", query, category ?? null] as const,
}

export function useUsers() {
  return useQuery({
    queryKey: keys.users,
    queryFn: async () => {
      const users = await getUsers()
      const ephemeral = getEphemeralUser()
      return ephemeral ? [...users.filter((u) => u.username !== ephemeral.username), ephemeral] : users
    },
  })
}

export function useUser(username: string) {
  return useQuery({
    queryKey: keys.user(username),
    queryFn: () => {
      const ephemeral = getEphemeralUser()
      return ephemeral?.username === username ? ephemeral : getUser(username)
    },
    retry: false,
  })
}

export function useUpdatePreferences(username: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (preferences: string) => {
      const ephemeral = getEphemeralUser()
      if (ephemeral?.username === username) {
        const updated = { ...ephemeral, preferences }
        saveEphemeralUser(updated)
        return updated
      }
      return updatePreferences(username, preferences)
    },
    onSuccess: (user: User) => {
      qc.setQueryData(keys.user(username), user)
      qc.invalidateQueries({ queryKey: keys.users })
    },
  })
}

export function useCreateUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ username, photo }: { username: string; photo: File }) => createEphemeralUser(username, photo),
    onSuccess: (user: User) => {
      qc.setQueryData(keys.user(user.username), user)
      qc.invalidateQueries({ queryKey: keys.users })
    },
  })
}

function fetchProducts(query: string, category?: string) {
  return query ? searchProducts(query, category) : listProducts(category)
}

/**
 * The backend filters by ONE category, so for a slot (several categories)
 * we run one request per category in parallel and merge the results.
 */
export function useProducts(query: string, categories: string[] | undefined) {
  const cats = categories && categories.length ? categories : [undefined]
  return useQueries({
    queries: cats.map((category) => ({
      queryKey: keys.products(query, category),
      queryFn: () => fetchProducts(query, category),
      staleTime: 60_000,
    })),
    combine: (results) => {
      const seen = new Set<string>()
      const products: Product[] = []
      for (const r of results)
        for (const p of r.data ?? [])
          if (!seen.has(p.id) && !HIDDEN_CATEGORIES.has(p.category)) {
            seen.add(p.id)
            products.push(p)
          }
      return {
        products,
        isLoading: results.some((r) => r.isLoading),
        error: results.find((r) => r.error)?.error ?? null,
        refetch: () => results.forEach((r) => r.refetch()),
      }
    },
  })
}

export function useTryOn() {
  return useMutation({
    mutationFn: (imageUrls: string[]) => tryOn(imageUrls),
  })
}

const MODEL_CACHE_TTL = 30 * 60 * 1000 // Meshy links expire, so don't keep them forever

function readCachedModel(storageKey: string): { model_url: string } | null {
  if (storageKey.startsWith("data:")) return null // ephemeral content is never persisted
  try {
    const raw = localStorage.getItem(`model:${storageKey}`)
    if (!raw) return null
    const { model_url, ts } = JSON.parse(raw)
    return Date.now() - ts < MODEL_CACHE_TTL ? { model_url } : null
  } catch {
    return null
  }
}

function writeCachedModel(storageKey: string, modelUrl: string) {
  if (storageKey.startsWith("data:")) return // ephemeral content is never persisted
  try {
    localStorage.setItem(`model:${storageKey}`, JSON.stringify({ model_url: modelUrl, ts: Date.now() }))
  } catch {
    // storage full or unavailable — cache is best-effort
  }
}

/**
 * Converts an image to a 3D model once per image — or once per outfit when a
 * try-on cache key is provided — then reuses the result. Cached in localStorage
 * so refreshes don't wait for regeneration. Ephemeral (data URI) content without
 * a cache key is never persisted anywhere.
 * Only runs while `enabled` is true (i.e. the 3D dialog is open).
 */
export function useModel(imageUrl: string, enabled: boolean, cacheKey?: string | null) {
  const storageKey = cacheKey ? `tryon:${cacheKey}` : imageUrl
  return useQuery({
    queryKey: ["model", storageKey],
    queryFn: async () => {
      const cached = readCachedModel(storageKey)
      if (cached) return cached
      const result = await convertToModel(imageUrl, cacheKey)
      writeCachedModel(storageKey, result.model_url)
      return result
    },
    enabled,
    staleTime: MODEL_CACHE_TTL,
    gcTime: MODEL_CACHE_TTL,
    retry: false,
  })
}
