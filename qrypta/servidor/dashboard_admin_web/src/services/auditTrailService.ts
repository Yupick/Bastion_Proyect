import type { AuditTrailEntry } from '../types/admin'

const STORAGE_KEY = 'qrypta-admin-audit-trail'

export function readAuditTrail(): AuditTrailEntry[] {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return []
  }

  try {
    return JSON.parse(raw) as AuditTrailEntry[]
  } catch {
    return []
  }
}

export function appendAuditTrail(entry: Omit<AuditTrailEntry, 'id' | 'at'>): AuditTrailEntry {
  const fullEntry: AuditTrailEntry = {
    id: crypto.randomUUID(),
    at: new Date().toISOString(),
    ...entry,
  }

  const next = [fullEntry, ...readAuditTrail()].slice(0, 80)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  return fullEntry
}

export function clearAuditTrail() {
  localStorage.removeItem(STORAGE_KEY)
}
