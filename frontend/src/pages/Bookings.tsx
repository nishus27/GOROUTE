/** Bookings — create and cancel bookings for bookable route legs. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { bookingsApi } from '../services/domain'
import { EmptyState, ErrorBanner, LoadingSpinner } from '../components/StateMessages'
import { formatCurrency, formatDateTime } from '../utils/format'
import type { Booking } from '../types'

const PROVIDERS = ['ola', 'uber', 'metro_card', 'bus_pass']

export function Bookings() {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [provider, setProvider] = useState(PROVIDERS[0])
  const [fare, setFare] = useState('120')
  const [scheduledAt, setScheduledAt] = useState('')

  function load() {
    return bookingsApi
      .list()
      .then((result) => setBookings(result.bookings))
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Unable to load bookings'),
      )
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    void load()
  }, [])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      await bookingsApi.create({
        provider,
        fare: Number(fare) || 0,
        scheduled_at: scheduledAt || null,
        details: { created_from: 'frontend' },
      })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create the booking')
    } finally {
      setBusy(false)
    }
  }

  async function handleCancel(id: number) {
    setError('')
    try {
      const result = await bookingsApi.cancel(id)
      setBookings((current) =>
        current.map((item) => (item.id === id ? result.booking : item)),
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to cancel the booking')
    }
  }

  if (loading) {
    return (
      <div className="page">
        <LoadingSpinner label="Loading bookings…" />
      </div>
    )
  }

  return (
    <div className="page">
      <header className="page__head">
        <h1>Bookings</h1>
        <p>Reserve a cab, metro card or bus pass for the legs of your trip.</p>
      </header>

      {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}

      <section className="card">
        <h2>New booking</h2>
        <form className="form" onSubmit={handleSubmit}>
          <div className="grid grid--3">
            <label className="field">
              <span>Provider</span>
              <select
                value={provider}
                onChange={(event) => setProvider(event.target.value)}
              >
                {PROVIDERS.map((item) => (
                  <option key={item} value={item}>
                    {item.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Fare (₹)</span>
              <input
                type="number"
                min={0}
                value={fare}
                onChange={(event) => setFare(event.target.value)}
              />
            </label>
            <label className="field">
              <span>Scheduled at (optional)</span>
              <input
                type="datetime-local"
                value={scheduledAt}
                onChange={(event) => setScheduledAt(event.target.value)}
              />
            </label>
          </div>
          <button type="submit" className="btn btn--primary" disabled={busy}>
            {busy ? 'Creating…' : 'Create booking'}
          </button>
        </form>
      </section>

      <section className="section">
        <h2 className="section__title">Your bookings</h2>
        {bookings.length ? (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th scope="col">Provider</th>
                  <th scope="col">Status</th>
                  <th scope="col">Fare</th>
                  <th scope="col">Scheduled</th>
                  <th scope="col">Created</th>
                  <th scope="col" />
                </tr>
              </thead>
              <tbody>
                {bookings.map((booking) => (
                  <tr key={booking.id}>
                    <th scope="row">{booking.provider.replace('_', ' ')}</th>
                    <td>
                      <span className={`tag tag--${booking.status}`}>
                        {booking.status}
                      </span>
                    </td>
                    <td>{formatCurrency(booking.fare)}</td>
                    <td>{formatDateTime(booking.scheduled_at)}</td>
                    <td>{formatDateTime(booking.created_at)}</td>
                    <td>
                      {booking.status !== 'cancelled' ? (
                        <button
                          type="button"
                          className="btn btn--link btn--danger"
                          onClick={() => handleCancel(booking.id)}
                        >
                          Cancel
                        </button>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No bookings" hint="Create a booking to see it here." />
        )}
      </section>
    </div>
  )
}

