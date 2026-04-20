import { useMemo, useState } from 'react'
import { adminUsers, auditEvents, serverNodes } from '../store/adminStore'
import type { AuditEvent, EventLevel } from '../types/admin'

export function useAdminDashboard() {
  const [filter, setFilter] = useState<'TODOS' | EventLevel>('TODOS')

  const filteredEvents = useMemo(() => {
    if (filter === 'TODOS') return auditEvents
    return auditEvents.filter((event) => event.level === filter)
  }, [filter])

  const kpi = useMemo(
    () => ({
      uptime: '99.93%',
      activePeers: 182,
      queueMessages: serverNodes.reduce((sum, node) => sum + node.queueSize, 0),
      activeAdmins: adminUsers.filter((user) => user.status === 'activo').length,
      criticalEvents: auditEvents.filter((event) => event.level === 'ERROR').length,
    }),
    [],
  )

  const exportableEvents: AuditEvent[] = filteredEvents

  return {
    filter,
    setFilter,
    filteredEvents,
    kpi,
    exportableEvents,
  }
}
