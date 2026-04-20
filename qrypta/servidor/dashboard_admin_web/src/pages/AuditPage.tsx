import type { AuditEvent, EventLevel } from '../types/admin'
import { exportAuditAsJson } from '../services/exportService'

type Props = {
  filter: 'TODOS' | EventLevel
  onFilterChange: (filter: 'TODOS' | EventLevel) => void
  events: AuditEvent[]
}

export function AuditPage({ filter, onFilterChange, events }: Props) {
  return (
    <section className="card-page">
      <div className="card-head card-head-inline">
        <div>
          <h2>Auditoria</h2>
          <p>Eventos firmados por nivel y fuente operativa.</p>
        </div>
        <button type="button" onClick={() => exportAuditAsJson(events)}>
          Exportar JSON
        </button>
      </div>

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

      <ul className="audit-list">
        {events.map((event) => (
          <li key={event.id}>
            <p>{event.detail}</p>
            <div>
              <span>{event.level}</span>
              <span>{event.source}</span>
              <time>{event.time}</time>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
