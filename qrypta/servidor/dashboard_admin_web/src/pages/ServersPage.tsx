import { useMemo, useState } from 'react'
import { serverNodes } from '../store/adminStore'

type ServerStatus = 'operativo' | 'degradado' | 'caido'

export function ServersPage() {
  const [overrides, setOverrides] = useState<Record<string, ServerStatus>>({})

  const nodes = useMemo(
    () =>
      serverNodes.map((node) => ({
        ...node,
        status: overrides[node.id] ?? node.status,
      })),
    [overrides],
  )

  const restartNode = (id: string) => {
    setOverrides((previous) => ({
      ...previous,
      [id]: 'operativo',
    }))
  }

  return (
    <section className="card-page">
      <div className="card-head">
        <h2>Servidores y nodos</h2>
        <p>Monitoreo por region con acciones operativas de recuperacion.</p>
      </div>

      <ul className="server-grid">
        {nodes.map((node) => (
          <li key={node.id}>
            <h3>{node.name}</h3>
            <p>Region: {node.region}</p>
            <p>Cola: {node.queueSize} mensajes</p>
            <p>
              Estado:{' '}
              <span className={`pill ${node.status === 'operativo' ? 'pill-ok' : 'pill-warn'}`}>
                {node.status}
              </span>
            </p>
            <button type="button" onClick={() => restartNode(node.id)}>
              Reiniciar servicio
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
