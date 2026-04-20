export type EventLevel = 'INFO' | 'EXITO' | 'ADVERTENCIA' | 'ERROR'

export type AuditEvent = {
  id: string
  level: EventLevel
  detail: string
  time: string
  source: 'API' | 'NODO' | 'SISTEMA'
}

export type UserRole = 'admin' | 'operador' | 'analista'

export type AdminUser = {
  id: string
  alias: string
  role: UserRole
  status: 'activo' | 'bloqueado'
  lastSeen: string
}

export type ServerNode = {
  id: string
  name: string
  status: 'operativo' | 'degradado' | 'caido'
  region: string
  queueSize: number
}

export type PlatformSettings = {
  rateLimitPerMinute: number
  sessionTimeoutMinutes: number
  auditRetentionDays: number
  allowDangerousRawSql: boolean
}

export type AuditTrailEntry = {
  id: string
  action: string
  actor: string
  at: string
  detail?: string
}
