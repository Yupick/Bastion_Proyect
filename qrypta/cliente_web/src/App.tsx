import { useEffect, useMemo, useRef, useState } from 'react'
import { useAuth } from './hooks/useAuth'
import { useChat } from './hooks/useChat'
import { useContacts } from './hooks/useContacts'
import { Button } from './components/ui/button'
import { decryptMessage, encryptMessage } from './services/cryptoService'
import { cacheMessage } from './services/indexedDbService'
import { useUiStore } from './store/uiStore'
import './App.css'

type Contacto = {
  id: string
  nombre: string
  ultimoMensaje: string
  hora: string
  noLeidos: number
  estado: 'online' | 'offline'
}

type Mensaje = {
  id: string
  cuerpo: string
  incoming: boolean
  hora: string
  adjunto?: { nombre: string; contenido: string }
}

type AjustesUsuario = {
  alias: string
  privacidadAlta: boolean
  notificacionesPush: boolean
  ocultarMetadata: boolean
}

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>
}

const MENSAJES_INICIALES: Mensaje[] = [
  {
    id: 'm-1',
    cuerpo: 'Canal listo. Puedes enviar mensajes cifrados.',
    incoming: true,
    hora: '11:40',
  },
  {
    id: 'm-2',
    cuerpo: 'Perfecto. Validando firma de alias.',
    incoming: false,
    hora: '11:41',
  },
  {
    id: 'm-3',
    cuerpo: 'Firma valida. Sesion segura establecida.',
    incoming: true,
    hora: '11:42',
  },
]

const EMOJIS_RAPIDOS = ['🔐', '✅', '⚡', '🛰️', '🛡️']

const HORA_FORMATTER = new Intl.DateTimeFormat('es-ES', {
  hour: '2-digit',
  minute: '2-digit',
})

function App() {
  const [seccion, setSeccion] = useState<'chats' | 'contactos' | 'dispositivos' | 'ajustes'>('chats')
  const contactoActivoId = useUiStore((state) => state.activeContactId)
  const setContactoActivoId = useUiStore((state) => state.setActiveContactId)
  const [texto, setTexto] = useState('')
  const [mensajes, setMensajes] = useState<Mensaje[]>(MENSAJES_INICIALES)
  const [archivoAdjunto, setArchivoAdjunto] = useState<File | null>(null)
  const [notificacionesEntrega, setNotificacionesEntrega] = useState<string[]>([])
  const [typingActivo, setTypingActivo] = useState(false)
  const [estadoConexion, setEstadoConexion] = useState<'conectando' | 'conectado' | 'simulado'>('conectando')
  const [wsUrl, setWsUrl] = useState('ws://localhost:8000/ws')
  const [ajustes, setAjustes] = useState<AjustesUsuario>({
    alias: 'qrypta_operator',
    privacidadAlta: true,
    notificacionesPush: true,
    ocultarMetadata: true,
  })
  const [installEvent, setInstallEvent] = useState<BeforeInstallPromptEvent | null>(null)
  const [modoOffline, setModoOffline] = useState(!navigator.onLine)
  const [mnemonicInput, setMnemonicInput] = useState('')
  const [mnemonicGenerada, setMnemonicGenerada] = useState('')
  const [authError, setAuthError] = useState<string | null>(null)
  const [pushStatus, setPushStatus] = useState('Push sin configurar')

  const { contacts } = useContacts()
  const { isAuthenticated, authStatus, register, login, refresh, registerWebAuthn, logout } = useAuth()
  const { cached } = useChat()

  const wsRef = useRef<WebSocket | null>(null)
  const typingTimer = useRef<number | null>(null)

  const contactoActivo = useMemo<Contacto>(
    () =>
      contacts.find((c) => c.id === contactoActivoId) ?? {
        id: 'fallback',
        nombre: 'Sin contacto',
        ultimoMensaje: '',
        hora: '--:--',
        noLeidos: 0,
        estado: 'offline',
      },
    [contactoActivoId, contacts],
  )

  const puedeEnviar = texto.trim().length > 0 || archivoAdjunto !== null

  useEffect(() => {
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.addEventListener('open', () => {
      setEstadoConexion('conectado')
    })

    ws.addEventListener('error', () => {
      setEstadoConexion('simulado')
    })

    ws.addEventListener('close', () => {
      setEstadoConexion((current) => (current === 'conectado' ? 'simulado' : current))
    })

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [wsUrl])

  useEffect(() => {
    return () => {
      if (typingTimer.current !== null) {
        window.clearTimeout(typingTimer.current)
      }
    }
  }, [])

  useEffect(() => {
    const onInstallPrompt = (event: Event) => {
      event.preventDefault()
      setInstallEvent(event as BeforeInstallPromptEvent)
    }

    const onOnline = () => setModoOffline(false)
    const onOffline = () => setModoOffline(true)

    window.addEventListener('beforeinstallprompt', onInstallPrompt)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)

    return () => {
      window.removeEventListener('beforeinstallprompt', onInstallPrompt)
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  const addEmoji = (emoji: string) => setTexto((prev) => `${prev}${emoji}`)

  const onTyping = (value: string) => {
    setTexto(value)
    setTypingActivo(value.trim().length > 0)
    if (typingTimer.current !== null) {
      window.clearTimeout(typingTimer.current)
    }
    typingTimer.current = window.setTimeout(() => {
      setTypingActivo(false)
    }, 900)
  }

  const appendEntrega = (textoEntrega: string) => {
    setNotificacionesEntrega((prev) => [textoEntrega, ...prev].slice(0, 5))
  }

  const renderEstadoConexion =
    estadoConexion === 'conectado'
      ? 'WebSocket conectado'
      : estadoConexion === 'conectando'
        ? 'Conectando WebSocket...'
        : 'Modo simulado (sin WS)'

  const instalarApp = async () => {
    if (!installEvent) {
      return
    }
    await installEvent.prompt()
    await installEvent.userChoice
    setInstallEvent(null)
  }

  const activarPush = async () => {
    if (!('Notification' in window)) {
      setPushStatus('Push no soportado por este navegador')
      return
    }

    const permission = await Notification.requestPermission()
    if (permission !== 'granted') {
      setPushStatus('Permiso de notificaciones denegado')
      return
    }

    setPushStatus('Push habilitado')

    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.ready
      registration.showNotification('Qrypta Web', {
        body: 'Notificaciones push activadas',
        icon: '/vite.svg',
        tag: 'qrypta-push-enabled',
      })
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <p className="eyebrow">Qrypta</p>
          <h1>Mensajeria Segura</h1>
          <p className="subtle">Cliente web base para fase 13b</p>
        </div>

        <nav className="menu">
          <button
            className={`menu-item ${seccion === 'chats' ? 'active' : ''}`}
            type="button"
            onClick={() => setSeccion('chats')}
          >
            Chats
          </button>
          <button
            className={`menu-item ${seccion === 'contactos' ? 'active' : ''}`}
            type="button"
            onClick={() => setSeccion('contactos')}
          >
            Contactos
          </button>
          <button
            className={`menu-item ${seccion === 'dispositivos' ? 'active' : ''}`}
            type="button"
            onClick={() => setSeccion('dispositivos')}
          >
            Dispositivos
          </button>
          <button
            className={`menu-item ${seccion === 'ajustes' ? 'active' : ''}`}
            type="button"
            onClick={() => setSeccion('ajustes')}
          >
            Ajustes
          </button>
        </nav>

        <div className="status-card">
          <p>Canal cifrado</p>
          <strong>AES-256-GCM Activo</strong>
          <small>Sesion: Kyber768 + Dilithium3</small>
          <small>{renderEstadoConexion}</small>
          <small>{modoOffline ? 'Modo offline activo' : 'Modo online activo'}</small>
          <small>{isAuthenticated ? 'Sesion autenticada' : 'Sesion sin token local'}</small>
          <small>{cached.data?.length ?? 0} mensajes cacheados (IndexedDB)</small>
          {installEvent ? (
            <Button type="button" className="install-btn" onClick={instalarApp} variant="secondary" size="sm">
              Instalar PWA
            </Button>
          ) : null}
        </div>
      </aside>

      <section className="conversation-panel">
        <header className="panel-header">
          <div>
            <p className="eyebrow">Conversacion activa</p>
            <h2>{contactoActivo.nombre}</h2>
          </div>
          <span className={`pill ${contactoActivo.estado === 'online' ? '' : 'pill-off'}`}>
            {contactoActivo.estado}
          </span>
        </header>

        {seccion === 'chats' ? (
          <>
            <ul className="mensajes">
              {mensajes.map((mensaje) => (
                <li key={mensaje.id} className={`mensaje ${mensaje.incoming ? 'recibido' : 'enviado'}`}>
                  <p>{mensaje.cuerpo}</p>
                  {mensaje.adjunto ? (
                    <button
                      type="button"
                      className="attachment-btn"
                      onClick={() => {
                        const blob = new Blob([mensaje.adjunto?.contenido ?? ''], { type: 'text/plain' })
                        const url = URL.createObjectURL(blob)
                        const anchor = document.createElement('a')
                        anchor.href = url
                        anchor.download = mensaje.adjunto?.nombre ?? 'adjunto.txt'
                        anchor.click()
                        URL.revokeObjectURL(url)
                      }}
                    >
                      Descargar {mensaje.adjunto.nombre}
                    </button>
                  ) : null}
                  <small>{mensaje.hora}</small>
                </li>
              ))}
            </ul>

            {typingActivo ? <p className="typing">Escribiendo mensaje cifrado...</p> : null}

            <form
              className="composer"
              onSubmit={async (event) => {
                event.preventDefault()
                if (!puedeEnviar) return

                const plain = texto || '[Adjunto seguro enviado]'
                const encrypted = await encryptMessage(plain)
                const decrypted = await decryptMessage(encrypted)
                const id = crypto.randomUUID()

                await cacheMessage(id, decrypted, new Date().toISOString())

                setMensajes((prev) => [
                  {
                    id,
                    cuerpo: decrypted,
                    incoming: false,
                    hora: HORA_FORMATTER.format(new Date()),
                    adjunto: archivoAdjunto
                      ? {
                          nombre: archivoAdjunto.name,
                          contenido: `Archivo simulado: ${archivoAdjunto.name}`,
                        }
                      : undefined,
                  },
                  ...prev,
                ])

                appendEntrega(`Entregado a ${contactoActivo.nombre} (${HORA_FORMATTER.format(new Date())})`)

                setTexto('')
                setArchivoAdjunto(null)
                setTypingActivo(false)
              }}
            >
              <textarea
                value={texto}
                onChange={(event) => onTyping(event.target.value)}
                placeholder="Escribe un mensaje seguro..."
                aria-label="Mensaje"
              />
              <div className="composer-actions">
                <div className="emoji-row">
                  {EMOJIS_RAPIDOS.map((emoji) => (
                    <button key={emoji} type="button" onClick={() => addEmoji(emoji)}>
                      {emoji}
                    </button>
                  ))}
                </div>

                <label className="file-btn">
                  Adjuntar
                  <input
                    type="file"
                    onChange={(event) => setArchivoAdjunto(event.target.files?.[0] ?? null)}
                  />
                </label>
                <button type="submit" disabled={!puedeEnviar}>
                  Enviar
                </button>
              </div>
            </form>

            {archivoAdjunto ? <p className="file-hint">Adjunto listo: {archivoAdjunto.name}</p> : null}
          </>
        ) : null}

        {seccion === 'dispositivos' ? (
          <section className="config-card">
            <h3>Dispositivos enlazados</h3>
            <p>Estado de conexion actual: {renderEstadoConexion}</p>
            <label>
              URL WebSocket
              <input value={wsUrl} onChange={(event) => setWsUrl(event.target.value)} />
            </label>
          </section>
        ) : null}

        {seccion === 'ajustes' ? (
          <section className="config-card">
            <h3>Config panel</h3>
            <label>
              Alias
              <input
                value={ajustes.alias}
                onChange={(event) => setAjustes((prev) => ({ ...prev, alias: event.target.value }))}
              />
            </label>
            <label className="inline-check">
              <input
                type="checkbox"
                checked={ajustes.privacidadAlta}
                onChange={(event) =>
                  setAjustes((prev) => ({
                    ...prev,
                    privacidadAlta: event.target.checked,
                  }))
                }
              />
              Privacidad alta
            </label>
            <label className="inline-check">
              <input
                type="checkbox"
                checked={ajustes.notificacionesPush}
                onChange={(event) =>
                  setAjustes((prev) => ({
                    ...prev,
                    notificacionesPush: event.target.checked,
                  }))
                }
              />
              Notificaciones push
            </label>
            <label className="inline-check">
              <input
                type="checkbox"
                checked={ajustes.ocultarMetadata}
                onChange={(event) =>
                  setAjustes((prev) => ({
                    ...prev,
                    ocultarMetadata: event.target.checked,
                  }))
                }
              />
              Ocultar metadata de presencia
            </label>

            <h3>Autenticacion local</h3>
            <label>
              Mnemonic BIP-39
              <input
                value={mnemonicInput}
                onChange={(event) => setMnemonicInput(event.target.value)}
                placeholder="Ingresa 12 o 24 palabras"
              />
            </label>

            <div className="emoji-row">
              <Button
                type="button"
                onClick={() => {
                  try {
                    setAuthError(null)
                    const m = register()
                    setMnemonicGenerada(m)
                  } catch (error) {
                    setAuthError(error instanceof Error ? error.message : 'Error registrando identidad')
                  }
                }}
              >
                Registro local
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  try {
                    setAuthError(null)
                    login(mnemonicInput)
                  } catch (error) {
                    setAuthError(error instanceof Error ? error.message : 'Error de login')
                  }
                }}
              >
                Login BIP-39
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => {
                  try {
                    setAuthError(null)
                    refresh()
                  } catch (error) {
                    setAuthError(error instanceof Error ? error.message : 'Error renovando token')
                  }
                }}
              >
                Refresh JWT
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={async () => {
                  try {
                    setAuthError(null)
                    await registerWebAuthn()
                  } catch (error) {
                    setAuthError(error instanceof Error ? error.message : 'Error registrando WebAuthn')
                  }
                }}
              >
                Registrar WebAuthn
              </Button>
              <Button type="button" variant="secondary" onClick={activarPush}>
                Activar Push
              </Button>
              <Button type="button" variant="ghost" onClick={() => logout()}>
                Cerrar sesion
              </Button>
            </div>

            {mnemonicGenerada ? <p>Mnemonic generada: {mnemonicGenerada}</p> : null}
            <p>{authStatus}</p>
            <p>{pushStatus}</p>
            {authError ? <p>{authError}</p> : null}
          </section>
        ) : null}

        {seccion === 'contactos' ? (
          <section className="config-card">
            <h3>Resumen de contactos</h3>
            <p>Selecciona un contacto desde el panel derecho para iniciar chat.</p>
            <p>{contacts.filter((c) => c.estado === 'online').length} contactos online.</p>
          </section>
        ) : null}

        <ul className="delivery-list">
          {notificacionesEntrega.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <aside className="contactos-panel">
        <div className="panel-title">
          <h3>Contactos</h3>
          <small>3 activos</small>
        </div>

        <ul>
          {contacts.map((contacto) => (
            <li key={contacto.id}>
              <button
                type="button"
                className={`contacto ${contacto.id === contactoActivoId ? 'seleccionado' : ''}`}
                onClick={() => setContactoActivoId(contacto.id)}
              >
                <div>
                  <strong>{contacto.nombre}</strong>
                  <p>{contacto.ultimoMensaje}</p>
                </div>
                <div className="meta">
                  <span>{contacto.hora}</span>
                  <small className={contacto.estado === 'online' ? 'dot-online' : 'dot-offline'}>
                    {contacto.estado}
                  </small>
                  {contacto.noLeidos > 0 ? <em>{contacto.noLeidos}</em> : null}
                </div>
              </button>
            </li>
          ))}
        </ul>
      </aside>
    </main>
  )
}

export default App
