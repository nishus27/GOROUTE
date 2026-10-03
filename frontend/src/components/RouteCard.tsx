/** Route card: one scored candidate route with metrics and factor breakdown. */

import type { RouteOption } from '../types'
import { ScoreBadge, ModeIcon } from './ScoreBadge'
import {
  FACTOR_LABELS,
  formatCurrency,
  formatDistance,
  formatDuration,
  formatPercent,
} from '../utils/format'

function FactorBars({ route }: { route: RouteOption }) {
  const normalized = route.normalized
  if (!normalized) return null
  return (
    <div className="factors">
      {Object.entries(normalized).map(([factor, value]) => (
        <div className="factor" key={factor}>
          <span className="factor__label">{FACTOR_LABELS[factor] ?? factor}</span>
          <span className="factor__track">
            <span
              className="factor__fill"
              style={{ width: `${Math.max(2, Math.round(value * 100))}%` }}
            />
          </span>
          <span className="factor__value">{formatPercent(value)}</span>
        </div>
      ))}
    </div>
  )
}

export function RouteCard({
  route,
  isRecommended,
  isAffected,
  expanded,
  onToggle,
}: {
  route: RouteOption
  isRecommended: boolean
  isAffected?: boolean
  expanded?: boolean
  onToggle?: () => void
}) {
  const metrics = route.metrics
  return (
    <article
      className={[
        'card',
        'route-card',
        isRecommended ? 'route-card--recommended' : '',
        isAffected ? 'route-card--affected' : '',
      ]
        .filter(Boolean)
        .join(' ')}
    >
      <header className="route-card__head">
        <div className="route-card__title">
          <ModeIcon modes={route.modes} />
          <div>
            <h3>{route.mode_summary}</h3>
            <p className="route-card__tags">
              {isRecommended ? (
                <span className="tag tag--best">Recommended</span>
              ) : null}
              {typeof route.rank === 'number' ? (
                <span className="tag">Rank #{route.rank}</span>
              ) : null}
              {isAffected ? (
                <span className="tag tag--warn">Affected by incident</span>
              ) : null}
            </p>
          </div>
        </div>
        <ScoreBadge score={route.score} label="Score / 100" />
      </header>

      <dl className="metrics">
        <div>
          <dt>Duration</dt>
          <dd>{formatDuration(metrics.total_duration_min)}</dd>
        </div>
        <div>
          <dt>Fare</dt>
          <dd>{formatCurrency(metrics.total_cost)}</dd>
        </div>
        <div>
          <dt>Waiting</dt>
          <dd>{metrics.waiting_time_min} min</dd>
        </div>
        <div>
          <dt>Transfers</dt>
          <dd>{metrics.transfers}</dd>
        </div>
        <div>
          <dt>Walking</dt>
          <dd>{formatDistance(metrics.walking_distance_m)}</dd>
        </div>
        <div>
          <dt>Reliability</dt>
          <dd>{formatPercent(metrics.reliability)}</dd>
        </div>
      </dl>

      <div className="route-card__actions">
        {onToggle ? (
          <button type="button" className="btn btn--link" onClick={onToggle}>
            {expanded ? 'Hide details' : 'View legs & factors'}
          </button>
        ) : null}
      </div>

      {expanded ? (
        <div className="route-card__details">
          <h4>Journey legs</h4>
          <ol className="legs">
            {route.legs.map((leg, index) => (
              <li key={`${leg.mode}-${index}`}>
                <span className="legs__mode">{leg.mode_label}</span>
                <span className="legs__route">
                  {leg.instruction ?? `${leg.from} → ${leg.to}`}
                </span>
                <span className="legs__meta">
                  {formatDuration(leg.duration_min)} · {leg.distance_km} km ·{' '}
                  {formatCurrency(leg.cost)}
                </span>
              </li>
            ))}
          </ol>

          <h4>Factor scores</h4>
          <p className="hint">
            Each factor is normalised 0–100% across the compared routes, then
            weighted by your preference.
          </p>
          <FactorBars route={route} />
        </div>
      ) : null}
    </article>
  )
}
