/** Journey Planner — collects the request and starts a route search. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { savedPlacesApi } from '../services/domain'
import { ErrorBanner } from '../components/StateMessages'
import { PREFERENCE_HINTS, PREFERENCE_LABELS } from '../utils/format'
import type { Preference, SavedPlace } from '../types'

const MODES = ['train', 'metro', 'bus', 'cab', 'auto', 'walking']

export function PlanJourney() {
  const navigate = useNavigate()
  const [source, setSource] = useState('Thane')
  const [destination, setDestination] = useState('Andheri')
  const [preference, setPreference] = useState<Preference>('balanced')
  const [departureTime, setDepartureTime] = useState('')
  const [modes, setModes] = useState<string[]>([])
  const [places, setPlaces] = useState<SavedPlace[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    savedPlacesApi
      .list()
      .then((result) => setPlaces(result.saved_places))
      .catch(() => setPlaces([]))
  }, [])

  function toggleMode(mode: string) {
    setModes((current) =>
      current.includes(mode)
        ? current.filter((item) => item !== mode)
        : [...current, mode],
    )
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!source.trim() || !destination.trim()) {
      setError('Enter both a starting point and a destination.')
      return
    }
    const params = new URLSearchParams({
      source: source.trim(),
      destination: destination.trim(),
      preference,
    })
    if (departureTime) params.set('departure_time', departureTime)
    if (modes.length) params.set('modes', modes.join(','))
    navigate(`/results?${params.toString()}`)
  }

  return (
    <div className="page">
      <header className="page__head">
        <h1>Plan a journey</h1>
        <p>
          Enter your trip, choose what matters most, and GoRoute will compare
          every multimodal option.
        </p>
      </header>

      {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}

      <form className="card form" onSubmit={handleSubmit}>
        <div className="grid grid--2">
          <label className="field">
            <span>From</span>
            <input
              list="saved-place-options"
              value={source}
              required
              onChange={(event) => setSource(event.target.value)}
              placeholder="e.g. Thane"
            />
          </label>

          <label className="field">
            <span>To</span>
            <input
              list="saved-place-options"
              value={destination}
              required
              onChange={(event) => setDestination(event.target.value)}
              placeholder="e.g. Andheri"
            />
          </label>
        </div>

        <datalist id="saved-place-options">
          {places.map((place) => (
            <option key={place.id} value={place.address}>
              {place.label}
            </option>
          ))}
        </datalist>

        <fieldset className="fieldset">
          <legend>Preference</legend>
          <div className="chip-row">
            {(Object.keys(PREFERENCE_LABELS) as Preference[]).map((key) => (
              <button
                key={key}
                type="button"
                className={
                  preference === key ? 'chip chip--active' : 'chip'
                }
                onClick={() => setPreference(key)}
              >
                {PREFERENCE_LABELS[key]}
              </button>
            ))}
          </div>
          <p className="hint">{PREFERENCE_HINTS[preference]}</p>
        </fieldset>

        <div className="grid grid--2">
          <label className="field">
            <span>Departure time (optional)</span>
            <input
              type="datetime-local"
              value={departureTime}
              onChange={(event) => setDepartureTime(event.target.value)}
            />
          </label>

          <fieldset className="fieldset">
            <legend>Modes (optional)</legend>
            <div className="chip-row">
              {MODES.map((mode) => (
                <button
                  key={mode}
                  type="button"
                  className={modes.includes(mode) ? 'chip chip--active' : 'chip'}
                  onClick={() => toggleMode(mode)}
                >
                  {mode}
                </button>
              ))}
            </div>
            <p className="hint">Leave empty to consider every mode.</p>
          </fieldset>
        </div>

        <button type="submit" className="btn btn--primary btn--wide">
          Find Best Route
        </button>
      </form>
    </div>
  )
}
