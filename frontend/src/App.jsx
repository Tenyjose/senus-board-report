import { useState, useEffect } from 'react'

function App() {
  const [periods, setPeriods] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [selectedPeriodId, setSelectedPeriodId] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [metricsLoading, setMetricsLoading] = useState(false)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/periods/')
      .then((response) => response.json())
      .then((data) => {
        setPeriods(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    if (selectedPeriodId === null) return

    setMetricsLoading(true)
    setMetrics(null)

    fetch(`http://127.0.0.1:8000/periods/${selectedPeriodId}/metrics`)
      .then((response) => response.json())
      .then((data) => {
        setMetrics(data)
        setMetricsLoading(false)
      })
  }, [selectedPeriodId])

  const display = (value, suffix = '') => {
    if (value === null || value === undefined) return 'N/A'
    return `${value}${suffix}`
  }

  if (loading) return <p>Loading periods...</p>
  if (error) return <p>Error: {error}</p>

  return (
    <div>
      <h1>Senus PLC — Board Report</h1>

      <ul>
        {periods.map((period) => (
          <li key={period.id}>
            <button onClick={() => setSelectedPeriodId(period.id)}>
              {period.label} ({period.start_date} to {period.end_date})
            </button>
          </li>
        ))}
      </ul>

      {metricsLoading && <p>Loading metrics...</p>}

      {metrics && (
        <div>
          <h2>{metrics.period.label}</h2>
          <p>Revenue: {display(metrics.growth_and_revenue.revenue)}</p>
          <p>Revenue Growth: {display(metrics.growth_and_revenue.revenue_growth_pct, '%')}</p>
          <p>Gross Margin: {display(metrics.profitability.gross_margin_pct, '%')}</p>
          <p>Operating Margin: {display(metrics.profitability.operating_margin_pct, '%')}</p>
          <p>EBITDA: {display(metrics.profitability.ebitda)}</p>
          <p>Working Capital: {display(metrics.cash_and_liquidity.working_capital)}</p>
          <p>Cash Runway: {display(metrics.cash_and_liquidity.cash_runway_months, ' months')}</p>
          <p>DSCR: {display(metrics.solvency_and_leverage.dscr)}</p>
          <p>ROCE: {display(metrics.returns.roce_pct, '%')}</p>
        </div>
      )}
    </div>
  )
}

export default App