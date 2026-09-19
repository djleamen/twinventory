export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "")

/** Set NEXT_PUBLIC_MOCK_PRODUCTS=true to run the UI without the backend. */
export const MOCK_PRODUCTS = process.env.NEXT_PUBLIC_MOCK_PRODUCTS === "true"

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    })
  } catch {
    throw new ApiError(0, `Can't reach the API at ${API_URL}. Is the backend running?`)
  }
  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new ApiError(res.status, text || `Request failed with status ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))
