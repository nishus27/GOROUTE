/** Saved Places — CRUD over the user's favourite locations. */

import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { savedPlacesApi } from '../services/domain'
import { EmptyState, ErrorBanner, LoadingSpinner } from '../components/StateMessages'
import type { SavedPlace } from '../types'

const BLANK = { label: '', address: '' }

export function SavedPlaces() {
  const [places, setPlaces] = useState<SavedPlace[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState(BLANK)
  const [editingId, setEditingId] = useState<number | null>(null)

  function load() {
    return savedPlacesApi
      .list()
      .then((result) => setPlaces(result.saved_places))
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Unable to load saved places'),
      )
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    void load()
  }, [])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setSaving(true)
    const payload = {
      label: form.label.trim(),
      address: form.address.trim(),
      latitude: null,
      longitude: null,
    }
    try {
      if (editingId) {
        await savedPlacesApi.update(editingId, payload)
      } else {
        await savedPlacesApi.create(payload)
      }
      setForm(BLANK)
      setEditingId(null)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save the place')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id: number) {
    setError('')
    try {
      await savedPlacesApi.remove(id)
      setPlaces((current) => current.filter((place) => place.id !== id))
      if (editingId === id) {
        setEditingId(null)
        setForm(BLANK)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to delete the place')
    }
  }

  function startEdit(place: SavedPlace) {
    setEditingId(place.id)
    setForm({ label: place.label, address: place.address })
  }

  if (loading) {
    return (
      <div className="page">
        <LoadingSpinner label="Loading saved places…" />
      </div>
    )
  }

  return (
    <div className="page">
      <header className="page__head">
        <h1>Saved places</h1>
        <p>Keep the locations you travel to most, ready for one-tap planning.</p>
      </header>

      {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}

      <div className="grid grid--2">
        <section className="card">
          <h2>{editingId ? 'Edit place' : 'Add a place'}</h2>
          <form className="form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Label</span>
              <input
                value={form.label}
                required
                placeholder="Home"
                onChange={(event) =>
                  setForm((current) => ({ ...current, label: event.target.value }))
                }
              />
            </label>
            <label className="field">
              <span>Address</span>
              <input
                value={form.address}
                required
                placeholder="Thane West"
                onChange={(event) =>
                  setForm((current) => ({ ...current, address: event.target.value }))
                }
              />
            </label>
            <div className="reroute__actions">
              <button type="submit" className="btn btn--primary" disabled={saving}>
                {saving ? 'Saving…' : editingId ? 'Save changes' : 'Add place'}
              </button>
              {editingId ? (
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => {
                    setEditingId(null)
                    setForm(BLANK)
                  }}
                >
                  Cancel
                </button>
              ) : null}
            </div>
          </form>
        </section>

        <section className="card">
          <h2>Your places</h2>
          {places.length ? (
            <ul className="list">
              {places.map((place) => (
                <li key={place.id}>
                  <div>
                    <strong>{place.label}</strong>
                    <span className="list__meta">{place.address}</span>
                  </div>
                  <span className="list__actions">
                    <Link
                      className="btn btn--link"
                      to={`/results?${new URLSearchParams({
                        source: place.address,
                        destination: 'Andheri',
                        preference: 'balanced',
                      }).toString()}`}
                    >
                      Plan from here
                    </Link>
                    <button
                      type="button"
                      className="btn btn--link"
                      onClick={() => startEdit(place)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="btn btn--link btn--danger"
                      onClick={() => handleDelete(place.id)}
                    >
                      Delete
                    </button>
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title="No saved places"
              hint="Add your home, work or college to plan faster."
            />
          )}
        </section>
      </div>
    </div>
  )
}
