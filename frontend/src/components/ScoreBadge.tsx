/** 0–100 score badge with a colour tone derived from the score. */

import { scoreTone } from '../utils/format'

export function ScoreBadge({
  score,
  label = 'Score',
  size = 'md',
}: {
  score: number
  label?: string
  size?: 'sm' | 'md' | 'lg'
}) {
  return (
    <div className={`score score--${scoreTone(score)} score--${size}`}>
      <span className="score__value">{score.toFixed(1)}</span>
      <span className="score__label">{label}</span>
    </div>
  )
}

export function ModeIcon({ modes }: { modes: string[] }) {
  const icons: Record<string, string> = {
    train: '🚆',
    metro: '🚇',
    bus: '🚌',
    cab: '🚕',
    auto: '🛺',
    walking: '🚶',
  }
  const shown = modes.length ? modes : ['bus']
  return (
    <span className="mode-icons" aria-hidden="true">
      {shown.map((mode, index) => (
        <span key={`${mode}-${index}`}>{icons[mode] ?? '🧭'}</span>
      ))}
    </span>
  )
}
