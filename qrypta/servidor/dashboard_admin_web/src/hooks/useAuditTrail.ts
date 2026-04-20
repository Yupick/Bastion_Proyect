import { useCallback, useMemo, useState } from 'react'
import { appendAuditTrail, clearAuditTrail, readAuditTrail } from '../services/auditTrailService'

export function useAuditTrail() {
  const [entries, setEntries] = useState(() => readAuditTrail())

  const track = useCallback((actor: string, action: string, detail?: string) => {
    const entry = appendAuditTrail({ actor, action, detail })
    setEntries((prev) => [entry, ...prev].slice(0, 80))
  }, [])

  const clear = useCallback(() => {
    clearAuditTrail()
    setEntries([])
  }, [])

  const latest = useMemo(() => entries.slice(0, 8), [entries])

  return {
    entries,
    latest,
    track,
    clear,
  }
}
