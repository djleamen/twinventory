"use client"

import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query"
import { listProducts, searchProducts, tryOn } from "@/lib/api/products"
import { getUser, getUsers, updatePreferences } from "@/lib/api/users"
import { HIDDEN_CATEGORIES } from "@/lib/slots"
import type { Product, User } from "@/lib/types"

export const keys = {
  users: ["users"] as const,
  user: (username: string) => ["users", username] as const,
  products: (query: string, category?: string) => ["products", query, category ?? null] as const,
}

export function useUsers() {
  return useQuery({ queryKey: keys.users, queryFn: getUsers })
}

export function useUser(username: string) {
  return useQuery({ queryKey: keys.user(username), queryFn: () => getUser(username), retry: false })
}

export function useUpdatePreferences(username: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (preferences: string) => updatePreferences(username, preferences),
    onSuccess: (user: User) => {
      qc.setQueryData(keys.user(username), user)
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
