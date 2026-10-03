/** Dashboard — the signed-in home screen. */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { dailyCommuteApi, journeysApi, notificationsApi } from '../services/domain'
import { EmptyState, ErrorBanner, LoadingSpinner } from '../components/StateMessages'
import { PREFERENCE_LABELS, formatDateTime, formatDuration } from '../utils/format'
import type { AppNotification, DailyCommute, Preference, StoredJourney } from '../types'

export function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [commute, setCommute] = useState<DailyCommute | null>(null)
  const [journeys, setJourneys] = useState<StoredJourney[]>([])
  const [notifications, setNotifications] = useState<AppNotification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [source, setSource] = useState('Thane')
  const [destination, setDestination] = useState('Andheri')
  const [preference, setPreference] = useState<Preference>('balanced')

  useEffect(() => {
    let active = true
    Promise.all([
      dailyCommuteApi.get().catch(() => ({ daily_commute: null })),
      journeysApi.list().catch(() => ({ journeys: [] })),
      notificationsApi.list().catch(() => ({ notifications: [], unread_count: 0 })),
    ])
      .then(([commuteResult, journeyResult, notificationResult]) => {
        if (!active) return
        setCommute(commuteResult.daily_commute)
        setJourneys(journeyResult.journeys.slice(0, 5))
        setNotifications(notificationResult.notifications.slice(0, 3))
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : 'Unable to load your dashboard')
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  function handleQuickPlan(event: React.FormEvent) {
    event.preventDefault()
    const params = new URLSearchParams({ source, destination, preference })
    navigate(`/results?${params.toString()}`)
  }

  if (loading) {
    return (
      <div className="page">
        <LoadingSpinner label="Loading your dashboard…" />
      </div>
    )
  }

  return (
    <div className="page">
      <header className="page__head">
        <h1>Hello{user?.name ? `, ${user.name}` : ''}</h1>
        <p>Plan a trip, review your commute and keep up with route changes.</p>
      </header>

      {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}

      <div className="grid grid--2">
        <section className="card">
          <h2>Quick plan</h2>
          <form className="form" onSubmit={handleQuickPlan}>
            <div className="grid grid--2">
              <label className="field">
                <span>From</span>
                <input
                  value={source}
                  onChange={(event) => setSource(event.target.value)}
                  required
                />
              </label>
              <label className="field">
                <span>To</span>
                <input
                  value={destination}
                  onChange={(event) => setDestination(event.target.value)}
                  required
                />
              </label>
            </div>
            <label className="field">
              <span>Preference</span>
              <select
                value={preference}
                onChange={(event) => setPreference(event.target.value as Preference)}
              >
                {Object.entries(PREFERENCE_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" className="btn btn--primary">
              Find Best Route
            </button>
          </form>
          <p className="hint">
            Need departure times or mode filters?{' '}
            <Link to="/plan">Open the full planner</Link>.
          </p>
        </section>

        <section className="card">
          <h2>Your daily commute</h2>
          {commute ? (
            <div className="commute-summary">
              <p className="commute-summary__route">
                {commute.source} <span className="arrow">→</span> {commute.destination}
              </p>
              <p className="hint">
                {PREFERENCE_LABELS[commute.preference] ?? commute.preference} ·{' '}
                {commute.days_of_week} · {commute.is_active ? 'Active' : 'Paused'}
              </p>
              <Link
                className="btn btn--ghost"
                to={`/results?${new URLSearchParams({
                  source: commute.source,
                  destination: commute.destination,
                  preference: commute.preference,
                }).toString()}`}
              >
                See today&apos;s recommendation
              </Link>
            </div>
          ) : (
            <EmptyState
              title="No commute configured"
              hint="Save your regular trip to get a daily recommendation."
            />
          )}
          <p className="hint">
            <Link to="/daily-commute">Manage daily commute</Link>
          </p>
        </section>
      </div>

      <div className="grid grid--2">
        <section className="card">
          <h2>Recent journeys</h2>
          {journeys.length ? (
            <ul className="list">
              {journeys.map((journey) => (
                <li key={journey.id}>
                  <div>
                    <strong>
                      {journey.source} <span className="arrow">→</span>{' '}
                      {journey.destination}
                    </strong>
                    <span className="list__meta">
                      {formatDateTime(journey.created_at)} ·{' '}
                      {PREFERENCE_LABELS[journey.preference] ?? journey.preference}
                      {journey.routes?.length
                        ? ` · ${journey.routes.length} routes compared`
                        : ''}
                    </span>
                  </div>
                  <span className="list__value">
                    {journey.routes?.[0]
                      ? formatDuration(journey.routes[0].metrics.total_duration_min)
                      : ''}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title="No journeys yet"
              hint="Your planned trips will appear here."
            />
          )}
          <p className="hint">
            <Link to="/history">View full history</Link>
          </p>
        </section>

        <section className="card">
          <h2>Latest notifications</h2>
          {notifications.length ? (
            <ul className="list">
              {notifications.map((item) => (
                <li key={item.id}>
                  <div>
                    <strong>{item.title}</strong>
                    <span className="list__meta">{item.message}</span>
                  </div>
                  <span className="list__value">{formatDateTime(item.created_at)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState title="Nothing new" hint="Route changes will show up here." />
          )}
          <p className="hint">
            <Link to="/insights">See weekly insights</Link>
          </p>
        </section>
      </div>
    </div>
  )
}

