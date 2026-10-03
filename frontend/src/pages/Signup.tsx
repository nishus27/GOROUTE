/** Signup page. */

import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ErrorBanner } from '../components/StateMessages'

export function Signup() {
  const { user, loading, signup } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) {
    return <div className="auth-page">Checking your session…</div>
  }

  if (user) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await signup(name.trim(), email.trim(), password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create account')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-card__brand">
          <span className="brand__mark" aria-hidden="true">
            GR
          </span>
          <div>
            <h1>Create your GoRoute account</h1>
            <p>Compare every mode and get the best route for your trip.</p>
          </div>
        </div>

        {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}

        <form onSubmit={handleSubmit} className="form">
          <label className="field">
            <span>Name</span>
            <input
              type="text"
              value={name}
              autoComplete="name"
              required
              onChange={(event) => setName(event.target.value)}
              placeholder="Asha"
            />
          </label>

          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              autoComplete="email"
              required
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
            />
          </label>

          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={password}
              autoComplete="new-password"
              required
              minLength={6}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 6 characters"
            />
          </label>

          <button type="submit" className="btn btn--primary" disabled={submitting}>
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="auth-card__foot">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
