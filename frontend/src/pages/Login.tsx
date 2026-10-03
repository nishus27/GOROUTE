/** Login page. */

import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ErrorBanner } from '../components/StateMessages'

export function Login() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) {
    return <div className="auth-page">Checking your session…</div>
  }

  if (user) {
    const target = (location.state as { from?: string } | null)?.from ?? '/'
    return <Navigate to={target} replace />
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(email.trim(), password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in')
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
            <h1>Welcome back to GoRoute</h1>
            <p>Sign in to plan and compare multimodal journeys.</p>
          </div>
        </div>

        {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}

        <form onSubmit={handleSubmit} className="form">
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
              autoComplete="current-password"
              required
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </label>

          <button type="submit" className="btn btn--primary" disabled={submitting}>
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="auth-card__foot">
          New to GoRoute? <Link to="/signup">Create an account</Link>
        </p>
      </div>
    </div>
  )
}
