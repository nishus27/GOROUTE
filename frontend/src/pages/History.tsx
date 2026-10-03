/** History — previously planned journeys with their compared routes. */

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { journeysApi } from '../services/domain'
import { EmptyState, ErrorBanner, LoadingSpinner } from '../components/StateMessages'
import { RouteComparison } from '../components/RouteComparison'
import { PREFERENCE_LABELS, formatDateTime, formatDuration } from '../utils/format'
import type { StoredJourney } from '../types'

export function History() {
  const [journeys, setJourneys] = useState<StoredJourney[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState<number | null>(null)

  useEffect(() => {
    let active = true
    journeysApi
      .list()
      .then((result) => {
        if (active) setJourneys(result.journeys)
      })
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Unable to load your history'),
      )
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  if (loading) {
    return (
      <div className="page">
        <LoadingSpinner label="Loading your history…" />
      </div>
    )
  }

  return (
    <div className="page">
      <header className="page__head">
        <h1>Journey history</h1>
        <p>Every journey you have planned, with the routes that were compared.</p>
      </header>

      {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}

      {journeys.length ? (
        <div className="stack">
          {journeys.map((journey) => {
            const routes = journey.routes ?? []
            const best = routes.find((route) => route.is_selected) ?? routes[0]
            const expanded = expandedId === journey.id
            return (
              <section className="card" key={journey.id}>
                <header className="route-card__head">
                  <div>
                    <h2>
                      {journey.source} <span className="arrow">→</span>{' '}
                      {journey.destination}
                    </h2>
                    <p className="list__meta">
                      {formatDateTime(journey.created_at)} ·{' '}
                      {PREFERENCE_LABELS[journey.preference] ?? journey.preference} ·{' '}
                      {routes.length} routes compared
                    </p>
                  </div>
                  {best ? (
                    <div className="history__best">
                      <strong>{best.mode_summary}</strong>
                      <span>
                        {formatDuration(best.metrics.total_duration_min)} ·{' '}
                        {best.score.toFixed(1)} pts
                      </span>
                    </div>
                  ) : null}
                </header>

                <div className="route-card__actions">
                  <button
                    type="button"
                    className="btn btn--link"
                    onClick={() =>
                      setExpandedId((current) =>
                        current === journey.id ? null : journey.id,
                      )
                    }
                  >
                    {expanded ? 'Hide comparison' : 'Show comparison'}
                  </button>
                  <Link
                    className="btn btn--link"
                    to={`/results?${new URLSearchParams({
                      source: journey.source,
                      destination: journey.destination,
                      preference: journey.preference,
                    }).toString()}`}
                  >
                    Plan again
                  </Link>
                </div>

                {expanded && routes.length ? (
                  <RouteComparison
                    routes={routes}
                    recommendedRouteId={best?.id ?? ''}
                  />
                ) : null}
              </section>
            )
          })}
        </div>
      ) : (
        <EmptyState
          title="No journeys yet"
          hint="Plan a journey and it will be saved here automatically."
        />
      )}
    </div>
  )
}
