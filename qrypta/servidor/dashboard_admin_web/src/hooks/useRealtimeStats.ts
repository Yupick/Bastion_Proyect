import { useEffect, useMemo, useRef, useState } from 'react'

type MetricPoint = {
  label: string
  requests: number
  errors: number
}

type AlertItem = {
  id: string
  level: 'INFO' | 'WARN' | 'CRITICAL'
  text: string
}

function withAlert(
  level: AlertItem['level'],
  text: string,
  previous: AlertItem[],
): AlertItem[] {
  return [{ id: crypto.randomUUID(), level, text }, ...previous].slice(0, 6)
}

const BASE_SERIES: MetricPoint[] = [
  { label: '10:30', requests: 420, errors: 6 },
  { label: '10:45', requests: 470, errors: 9 },
  { label: '11:00', requests: 520, errors: 4 },
  { label: '11:15', requests: 610, errors: 11 },
  { label: '11:30', requests: 560, errors: 5 },
  { label: '11:45', requests: 590, errors: 7 },
]

export function useRealtimeStats(wsUrl: string) {
  const [series, setSeries] = useState<MetricPoint[]>(BASE_SERIES)
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'fallback'>('connecting')
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.addEventListener('open', () => {
      setConnectionState('connected')
      setAlerts((prev) => withAlert('INFO', 'Canal realtime conectado', prev))
    })

    ws.addEventListener('message', (event) => {
      try {
        const parsed = JSON.parse(event.data) as { requests: number; errors: number; label?: string }
        const point: MetricPoint = {
          label: parsed.label ?? new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
          requests: parsed.requests,
          errors: parsed.errors,
        }
        setSeries((prev) => [...prev.slice(-11), point])
        if (point.errors >= 10) {
          setAlerts((prev) => withAlert('CRITICAL', `Pico de errores detectado (${point.errors})`, prev))
        }
      } catch {
        setAlerts((prev) => withAlert('WARN', 'Evento realtime con formato invalido', prev))
      }
    })

    ws.addEventListener('error', () => {
      setConnectionState('fallback')
    })

    ws.addEventListener('close', () => {
      setConnectionState((prev) => (prev === 'connected' ? 'fallback' : prev))
    })

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [wsUrl])

  useEffect(() => {
    if (connectionState !== 'fallback') {
      return
    }

    const timer = window.setInterval(() => {
      setSeries((prev) => {
        const last = prev[prev.length - 1] ?? BASE_SERIES[BASE_SERIES.length - 1]
        const nextRequests = Math.max(250, Math.min(800, last.requests + Math.floor((Math.random() - 0.4) * 80)))
        const nextErrors = Math.max(1, Math.min(15, last.errors + Math.floor((Math.random() - 0.5) * 4)))
        const nextPoint: MetricPoint = {
          label: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
          requests: nextRequests,
          errors: nextErrors,
        }

        if (nextErrors >= 10) {
          setAlerts((prevAlerts) => withAlert('WARN', `Error rate elevado (${nextErrors})`, prevAlerts))
        }

        return [...prev.slice(-11), nextPoint]
      })
    }, 4500)

    return () => {
      window.clearInterval(timer)
    }
  }, [connectionState])

  const summary = useMemo(
    () => ({
      connectionState,
      latest: series[series.length - 1],
      alerts,
    }),
    [connectionState, series, alerts],
  )

  return {
    series,
    summary,
  }
}
