/** Secondary domain API clients (journeys, notifications, insights, ...). */

import { api } from './api'
import type {
  AppNotification,
  Booking,
  DailyCommute,
  SavedPlace,
  StoredJourney,
  WeeklyInsights,
} from '../types'

export const journeysApi = {
  list: () => api.get<{ journeys: StoredJourney[] }>('/journeys'),
  get: (id: number) => api.get<{ journey: StoredJourney }>(`/journeys/${id}`),
}

export const notificationsApi = {
  list: () =>
    api.get<{ notifications: AppNotification[]; unread_count: number }>(
      '/notifications',
    ),
  markRead: (id: number) =>
    api.post<{ notification: AppNotification }>(`/notifications/${id}/read`),
  markAllRead: () => api.post<{ success: boolean }>('/notifications/read-all'),
}

export const insightsApi = {
  weekly: () => api.get<WeeklyInsights>('/weekly-insights'),
}

export const savedPlacesApi = {
  list: () => api.get<{ saved_places: SavedPlace[] }>('/saved-places'),
  create: (payload: Omit<SavedPlace, 'id' | 'created_at'>) =>
    api.post<{ saved_place: SavedPlace }>('/saved-places', payload),
  update: (id: number, payload: Omit<SavedPlace, 'id' | 'created_at'>) =>
    api.put<{ saved_place: SavedPlace }>(`/saved-places/${id}`, payload),
  remove: (id: number) => api.del<{ success: boolean }>(`/saved-places/${id}`),
}

export const dailyCommuteApi = {
  get: () => api.get<{ daily_commute: DailyCommute | null }>('/daily-commute'),
  save: (payload: Record<string, unknown>) =>
    api.post<{ daily_commute: DailyCommute }>('/daily-commute', payload),
  update: (payload: Record<string, unknown>) =>
    api.put<{ daily_commute: DailyCommute }>('/daily-commute', payload),
}

export const bookingsApi = {
  list: () => api.get<{ bookings: Booking[] }>('/bookings'),
  create: (payload: Record<string, unknown>) =>
    api.post<{ booking: Booking }>('/bookings', payload),
  cancel: (id: number) =>
    api.post<{ booking: Booking }>(`/bookings/${id}/cancel`),
}
