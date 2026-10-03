/** Side-by-side comparison of every candidate route. */

import type { RouteOption } from '../types'
import {
  formatCurrency,
  formatDistance,
  formatDuration,
  formatPercent,
} from '../utils/format'

export function RouteComparison({
  routes,
  recommendedRouteId,
}: {
  routes: RouteOption[]
  recommendedRouteId: string
}) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th scope="col">Route</th>
            <th scope="col">Score</th>
            <th scope="col">Duration</th>
            <th scope="col">Fare</th>
            <th scope="col">Waiting</th>
            <th scope="col">Transfers</th>
            <th scope="col">Walking</th>
            <th scope="col">Reliability</th>
          </tr>
        </thead>
        <tbody>
          {routes.map((route) => (
            <tr
              key={route.id}
              className={
                route.id === recommendedRouteId ? 'table__row--best' : undefined
              }
            >
              <th scope="row">
                {route.mode_summary}
                {route.id === recommendedRouteId ? (
                  <span className="tag tag--best">Best</span>
                ) : null}
              </th>
              <td className="table__score">{route.score.toFixed(1)}</td>
              <td>{formatDuration(route.metrics.total_duration_min)}</td>
              <td>{formatCurrency(route.metrics.total_cost)}</td>
              <td>{route.metrics.waiting_time_min} min</td>
              <td>{route.metrics.transfers}</td>
              <td>{formatDistance(route.metrics.walking_distance_m)}</td>
              <td>{formatPercent(route.metrics.reliability)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
