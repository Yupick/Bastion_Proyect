import type { AdminUser, AuditEvent, PlatformSettings, ServerNode } from '../types/admin'

export const auditEvents: AuditEvent[] = [
  {
    id: 'ev-1',
    level: 'EXITO',
    detail: 'Rotacion de clave de sesion completada para 18 peers',
    time: '11:31',
    source: 'SISTEMA',
  },
  {
    id: 'ev-2',
    level: 'INFO',
    detail: 'Sincronizacion multidispositivo finalizada (7 equipos)',
    time: '11:20',
    source: 'API',
  },
  {
    id: 'ev-3',
    level: 'ADVERTENCIA',
    detail: 'Pico de peticiones en /v1/mensajes (rate limit aplicado)',
    time: '10:58',
    source: 'API',
  },
  {
    id: 'ev-4',
    level: 'ERROR',
    detail: 'Fallo de conexion temporal con nodo DHT remoto',
    time: '10:44',
    source: 'NODO',
  },
]

export const adminUsers: AdminUser[] = [
  { id: 'u-1', alias: 'ops-central', role: 'admin', status: 'activo', lastSeen: 'hace 2 min' },
  { id: 'u-2', alias: 'auditoria-01', role: 'analista', status: 'activo', lastSeen: 'hace 9 min' },
  { id: 'u-3', alias: 'guardia-nocturna', role: 'operador', status: 'bloqueado', lastSeen: 'hace 1 h' },
]

export const serverNodes: ServerNode[] = [
  { id: 's-1', name: 'nodo-eu-central', status: 'operativo', region: 'eu-central', queueSize: 8 },
  { id: 's-2', name: 'nodo-us-east', status: 'degradado', region: 'us-east', queueSize: 21 },
  { id: 's-3', name: 'nodo-sa-south', status: 'operativo', region: 'sa-south', queueSize: 5 },
]

export const platformSettings: PlatformSettings = {
  rateLimitPerMinute: 120,
  sessionTimeoutMinutes: 30,
  auditRetentionDays: 90,
  allowDangerousRawSql: false,
}

export const trafficSeries = [
  { label: '10:30', requests: 420, errors: 6 },
  { label: '10:45', requests: 470, errors: 9 },
  { label: '11:00', requests: 520, errors: 4 },
  { label: '11:15', requests: 610, errors: 11 },
  { label: '11:30', requests: 560, errors: 5 },
  { label: '11:45', requests: 590, errors: 7 },
]
