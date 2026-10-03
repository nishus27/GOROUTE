/** Not found page for unknown routes inside the app shell. */

import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="page">
      <div className="state state--empty">
        <strong>Page not found</strong>
        <span>That route does not exist in GoRoute.</span>
        <Link className="btn btn--primary" to="/">
          Back to dashboard
        </Link>
      </div>
    </div>
  )
}
