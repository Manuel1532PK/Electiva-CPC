import { API } from '../config'

export const AUTH_EVENT = 'auth:unauthorized'

type ApiOptions = RequestInit & { auth?: boolean }

export function getToken(): string | null {
  return localStorage.getItem('token')
}

function dispatchUnauthorized(): void {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(AUTH_EVENT))
  }
}

export async function apiFetch(path: string, options: ApiOptions = {}): Promise<Response> {
  const { auth = true, headers, ...rest } = options
  const init: RequestInit = { ...rest }
  const h = new Headers(headers)
  if (init.body && !(init.body instanceof FormData) && !h.has('Content-Type')) {
    h.set('Content-Type', 'application/json')
  }
  if (auth) {
    const token = getToken()
    if (token) h.set('Authorization', `Bearer ${token}`)
  }
  if (!h.has('Accept')) h.set('Accept', 'application/json')
  init.headers = h
  const res = await fetch(API + path, init)
  if (res.status === 401 && auth) {
    dispatchUnauthorized()
  }
  return res
}

export async function errorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json()
    return (data && data.detail) || fallback
  } catch {
    return fallback
  }
}