/** Notifications — route and booking updates with read controls. */

import { useEffect, useState } from 'react'
import { notificationsApi } from '../services/domain'
import { EmptyState, ErrorBanner, LoadingSpinner } from '../components/StateMessages'
import { formatDateTime } from '../utils/format'
import type { AppNotification } from '../types'

export function Notifications() {
  const [items, setItems] = useState<AppNotification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    notificationsApi
      .list()
      .then((result) => {
        if (active) setItems(result.notifications)
      })
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Unable to load notifications'),
      )
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  async function markRead(id: number) {
    try {
      const result = await notificationsApi.markRead(id)
      setItems((current) =>
        current.map((item) => (item.id === id ? result.notification : item)),
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update the notification')
    }
  }

  async function markAllRead() {
    try {
      await notificationsApi.markAllRead()
      setItems((current) => current.map((item) => ({ ...item, is_read: true })))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update notifications')
    }
  }

  if (loading) {
    return (
      <div className="page">
        <LoadingSpinner label="Loading notifications…" />
      </div>
    )
  }

  const unread = items.filter((item) => !item.is_read).length

  return (
    <div className="page">
      <header className="page__head">
        <h1>Notifications</h1>
        <p>
          {unread
            ? `${unread} unread update${unread === 1 ? '' : 's'}`
            : 'You are all caught up.'}
        </p>
      </header>

      {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}

      {items.length ? (
        <>
          {unread ? (
            <div className="reroute__actions">
              <button type="button" className="btn btn--ghost" onClick={markAllRead}>
                Mark all as read
              </button>
            </div>
          ) : null}
          <ul className="list list--notifications">
            {items.map((item) => (
              <li
                key={item.id}
                className={item.is_read ? undefined : 'list__item--unread'}
              >
                <div>
                  <strong>
                    {item.title}
                    {!item.is_read ? <span className="tag tag--new">New</span> : null}
                  </strong>
                  <span className="list__meta">{item.message}</span>
                  <span className="list__meta">{formatDateTime(item.created_at)}</span>
                </div>
                {!item.is_read ? (
                  <button
                    type="button"
                    className="btn btn--link"
                    onClick={() => markRead(item.id)}
                  >
                    Mark read
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        </>
      ) : (
        <EmptyState
          title="No notifications"
          hint="Route changes and booking updates will appear here."
        />
      )}
    </div>
  )
}
