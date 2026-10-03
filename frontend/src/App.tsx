/** Route table: public auth pages and the protected application shell. */

import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import type { ReactElement } from 'react'
import { useAuth } from './hooks/useAuth'
import { AppShell } from './components/AppShell'
import { LoadingSpinner } from './components/StateMessages'
import { Login } from './pages/Login'
import { Signup } from './pages/Signup'
import { Dashboard } from './pages/Dashboard'
import { PlanJourney } from './pages/PlanJourney'
import { RouteResults } from './pages/RouteResults'
import { DailyCommute } from './pages/DailyCommute'
import { SavedPlaces } from './pages/SavedPlaces'
import { History } from './pages/History'
import { Bookings } from './pages/Bookings'
import { Insights } from './pages/Insights'
import { Notifications } from './pages/Notifications'
import { Profile } from './pages/Profile'
import { NotFound } from './pages/NotFound'

function RequireAuth({ children }: { children: ReactElement }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <LoadingSpinner label="Checking your session…" />
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return children
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/plan" element={<PlanJourney />} />
        <Route path="/results" element={<RouteResults />} />
        <Route path="/daily-commute" element={<DailyCommute />} />
        <Route path="/saved-places" element={<SavedPlaces />} />
        <Route path="/history" element={<History />} />
        <Route path="/bookings" element={<Bookings />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
