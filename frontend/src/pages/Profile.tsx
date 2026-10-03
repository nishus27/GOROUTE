/** Profile — account summary and session controls. */

import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { formatDateTime } from '../utils/format'

export function Profile() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="page">
      <header className="page__head">
        <h1>Profile</h1>
        <p>Your GoRoute account.</p>
      </header>

      <section className="card">
        <dl className="metrics">
          <div>
            <dt>Name</dt>
            <dd>{user?.name ?? '—'}</dd>
          </div>
          <div>
            <dt>Email</dt>
            <dd>{user?.email ?? '—'}</dd>
          </div>
          <div>
            <dt>Member since</dt>
            <dd>{formatDateTime(user?.created_at)}</dd>
          </div>
          <div>
            <dt>Account ID</dt>
            <dd>{user?.id ?? '—'}</dd>
          </div>
        </dl>

        <div className="reroute__actions">
          <button type="button" className="btn btn--primary" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </section>
    </div>
  )
}
