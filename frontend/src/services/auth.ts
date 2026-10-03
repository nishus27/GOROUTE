/** Authentication API client. */

import { api } from './api'
import type { User } from '../types'

interface UserResponse {
  user: User
}

export const authApi = {
  signup: (name: string, email: string, password: string) =>
    api.post<UserResponse>('/auth/signup', { name, email, password }),

  login: (email: string, password: string) =>
    api.post<UserResponse>('/auth/login', { email, password }),

  logout: () => api.post<{ success: boolean }>('/auth/logout'),

  me: () => api.get<UserResponse>('/auth/me'),
}
