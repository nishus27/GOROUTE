/** Route Results — scored routes, recommendation, comparison and rerouting. */

import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { routesApi } from '../services/routes'
import { RouteCard } from '../components/RouteCard'
import { RouteComparison } from '../components/RouteComparison'
import { ScoreBadge } from '../components/ScoreBadge'
import { ErrorBanner, LoadingSpinner } from '../components/StateMessages'
import {
  PREFERENCE_LABELS,
  formatDistance,
  formatDuration,
} from '../utils/format'
import type { Preference, RerouteResult, SearchResult } from '../types'

const INCIDENT_TYPES = [
  { value: 'traffic', label: 'Traffic congestion' },
  { value: 'delay', label: 'Service delay' },
]

export function RouteResults() {
  const [params] = useSearchParams()
  const source = params.get('source') ?? ''
  const destination = params.get('destination') ?? ''
  const preference = (params.get('preference') ?? 'balanced') as Preference
  const departureTime = params.get('departure_time')
  const modesParam = params.get('modes')

  const [result, setResult] = useState<SearchResult | null>(null)
  const [reroute, setReroute] = useState<RerouteResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const [incidentRouteId, setIncidentRouteId] = useState('')
  const [incidentType, setIncidentType] = useState('traffic')
  const [delayMinutes, setDelayMinutes] = useState(15)
  const [rerouting, setRerouting] = useState(false)
  const [rerouteError, setRerouteError] = useState('')

  const search = useCallback(async () => {
    if (!source || !destination) {
      setError('Missing source or destination. Start a new search.')
      setLoading(false)
      return
    }
    setLoading(true)
    setError('')
    try {
      const modes = modesParam?.split(',').filter(Boolean)
      const data = await routesApi.search({
        source,
        destination,
        preference,
        departure_time: departureTime,
        modes: modes && modes.length ? modes : undefined,
      })
      setResult(data)
      setReroute(null)
      setIncidentRouteId(data.recommended_route_id)
      setExpandedId(data.recommended_route_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load routes')
    } finally {
      setLoading(false)
    }
  }, [source, destination, preference, departureTime, modesParam])

  useEffect(() => {
    void search()
  }, [search])

  const routes = useMemo(
    () => reroute?.routes ?? result?.routes ?? [],
    [reroute, result],
  )
  const recommendedId =
    reroute?.recommended_route_id ?? result?.recommended_route_id ?? ''
  const recommended = routes.find((route) => route.id === recommendedId)
  const explanation = reroute?.explanation ?? result?.explanation ?? ''
  const previousId = reroute?.previous_recommended_route_id

  async function handleReroute() {
    setRerouting(true)
    setRerouteError('')
    try {
      const data = await routesApi.reroute({
        source,
        destination,
        preference,
        departure_time: departureTime,
        incident: {
          type: incidentType,
          route_id: incidentRouteId || recommendedId,
          delay_minutes: delayMinutes,
        },
        previous_recommended_route_id: recommendedId,
      })
      setReroute(data)
      setExpandedId(data.recommended_route_id)
    } catch (err) {
      setRerouteError(err instanceof Error ? err.message : 'Reroute failed')
    } finally {
      setRerouting(false)
    }
  }

  if (loading) {
    return (
      <div className="page">
        <LoadingSpinner label="Scoring routes…" />
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="page">
        <ErrorBanner message={error || 'No routes available'} />
        <Link className="btn btn--primary" to="/plan">
          Plan a journey
        </Link>
      </div>
    )
  }

  return (
    <div className="page">
      <header className="page__head">
        <h1>
          {result.source} <span className="arrow">→</span> {result.destination}
        </h1>
        <p>
          {formatDistance(result.distance_km * 1000)} ·{' '}
          {PREFERENCE_LABELS[result.preference] ?? result.preference} preference ·{' '}
          {routes.length} routes compared
        </p>
      </header>

      {reroute ? (
        <div
          className={reroute.changed ? 'banner banner--change' : 'banner banner--info'}
          role="status"
        >
          <strong>
            {reroute.changed
              ? 'Recommendation updated after rerouting'
              : 'Recommendation unchanged after rerouting'}
          </strong>
          <span>{reroute.change_reason}</span>
          <span className="banner__meta">
            All {reroute.routes.length} routes were re-scored and re-ranked.
            {reroute.changed && previousId ? (
              <>
                {' '}
                Previous best:{' '}
                <em>
                  {routes.find((route) => route.id === previousId)?.mode_summary ??
                    previousId}
                </em>
                .
              </>
            ) : null}
          </span>
        </div>
      ) : null}

      {recommended ? (
        <section className="card recommendation">
          <div className="recommendation__head">
            <div>
              <p className="eyebrow">Recommended route</p>
              <h2>{recommended.mode_summary}</h2>
              <p className="recommendation__stats">
                {formatDuration(recommended.metrics.total_duration_min)} ·{' '}
                {recommended.metrics.transfers} transfer(s) ·{' '}
                {formatDistance(recommended.metrics.walking_distance_m)} walking
              </p>
            </div>
            <ScoreBadge score={recommended.score} label="Score / 100" size="lg" />
          </div>
          {explanation ? <p className="recommendation__why">{explanation}</p> : null}
        </section>
      ) : null}


      <section className="section">
        <h2 className="section__title">All routes</h2>
        <div className="route-list">
          {routes.map((route) => (
            <RouteCard
              key={route.id}
              route={route}
              isRecommended={route.id === recommendedId}
              isAffected={Boolean(route.incident_applied)}
              expanded={expandedId === route.id}
              onToggle={() =>
                setExpandedId((current) => (current === route.id ? null : route.id))
              }
            />
          ))}
        </div>
      </section>

      <section className="section">
        <h2 className="section__title">Route comparison</h2>
        <RouteComparison routes={routes} recommendedRouteId={recommendedId} />
      </section>

      <section className="card reroute">
        <h2>Traffic &amp; delay simulation</h2>
        <p className="hint">
          Apply a real-world disruption to any route. GoRoute recalculates and
          re-ranks every candidate, then updates the recommendation.
        </p>

        {rerouteError ? (
          <ErrorBanner message={rerouteError} onDismiss={() => setRerouteError('')} />
        ) : null}

        <div className="grid grid--3">
          <label className="field">
            <span>Affected route</span>
            <select
              value={incidentRouteId}
              onChange={(event) => setIncidentRouteId(event.target.value)}
            >
              {routes.map((route) => (
                <option key={route.id} value={route.id}>
                  {route.mode_summary}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Incident type</span>
            <select
              value={incidentType}
              onChange={(event) => setIncidentType(event.target.value)}
            >
              {INCIDENT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>Added delay (minutes)</span>
            <input
              type="number"
              min={1}
              max={180}
              value={delayMinutes}
              onChange={(event) =>
                setDelayMinutes(Math.max(1, Number(event.target.value) || 1))
              }
            />
          </label>
        </div>

        <div className="reroute__actions">
          <button
            type="button"
            className="btn btn--primary"
            onClick={handleReroute}
            disabled={rerouting}
          >
            {rerouting ? 'Recalculating…' : 'Apply incident & reroute'}
          </button>
          {reroute ? (
            <button
              type="button"
              className="btn btn--ghost"
              onClick={() => {
                setReroute(null)
                setIncidentRouteId(recommendedId)
              }}
            >
              Reset to original
            </button>
          ) : null}
        </div>
      </section>

      <div className="page__foot">
        <Link className="btn btn--ghost" to="/plan">
          Plan another journey
        </Link>
      </div>
    </div>
  )
}

