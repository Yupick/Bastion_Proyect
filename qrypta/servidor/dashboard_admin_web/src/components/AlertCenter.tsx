type Alert = {
  id: string
  level: 'INFO' | 'WARN' | 'CRITICAL'
  text: string
}

type Props = {
  alerts: Alert[]
}

export function AlertCenter({ alerts }: Props) {
  return (
    <section className="alerts-panel">
      <div className="card-head">
        <h2>Alertas</h2>
        <p>Eventos operativos en tiempo casi real.</p>
      </div>

      {alerts.length === 0 ? <p className="muted">Sin alertas activas.</p> : null}

      <ul>
        {alerts.map((alert) => (
          <li key={alert.id} className={`alert-item alert-${alert.level.toLowerCase()}`}>
            <strong>{alert.level}</strong>
            <p>{alert.text}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}
