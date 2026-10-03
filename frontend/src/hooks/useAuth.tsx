/** Session authentication context backed by the GoRoute API. */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import { authApi } from '../services/auth'
import { ApiError } from '../services/api'
import type { User } from '../types'

export interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Restore the session on first load.
  useEffect(() => {
    let active = true
    authApi
      .me()
      .then((result) => {
        if (active) setUser(result.user)
      })
      .catch((error: unknown) => {
        if (error instanceof ApiError && error.status === 401) return
        // Network/server issues should not block the app shell.
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const result = await authApi.login(email, password)
    setUser(result.user)
  }, [])

  const signup = useCallback(
    async (name: string, email: string, password: string) => {
      const result = await authApi.signup(name, email, password)
      setUser(result.user)
    },
    [],
  )

  const logout = useCallback(async () => {
    await authApi.logout()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, login, signup, logout }),
    [user, loading, login, signup, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside an AuthProvider')
  }
  return context
}
