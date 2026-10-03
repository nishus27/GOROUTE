/** Journey planning, scoring, rerouting and explanation clients. */

import { api } from './api'
import type {
  RerouteRequest,
  RerouteResult,
  RouteOption,
  SearchRequest,
  SearchResult,
} from '../types'

export const routesApi = {
  /** Plan a journey: scored + ranked multimodal routes and a recommendation. */
  search: (request: SearchRequest) =>
    api.post<SearchResult>('/routes/search', request),

  /** Re-evaluate every candidate after an incident and re-rank them. */
  reroute: (request: RerouteRequest) =>
    api.post<RerouteResult>('/routes/reroute', request),

  /** Pure engine call: score an explicit set of routes. */
  score: (routes: RouteOption[], preference: string) =>
    api.post<{ ranked: RouteOption[]; recommended_route_id: string }>(
      '/routes/score',
      { routes, preference },
    ),
}

export const aiApi = {
  explain: (source: string, destination: string, preference: string, routes: RouteOption[]) =>
    api.post<{ explanation: string; source: string }>('/ai/explain-route', {
      source,
      destination,
      preference,
      routes,
    }),
}
