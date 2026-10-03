/** Daily Commute — configure and re-evaluate a recurring trip. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { dailyCommuteApi } from '../services/domain'
import { ErrorBanner, LoadingSpinner } from '../components/StateMessages'
import { PREFERENCE_HINTS, PREFERENCE_LABELS } from '../utils/format'
import type { DailyCommute as CommuteModel, Preference } from '../types'

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

export function DailyCommute() {
  const [commute, setCommute] = useState<CommuteModel | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const [source, setSource] = useState('Thane')
  const [destination, setDestination] = useState('Andheri')
  const [departureTime, setDepartureTime] = useState('09:00')
  const [days, setDays] = useState<string[]>(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
  const [preference, setPreference] = useState<Preference>('balanced')
  const [isActive, setIsActive] = useState(true)

  useEffect(() => {
    let active = true
    dailyCommuteApi
      .get()
      .then((result) => {
        if (!active) return
        setCommute(result.daily_commute)
        if (result.daily_commute) {
          setSource(result.daily_commute.source)
          setDestination(result.daily_commute.destination)
          setDepartureTime(result.daily_commute.departure_time ?? '')
          setDays(result.daily_commute.days_of_week.split(',').filter(Boolean))
          setPreference(result.daily_commute.preference)
          setIsActive(result.daily_commute.is_active)
        }
      })
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Unable to load your commute'),
      )
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  function toggleDay(day: string) {
    setDays((current) =>
      current.includes(day) ? current.filter((item) => item !== day) : [...current, day],
    )
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setNotice('')
    if (!days.length) {
      setError('Select at least one day of the week.')
      return
    }
    setSaving(true)
    const payload = {
      source: source.trim(),
      destination: destination.trim(),
      departure_time: departureTime || null,
      days_of_week: days.join(','),
      preference,
      is_active: isActive,
    }
    try {
      const result = commute
        ? await dailyCommuteApi.update(payload)
        : await dailyCommuteApi.save(payload)
      setCommute(result.daily_commute)
      setNotice('Daily commute saved.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save your commute')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="page">
        <LoadingSpinner label="Loading your commute…" />
      </div>
    )
  }

  return (
    <div className="page">
      <header className="page__head">
        <h1>Daily commute</h1>
        <p>Save the trip you repeat every day. GoRoute keeps it scored and ready.</p>
      </header>

      {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}
      {notice ? (
        <div className="banner banner--info" role="status">
          <span>{notice}</span>
        </div>
      ) : null}

      <form className="card form" onSubmit={handleSubmit}>
        <div className="grid grid--2">
          <label className="field">
            <span>From</span>
            <input
              value={source}
              required
              onChange={(event) => setSource(event.target.value)}
            />
          </label>
          <label className="field">
            <span>To</span>
            <input
              value={destination}
              required
              onChange={(event) => setDestination(event.target.value)}
            />
          </label>
        </div>

        <div className="grid grid--2">
          <label className="field">
            <span>Departure time</span>
            <input
              type="time"
              value={departureTime}
              onChange={(event) => setDepartureTime(event.target.value)}
            />
          </label>
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
        </div>
        <p className="hint">{PREFERENCE_HINTS[preference]}</p>

        <fieldset className="fieldset">
          <legend>Days</legend>
          <div className="chip-row">
            {DAYS.map((day) => (
              <button
                key={day}
                type="button"
                className={days.includes(day) ? 'chip chip--active' : 'chip'}
                onClick={() => toggleDay(day)}
              >
                {day}
              </button>
            ))}
          </div>
        </fieldset>

        <label className="checkbox">
          <input
            type="checkbox"
            checked={isActive}
            onChange={(event) => setIsActive(event.target.checked)}
          />
          <span>Keep this commute active</span>
        </label>

        <div className="reroute__actions">
          <button type="submit" className="btn btn--primary" disabled={saving}>
            {saving ? 'Saving…' : commute ? 'Update commute' : 'Save commute'}
          </button>
          <Link
            className="btn btn--ghost"
            to={`/results?${new URLSearchParams({
              source,
              destination,
              preference,
            }).toString()}`}
          >
            Preview today&apos;s routes
          </Link>
        </div>
      </form>
    </div>
  )
}

