/** Shared domain types for the GoRoute frontend. */

export type Preference =
  | 'balanced'
  | 'fastest'
  | 'cheapest'
  | 'most_reliable'
  | 'least_walking'

export interface User {
  id: number
  name: string
  email: string
  created_at?: string
}

export interface RouteMetrics {
  total_duration_min: number
  total_cost: number
  waiting_time_min: number
  transfers: number
  walking_distance_m: number
  reliability: number
}

export interface RouteLeg {
  mode: string
  mode_label: string
  from: string | number | null
  to: string | number | null
  duration_min: number
  distance_km: number
  cost: number
  instruction?: string
  latitude?: number | null
  longitude?: number | null
}

export interface RouteOption {
  id: string
  mode_summary: string
  modes: string[]
  legs: RouteLeg[]
  metrics: RouteMetrics
  normalized?: Record<string, number>
  score: number
  rank?: number
  is_selected?: boolean
  incident_applied?: Incident
}

export interface Incident {
  type?: string
  delay_minutes?: number
  route_id?: string
}

export interface SearchResult {
  journey_id: number | null
  source: string
  destination: string
  departure_time: string | null
  preference: Preference
  distance_km: number
  weights: Record<string, number>
  routes: RouteOption[]
  recommended_route_id: string
  explanation: string
  explanation_source: string
  route_source: string
}

export interface RerouteResult {
  source: string
  destination: string
  preference: Preference
  weights: Record<string, number>
  routes: RouteOption[]
  recommended_route_id: string
  previous_recommended_route_id: string
  changed: boolean
  change_reason: string
  incident: Incident
  affected_route_id?: string
  explanation: string
  explanation_source: string
  route_source: string
}

export interface SearchRequest {
  source: string
  destination: string
  preference: Preference
  departure_time?: string | null
  modes?: string[]
}

export interface RerouteRequest extends SearchRequest {
  incident: Incident
  previous_recommended_route_id?: string
}

export interface StoredJourney {
  id: number
  source: string
  destination: string
  departure_time: string | null
  preference: Preference
  status: string
  selected_route_id: number | null
  created_at: string
  routes?: RouteOption[]
}

export interface SavedPlace {
  id: number
  label: string
  address: string
  latitude: number | null
  longitude: number | null
  created_at: string
}

export interface DailyCommute {
  id: number
  source: string
  destination: string
  departure_time: string | null
  days_of_week: string
  preference: Preference
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Booking {
  id: number
  route_id: number | null
  provider: string
  status: string
  fare: number
  scheduled_at: string | null
  details: Record<string, unknown>
  created_at: string
}

export interface AppNotification {
  id: number
  type: string
  title: string
  message: string
  is_read: boolean
  created_at: string
}

export interface WeeklyInsights {
  period_days: number
  total_journeys: number
  total_time_min: number
  total_cost: number
  total_transfers: number
  route_changes: number
  mode_breakdown: { mode: string; count: number }[]
}
