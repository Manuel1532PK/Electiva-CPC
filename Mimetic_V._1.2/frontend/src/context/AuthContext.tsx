import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { AUTH_EVENT, apiFetch, errorMessage } from '../api/client'

type User = {
  id: string
  email: string
  name: string
  role: string
  hospital_id: string
  first_name: string
  last_name: string
  created_at: string
}

type AuthContextType = {
  user: User | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, name: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  const clearSession = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }
    const run = async () => {
      try {
        const res = await apiFetch('/api/auth/me')
        if (!res.ok) throw new Error('Invalid token')
        setUser(await res.json())
      } catch {
        clearSession()
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [token])

  useEffect(() => {
    window.addEventListener(AUTH_EVENT, clearSession)
    return () => window.removeEventListener(AUTH_EVENT, clearSession)
  }, [])

  const login = async (email: string, password: string) => {
    const res = await apiFetch('/api/auth/login', {
      method: 'POST',
      auth: false,
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) throw new Error(await errorMessage(res, 'Login failed'))
    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }

  const register = async (email: string, name: string, password: string) => {
    const res = await apiFetch('/api/auth/register', {
      method: 'POST',
      auth: false,
      body: JSON.stringify({ email, name, password }),
    })
    if (!res.ok) throw new Error(await errorMessage(res, 'Registration failed'))
    const data = await res.json()
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
    setUser(data.user)
  }

  const logout = () => {
    clearSession()
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}