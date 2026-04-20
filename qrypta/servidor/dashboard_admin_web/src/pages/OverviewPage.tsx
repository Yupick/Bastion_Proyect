import { AlertCenter } from '../components/AlertCenter'
import { MetricsPanel } from '../components/MetricsPanel'
import type { AuditEvent, EventLevel } from '../types/admin'

type Props = {
  filter: 'TODOS' | EventLevel
  onFilterChange: (filter: 'TODOS' | EventLevel) => void
  events: AuditEvent[]
  kpi: {
    uptime: string
    activePeers: number
    queueMessages: number
    activeAdmins: number
    criticalEvents: number
  }
  trafficPoints: Array<{ label: string; requests: number; errors: number }>
  realtimeState: 'connecting' | 'connected' | 'fallback'
  alerts: Array<{ id: string; level: 'INFO' | 'WARN' | 'CRITICAL'; text: string }>
}

export function OverviewPage({
  filter,
  onFilterChange,
  events,
  kpi,
  trafficPoints,
  realtimeState,
  alerts,
}: Props) {
  return (
    <>
      <header className="top-kpi">
        <article>
          <small>Estado</small>
          <strong>Operativo</strong>
          <span>Uptime {kpi.uptime}</span>
        </article>
        <article>
          <small>Peers activos</small>
          <strong>{kpi.activePeers}</strong>
          <span>Conectividad estable</span>
        </article>
        <article>
          <small>Mensajes en cola</small>
          <strong>{kpi.queueMessages}</strong>
          <span>Cola distribuida actual</span>
        </article>
        <article>
          <small>Admins activos</small>
          <strong>{kpi.activeAdmins}</strong>
          <span>Sesiones administrativas vigentes</span>
        </article>
      </header>

      <section className="audit-box">
        <div className="audit-head">
          <h2>Auditoria Reciente</h2>
          <div className="filters">
            {(['TODOS', 'INFO', 'EXITO', 'ADVERTENCIA', 'ERROR'] as const).map((kind) => (
              <button
                key={kind}
                type="button"
                className={filter === kind ? 'active' : ''}
                onClick={() => onFilterChange(kind)}
              >
                {kind}
              </button>
            ))}
          </div>
        </div>

        <ul>
          {events.map((event) => (
            <li key={event.id} className={`evento evento-${event.level.toLowerCase()}`}>
              <p>{event.detail}</p>
              <span>{event.level}</span>
              <time>{event.time}</time>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel-strip">
        <article>
          <h3>Riesgo activo</h3>
          <p>{kpi.criticalEvents} alertas criticas en la ventana actual.</p>
        </article>
        <article>
          <h3>Operacion sugerida</h3>
          <p>Forzar revalidacion de claves en nodos degradados.</p>
        </article>
      </section>

      <section className="panel-strip">
        <article>
          <h3>Canal realtime</h3>
          <p>
            {realtimeState === 'connected'
              ? 'WebSocket operativo'
              : realtimeState === 'connecting'
                ? 'Conectando al stream...'
                : 'Fallback por sondeo local'}
          </p>
        </article>
      </section>

      <MetricsPanel points={trafficPoints} />
      <AlertCenter alerts={alerts} />
    </>
  )
}
