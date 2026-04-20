import type { AuditEvent } from '../types/admin'

export function exportAuditAsJson(events: AuditEvent[]): void {
  const payload = JSON.stringify(events, null, 2)
  const blob = new Blob([payload], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `qrypta-auditoria-${new Date().toISOString().slice(0, 10)}.json`
  anchor.click()
  URL.revokeObjectURL(url)
}
