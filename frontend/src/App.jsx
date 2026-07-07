import { useState, useEffect } from 'react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import './index.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL
const COLORS = { brass: '#B8935A', rust: '#A8503C', sage: '#6E8B74' }

function App() {
  const [periods, setPeriods] = useState([])
  const [selectedPeriodId, setSelectedPeriodId] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [insights, setInsights] = useState(null)
  const [chartData, setChartData] = useState([])

  useEffect(() => {
    fetch(`${API_BASE}/periods/`)
      .then((r) => r.json())
      .then((data) => {
        setPeriods(data)
        if (data.length > 0) setSelectedPeriodId(data[0].id)
      })
  }, [])

  useEffect(() => {
    if (selectedPeriodId === null) return
    setMetrics(null)
    setInsights(null)

    fetch(`${API_BASE}/periods/${selectedPeriodId}/metrics`)
      .then((r) => r.json())
      .then(setMetrics)

    fetch(`${API_BASE}/periods/${selectedPeriodId}/insights`)
      .then((r) => r.json())
      .then((data) => setInsights(data.commentary))
  }, [selectedPeriodId])

  useEffect(() => {
    if (periods.length === 0) return
    Promise.all(
      periods.map((p) =>
        fetch(`${API_BASE}/periods/${p.id}/metrics`).then((r) => r.json())
      )
    ).then((all) => {
      const withRevenue = all
        .filter((m) => m.growth_and_revenue.revenue !== null)
        .sort((a, b) => new Date(a.period.start_date) - new Date(b.period.start_date))
      setChartData(withRevenue)
    })
  }, [periods])

  const formatCurrency = (v) => {
    if (v === null || v === undefined) return { text: 'N/A', cls: 'value-na' }
    const text = `€${Number(v).toLocaleString('en-IE', { maximumFractionDigits: 0 })}`
    return { text, cls: v >= 0 ? 'value-positive' : 'value-negative' }
  }

  const formatPct = (v) => {
    if (v === null || v === undefined) return { text: 'N/A', cls: 'value-na' }
    return { text: `${v}%`, cls: v >= 0 ? 'value-positive' : 'value-negative' }
  }

  const formatAxisValue = (value) => {
    if (value >= 1000000) return `€${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `€${(value / 1000).toFixed(0)}k`
    return `€${value}`
  }

  const formatCount = (v) => {
    if (v === null || v === undefined) return { text: 'N/A', cls: 'value-na' }
    return { text: v, cls: 'value-positive' }
  }

  const Row = ({ label, value }) => (
    <tr>
      <td>{label}</td>
      <td className={value.cls}>{value.text}</td>
    </tr>
  )

  const hasGrowthData = metrics && metrics.growth_metrics && (
    metrics.growth_metrics.total_customer_accounts !== null ||
    metrics.growth_metrics.new_deals_closed_value !== null ||
    metrics.growth_metrics.open_pipeline_value !== null ||
    metrics.growth_metrics.notable_commercial_events.length > 0
  )

  const isSnapshot = metrics && metrics.period.period_type === 'snapshot'

  return (
    <div className="report">
      <div className="report-header">
        <h1>Senus PLC</h1>
        <p className="report-subtitle">
          Board Report{metrics ? ` — ${metrics.period.label}` : ''}
        </p>
        <p className="report-caption">
          Natural Capital Management Software · Euronext Access Dublin
        </p>
      </div>

      <div className="period-nav">
        {periods.map((p) => (
          <button
            key={p.id}
            className={`period-pill ${p.id === selectedPeriodId ? 'active' : ''}`}
            onClick={() => setSelectedPeriodId(p.id)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {!metrics && <p className="loading-text">Loading...</p>}

      {metrics && isSnapshot && metrics.balance_sheet_detail && (
        <div className="panel">
          <h2>{metrics.period.label} — Financial Position</h2>
          <p className="report-caption" style={{ marginBottom: '20px' }}>
            One-off balance sheet prepared ahead of the Euronext Access Dublin
            direct listing on 22 December 2025. No income statement or cash
            flow statement was disclosed for this snapshot.
          </p>
          <table className="ledger">
            <tbody>
              <Row label="Fixed Assets" value={formatCurrency(metrics.balance_sheet_detail.fixed_assets)} />
              <Row label="Current Assets" value={formatCurrency(metrics.balance_sheet_detail.current_assets)} />
              <Row label="Creditors (within one year)" value={formatCurrency(metrics.balance_sheet_detail.creditors_due_within_one_year)} />
              <Row label="Net Current Assets (Working Capital)" value={formatCurrency(metrics.balance_sheet_detail.net_current_assets)} />
              <Row label="Creditors (after one year)" value={formatCurrency(metrics.balance_sheet_detail.creditors_due_after_one_year)} />
              <Row label="Net Assets" value={formatCurrency(metrics.balance_sheet_detail.net_assets)} />
              <Row label="Share Capital" value={formatCurrency(metrics.balance_sheet_detail.share_capital)} />
              <Row label="Share Premium" value={formatCurrency(metrics.balance_sheet_detail.share_premium)} />
              <Row label="Retained Earnings" value={formatCurrency(metrics.balance_sheet_detail.retained_earnings)} />
              <Row label="Total Equity" value={formatCurrency(metrics.balance_sheet_detail.total_equity)} />
            </tbody>
          </table>
        </div>
      )}

      {metrics && !isSnapshot && (
        <div className="panel">
          <h2>{metrics.period.label}</h2>
          <table className="ledger">
            <tbody>
              <Row label="Revenue" value={formatCurrency(metrics.growth_and_revenue.revenue)} />
              <Row label="Revenue Growth" value={formatPct(metrics.growth_and_revenue.revenue_growth_pct)} />
              <Row label="Gross Margin" value={formatPct(metrics.profitability.gross_margin_pct)} />
              <Row label="Operating Margin" value={formatPct(metrics.profitability.operating_margin_pct)} />
              <Row label="EBITDA" value={formatCurrency(metrics.profitability.ebitda)} />
              <Row label="Working Capital" value={formatCurrency(metrics.cash_and_liquidity.working_capital)} />
              <Row label="Cash Runway" value={
                metrics.cash_and_liquidity.cash_runway_months === null
                  ? { text: 'N/A', cls: 'value-na' }
                  : { text: `${metrics.cash_and_liquidity.cash_runway_months} months`, cls: 'value-positive' }
              } />
              <Row label="DSCR" value={formatCurrency(metrics.solvency_and_leverage.dscr)} />
              <Row label="ROCE" value={formatPct(metrics.returns.roce_pct)} />
            </tbody>
          </table>
        </div>
      )}

      {hasGrowthData && (
        <div className="panel">
          <h2>Growth & Commercial Activity</h2>
          <table className="ledger">
            <tbody>
              <Row label="Total Customer Accounts" value={formatCount(metrics.growth_metrics.total_customer_accounts)} />
              <Row label="New Deals Closed" value={formatCurrency(metrics.growth_metrics.new_deals_closed_value)} />
              <Row label="Open Pipeline" value={formatCurrency(metrics.growth_metrics.open_pipeline_value)} />
            </tbody>
          </table>

          {metrics.growth_metrics.notable_commercial_events.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <p style={{ color: 'var(--parchment-dim)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '10px' }}>
                Notable Commercial Events
              </p>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                {metrics.growth_metrics.notable_commercial_events.map((event, i) => (
                  <li key={i} style={{ marginBottom: '6px', fontSize: '14px' }}>{event}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {insights && (
        <div className="panel">
          <h2>AI Summary</h2>
          <p className="commentary">{insights}</p>
        </div>
      )}

      {chartData.length > 0 && (
        <div className="panel chart-panel">
          <h2>Revenue Trend</h2>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData.map((m) => ({
              label: m.period.label,
              revenue_full_year: m.period.period_type === 'full_year' ? m.growth_and_revenue.revenue : null,
              revenue_half_year: m.period.period_type === 'half_year' ? m.growth_and_revenue.revenue : null,
            }))}>
              <CartesianGrid stroke="#2A4136" strokeDasharray="3 3" />
              <XAxis dataKey="label" stroke="#A9AFA6" />
              <YAxis stroke="#A9AFA6" tickFormatter={formatAxisValue} />
              <Tooltip contentStyle={{ background: '#17291F', border: '1px solid #2A4136', color: '#EDE7D9' }} />
              <Legend />
              <Line type="monotone" dataKey="revenue_full_year" stroke={COLORS.brass} strokeWidth={2} dot={{ fill: COLORS.brass }} name="Full Year Revenue" connectNulls={true} />
              <Line type="monotone" dataKey="revenue_half_year" stroke={COLORS.sage} strokeWidth={2} dot={{ fill: COLORS.sage }} name="Half Year Revenue" connectNulls={true} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {chartData.length > 0 && (
        <div className="panel chart-panel">
          <h2>Margin Comparison</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData.map((m) => ({
              label: m.period.label,
              gross: m.profitability.gross_margin_pct,
              operating: m.profitability.operating_margin_pct,
              ebitda: m.profitability.ebitda_margin_pct,
            }))}>
              <CartesianGrid stroke="#2A4136" strokeDasharray="3 3" />
              <XAxis dataKey="label" stroke="#A9AFA6" />
              <YAxis stroke="#A9AFA6" />
              <Tooltip contentStyle={{ background: '#17291F', border: '1px solid #2A4136', color: '#EDE7D9' }} />
              <Legend />
              <Bar dataKey="gross" fill={COLORS.sage} name="Gross Margin %" />
              <Bar dataKey="operating" fill={COLORS.rust} name="Operating Margin %" />
              <Bar dataKey="ebitda" fill={COLORS.brass} name="EBITDA Margin %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

export default App