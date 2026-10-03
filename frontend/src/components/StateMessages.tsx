/** Small shared state components: loading, error and empty messages. */

export function LoadingSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="state state--loading" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export function ErrorBanner({
  message,
  onDismiss,
}: {
  message: string
  onDismiss?: () => void
}) {
  return (
    <div className="banner banner--error" role="alert">
      <span>{message}</span>
      {onDismiss ? (
        <button type="button" className="banner__close" onClick={onDismiss}>
          Dismiss
        </button>
      ) : null}
    </div>
  )
}

export function EmptyState({
  title,
  hint,
}: {
  title: string
  hint?: string
}) {
  return (
    <div className="state state--empty">
      <strong>{title}</strong>
      {hint ? <span>{hint}</span> : null}
    </div>
  )
}
