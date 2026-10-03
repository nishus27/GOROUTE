/** Insights — weekly aggregates over the user's planned journeys. */

import { useEffect, useState } from 'react'
import { insightsApi } from '../services/domain'
import { ErrorBanner, LoadingSpinner } from '../components/StateMessages'
import { formatCurrency, formatDuration } from '../utils/format'
import type { WeeklyInsights } from '../types'

export function Insights() {
  const [insights, setInsights] = useState<WeeklyInsights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    insightsApi
      .weekly()
      .then((result) => {
        if (active) setInsights(result)
      })
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Unable to load insights'),
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
        <LoadingSpinner label="Crunching your weekly insights…" />
      </div>
    )
  }

  if (error || !insights) {
    return (
      <div className="page">
        <ErrorBanner message={error || 'No insights available'} />
      </div>
    )
  }

  const maxCount = insights.mode_breakdown.reduce(
    (max, item) => Math.max(max, item.count),
    0,
  )

  return (
    <div className="page">
      <header className="page__head">
        <h1>Weekly insights</h1>
        <p>How you travelled over the last {insights.period_days} days.</p>
      </header>

      <section className="stat-grid">
        <div className="stat">
          <span className="stat__value">{insights.total_journeys}</span>
          <span className="stat__label">Journeys planned</span>
        </div>
        <div className="stat">
          <span className="stat__value">{formatDuration(insights.total_time_min)}</span>
          <span className="stat__label">Time on the move</span>
        </div>
        <div className="stat">
          <span className="stat__value">{formatCurrency(insights.total_cost)}</span>
          <span className="stat__label">Total fare</span>
        </div>
        <div className="stat">
          <span className="stat__value">{insights.total_transfers}</span>
          <span className="stat__label">Transfers</span>
        </div>
        <div className="stat">
          <span className="stat__value">{insights.route_changes}</span>
          <span className="stat__label">Reroutes triggered</span>
        </div>
      </section>

      <section className="card">
        <h2>Mode breakdown</h2>
        {insights.mode_breakdown.length ? (
          <div className="factors">
            {insights.mode_breakdown.map((item) => (
              <div className="factor" key={item.mode}>
                <span className="factor__label">{item.mode}</span>
                <span className="factor__track">
                  <span
                    className="factor__fill"
                    style={{
                      width: `${maxCount ? Math.round((item.count / maxCount) * 100) : 0}%`,
                    }}
                  />
                </span>
                <span className="factor__value">{item.count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="hint">No journeys in this period.</p>
        )}
      </section>
    </div>
  )
}
