import { useEffect, useState } from 'react'
import { getMetrics } from '../api/client'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    getMetrics().then(setMetrics)
  }, [])

  if (!metrics) return <div>Loading...</div>

  const chartData = [
    { name: 'Avg Latency', value: metrics.avg_latency_ms },
    { name: 'P95 Latency', value: metrics.p95_latency_ms },
  ]

  return (
    <div style={{ padding: 32 }}>
      <h2>Inference Dashboard</h2>

      {/* Stat cards */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 32 }}>
        <StatCard label="Total Requests" value={metrics.total_requests} />
        <StatCard label="Avg Latency" value={`${metrics.avg_latency_ms} ms`} />
        <StatCard label="P95 Latency" value={`${metrics.p95_latency_ms} ms`} />
        <StatCard label="Error Rate" value={`${metrics.error_rate_pct}%`} color={metrics.error_rate_pct > 5 ? '#ef4444' : '#22c55e'} />
        <StatCard label="Total Tokens" value={metrics.total_tokens} />
      </div>

      {/* Latency bar chart */}
      <h3>Latency (ms)</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function StatCard({ label, value, color = '#1e293b' }: { label: string; value: any; color?: string }) {
  return (
    <div style={{ padding: '16px 24px', background: '#f8fafc', borderRadius: 10, minWidth: 140 }}>
      <div style={{ fontSize: 12, color: '#64748b', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color }}>{value}</div>
    </div>
  )
}
