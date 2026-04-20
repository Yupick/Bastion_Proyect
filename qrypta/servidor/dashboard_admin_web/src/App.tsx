import { Suspense, lazy, useMemo, useState } from 'react'
import { useAdminDashboard } from './hooks/useAdminDashboard'
import { useAuditTrail } from './hooks/useAuditTrail'
import { Button } from './components/ui/button'
import { useRealtimeStats } from './hooks/useRealtimeStats'
import { useSecurityGate } from './hooks/useSecurityGate'
import './App.css'

const OverviewPage = lazy(() => import('./pages/OverviewPage').then((module) => ({ default: module.OverviewPage })))
const AuditPage = lazy(() => import('./pages/AuditPage').then((module) => ({ default: module.AuditPage })))
const UsersPage = lazy(() => import('./pages/UsersPage').then((module) => ({ default: module.UsersPage })))
const ServersPage = lazy(() => import('./pages/ServersPage').then((module) => ({ default: module.ServersPage })))
const SettingsPage = lazy(() =>
  import('./pages/SettingsPage').then((module) => ({ default: module.SettingsPage })),
)

type Section = 'resumen' | 'auditoria' | 'usuarios' | 'servidores' | 'configuracion'

const NAV_ITEMS: Array<{ id: Section; label: string }> = [
  { id: 'resumen', label: 'Resumen' },
  { id: 'auditoria', label: 'Auditoria' },
  { id: 'usuarios', label: 'Usuarios' },
  { id: 'servidores', label: 'Servidores' },
  { id: 'configuracion', label: 'Configuracion' },
]

function App() {
  const auditTrail = useAuditTrail()
  const [section, setSection] = useState<Section>('resumen')
  const [wsUrl, setWsUrl] = useState('ws://localhost:8000/admin/metrics')
  const { filter, setFilter, filteredEvents, exportableEvents, kpi } = useAdminDashboard()
  const { series, summary } = useRealtimeStats(wsUrl)
  const security = useSecurityGate({
    onAudit: auditTrail.track,
  })

  const sectionContent = useMemo(() => {
    if (!security.authenticated) {
      return null
    }

    if (!security.allowed.includes(section)) {
      return (
        <section className="card-page">
          <div className="card-head">
            <h2>Acceso restringido por rol</h2>
            <p>El rol actual no tiene permisos para esta sección.</p>
          </div>
        </section>
      )
    }

    if (section === 'resumen') {
      return (
        <OverviewPage
          filter={filter}
          onFilterChange={setFilter}
          events={filteredEvents}
          kpi={kpi}
          trafficPoints={series}
          realtimeState={summary.connectionState}
          alerts={summary.alerts}
        />
      )
    }

    if (section === 'auditoria') {
      return <AuditPage filter={filter} onFilterChange={setFilter} events={exportableEvents} />
    }

    if (section === 'usuarios') {
      return <UsersPage />
    }

    if (section === 'servidores') {
      return <ServersPage />
    }

    return <SettingsPage />
  }, [section, security.authenticated, security.allowed, filter, setFilter, filteredEvents, kpi, series, summary, exportableEvents])

  if (!security.authenticated) {
    return (
      <main className="auth-shell">
        <section className="auth-card">
          <h1>Ingreso administrativo</h1>
          <p>Autenticación RBAC + 2FA (demo).</p>

          <label>
            Rol
            <select
              value={security.role}
              onChange={(event) => security.setRole(event.target.value as 'admin' | 'operador' | 'analista')}
            >
              <option value="admin">admin</option>
              <option value="operador">operador</option>
              <option value="analista">analista</option>
            </select>
          </label>

          <label>
            Código 2FA
            <input
              value={security.totpCode}
              onChange={(event) => security.setTotpCode(event.target.value)}
              placeholder="123456"
            />
          </label>

          <Button type="button" onClick={() => security.verifyTotp()}>
            Validar sesión
          </Button>
          <div className="auth-actions">
            <Button type="button" variant="secondary" onClick={() => security.refreshSession()}>
              Refresh JWT
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={async () => {
                await security.registerWebAuthn()
              }}
            >
              Registrar WebAuthn
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={async () => {
                await security.authenticateWebAuthn()
              }}
            >
              Auth WebAuthn
            </Button>
          </div>
          <small>{security.securityStatus}</small>
          <small>Para demo: usa 123456</small>
        </section>
      </main>
    )
  }

  return (
    <main className="admin-shell">
      <aside className="left-nav">
        <div>
          <p className="badge">Qrypta Admin</p>
          <h1>Centro de Control</h1>
          <p className="muted">Panel web para monitoreo y operaciones seguras.</p>
          <small className="muted">Rol: {security.role} | Sesión: {security.sessionExpiresIn} min</small>
        </div>

        <nav>
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${section === item.id ? 'active' : ''}`}
              type="button"
              onClick={() => setSection(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="quick-actions">
          <h3>Acciones rapidas</h3>
          <button type="button">Limpiar cola de mensajes</button>
          <button type="button">Exportar auditoria</button>
          <button type="button" onClick={() => security.consumeSessionMinute()}>
            Simular +1 min sesión
          </button>
          <Button type="button" variant="ghost" onClick={() => security.logout()}>
            Cerrar sesión
          </Button>
          <small>{security.securityStatus}</small>
          <label className="ws-input">
            WS métricas
            <input value={wsUrl} onChange={(event) => setWsUrl(event.target.value)} />
          </label>

          <div className="audit-trail-card">
            <div className="audit-trail-head">
              <h3>Audit trail de cambios</h3>
              <Button type="button" variant="ghost" size="sm" onClick={() => auditTrail.clear()}>
                Limpiar
              </Button>
            </div>
            <ul className="audit-trail-list">
              {auditTrail.latest.map((entry) => (
                <li key={entry.id}>
                  <strong>{entry.action}</strong>
                  <small>{entry.actor}</small>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </aside>

      <section className="main-content">
        <Suspense fallback={<div className="loading-card">Cargando modulo...</div>}>
          {sectionContent}
        </Suspense>
      </section>
    </main>
  )
}

export default App
