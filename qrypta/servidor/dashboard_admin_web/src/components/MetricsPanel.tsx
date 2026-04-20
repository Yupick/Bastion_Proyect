import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

type Point = {
  label: string
  requests: number
  errors: number
}

type Props = {
  points: Point[]
}

export function MetricsPanel({ points }: Props) {
  return (
    <section className="chart-panel">
      <div className="card-head">
        <h2>Métricas operativas</h2>
        <p>Tráfico y errores por ventana de tiempo.</p>
      </div>

      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={points}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d4dfeb" />
            <XAxis dataKey="label" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="requests" stroke="#155eef" strokeWidth={2} />
            <Line type="monotone" dataKey="errors" stroke="#c0392b" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
