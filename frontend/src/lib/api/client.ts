export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "")

/** Local uploads come back as /static/... paths — point them at the API host. */
export function toApiUrl(url: string): string {
  return url.startsWith("/") ? `${API_URL}${url}` : url
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `Request failed with status ${res.status}`
    try {
      const body = await res.json()
      if (typeof body?.detail === "string") message = body.detail
    } catch {}
    throw new ApiError(res.status, message)
  }
  return res.json() as Promise<T>
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
  return handleResponse<T>(res)
}

/** For multipart/form-data uploads — the browser sets the Content-Type boundary itself. */
export async function apiFetchForm<T>(path: string, formData: FormData): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_URL}${path}`, { method: "POST", body: formData })
  } catch {
    throw new ApiError(0, `Can't reach the API at ${API_URL}. Is the backend running?`)
  }
  return handleResponse<T>(res)
}
