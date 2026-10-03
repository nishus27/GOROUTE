/** Application shell: top navigation, notification bell and user menu. */

import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { notificationsApi } from '../services/domain'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/plan', label: 'Plan Journey' },
  { to: '/results', label: 'Route Results' },
  { to: '/daily-commute', label: 'Daily Commute' },
  { to: '/saved-places', label: 'Saved Places' },
  { to: '/history', label: 'History' },
  { to: '/bookings', label: 'Bookings' },
  { to: '/insights', label: 'Insights' },
  { to: '/notifications', label: 'Notifications' },
  { to: '/profile', label: 'Profile' },
]

export function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    let active = true
    notificationsApi
      .list()
      .then((result) => {
        if (active) setUnread(result.unread_count)
      })
      .catch(() => undefined)
    return () => {
      active = false
    }
  }, [])

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app">
      <header className="app__header">
        <Link to="/" className="brand">
          <span className="brand__mark" aria-hidden="true">
            GR
          </span>
          <span className="brand__text">
            <strong>GoRoute</strong>
            <small>Multimodal journey planner</small>
          </span>
        </Link>

        <nav className="app__nav" aria-label="Main">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                isActive ? 'nav-link nav-link--active' : 'nav-link'
              }
            >
              {item.label}
              {item.to === '/notifications' && unread > 0 ? (
                <span className="nav-link__badge">{unread}</span>
              ) : null}
            </NavLink>
          ))}
        </nav>

        <div className="app__user">
          <span className="app__user-name">{user?.name ?? 'Signed in'}</span>
          <button type="button" className="btn btn--ghost" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="app__main">
        <Outlet />
      </main>

      <footer className="app__footer">
        Scores are computed by the GoRoute decision engine using fixed, weighted
        factors.
      </footer>
    </div>
  )
}
