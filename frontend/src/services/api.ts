/** Fetch wrapper for the GoRoute backend API. */

const RAW_BASE = import.meta.env.VITE_API_BASE_URL

/** Backend API base. Falls back to the Vite dev proxy (same-origin cookies). */
export const API_BASE = RAW_BASE ? `${RAW_BASE.replace(/\/+$/, '')}/api` : '/api'

export class ApiError extends Error {
  code: string
  status: number

  constructor(code: string, message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
}

/** Perform a JSON request against the API, throwing ApiError on failure. */
export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? 'GET',
    credentials: 'include',
    headers: options.body ? { 'Content-Type': 'application/json' } : undefined,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  const text = await response.text()
  const payload = text ? (JSON.parse(text) as unknown) : {}

  if (!response.ok) {
    const error = (payload as { error?: { code?: string; message?: string } }).error
    throw new ApiError(
      error?.code ?? 'REQUEST_FAILED',
      error?.message ?? 'Something went wrong. Please try again.',
      response.status,
    )
  }

  return payload as T
}

export const api = {
  get: <T>(path: string) => apiRequest<T>(path),
  post: <T>(path: string, body?: unknown) =>
    apiRequest<T>(path, { method: 'POST', body }),
  put: <T>(path: string, body?: unknown) =>
    apiRequest<T>(path, { method: 'PUT', body }),
  del: <T>(path: string) => apiRequest<T>(path, { method: 'DELETE' }),
}
