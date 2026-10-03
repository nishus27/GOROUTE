/** Formatting helpers shared across pages. */

export function formatDuration(minutes: number): string {
  const total = Math.max(0, Math.round(minutes))
  const hours = Math.floor(total / 60)
  const mins = total % 60
  if (hours === 0) return `${mins} min`
  if (mins === 0) return `${hours} h`
  return `${hours} h ${mins} min`
}

export function formatCurrency(amount: number): string {
  return `\u20b9${Math.round(amount)}`
}

export function formatDistance(metres: number): string {
  if (metres < 1000) return `${Math.round(metres)} m`
  return `${(metres / 1000).toFixed(1)} km`
}

export function formatKm(km: number): string {
  return `${km.toFixed(1)} km`
}

export function formatPercent(ratio: number): string {
  return `${Math.round(ratio * 100)}%`
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString(undefined, {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const PREFERENCE_LABELS: Record<string, string> = {
  balanced: 'Balanced',
  fastest: 'Fastest',
  cheapest: 'Cheapest',
  most_reliable: 'Most reliable',
  least_walking: 'Least walking',
}

export const PREFERENCE_HINTS: Record<string, string> = {
  balanced: 'Travel time 30% · Reliability 20% · Cost 15% · Waiting 10% · Transfers 10% · Walking 15%',
  fastest: 'Prioritises the shortest travel time',
  cheapest: 'Prioritises the lowest fare',
  most_reliable: 'Prioritises consistency and punctuality',
  least_walking: 'Minimises walking distance',
}

export const FACTOR_LABELS: Record<string, string> = {
  time: 'Travel time',
  reliability: 'Reliability',
  cost: 'Cost',
  waiting: 'Waiting',
  transfers: 'Transfers',
  walking: 'Walking',
}

export function scoreTone(score: number): 'best' | 'good' | 'fair' {
  if (score >= 80) return 'best'
  if (score >= 60) return 'good'
  return 'fair'
}
