import { useEffect, useState } from 'react'

type Atajo = {
  clave: string
  accion: string
}

const ATAJOS: Atajo[] = [
  { clave: 'Ctrl+N', accion: 'Nuevo chat' },
  { clave: 'Ctrl+K', accion: 'Buscar contacto' },
  { clave: 'Ctrl+Shift+S', accion: 'Sincronizar ahora' },
]

export function App() {
  const [ultimaAccion, setUltimaAccion] = useState('Sin acciones recientes.')
  const [archivoArrastrado, setArchivoArrastrado] = useState<string | null>(null)
  const [clipboardTexto, setClipboardTexto] = useState('')
  const [menuAbierto, setMenuAbierto] = useState(false)

  useEffect(() => {
    const onKeydown = (event: KeyboardEvent) => {
      if (event.ctrlKey && event.key.toLowerCase() === 'n') {
        event.preventDefault()
        setUltimaAccion('Atajo Ctrl+N ejecutado: Nuevo chat')
      }

      if (event.ctrlKey && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setUltimaAccion('Atajo Ctrl+K ejecutado: Buscar contacto')
      }

      if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 's') {
        event.preventDefault()
        setUltimaAccion('Atajo Ctrl+Shift+S ejecutado: Sincronización forzada')
      }
    }

    window.addEventListener('keydown', onKeydown)
    return () => window.removeEventListener('keydown', onKeydown)
  }, [])

  const notify = async () => {
    if (!('Notification' in window)) {
      setUltimaAccion('Notificaciones no soportadas en este entorno.')
      return
    }

    if (Notification.permission === 'default') {
      await Notification.requestPermission()
    }

    if (Notification.permission === 'granted') {
      new Notification('Qrypta Desktop', { body: 'Canal cifrado activo y sincronizado.' })
      setUltimaAccion('Notificación del sistema enviada.')
      return
    }

    setUltimaAccion('Permiso de notificaciones denegado.')
  }

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText('qrypta://session/secure-channel')
    setUltimaAccion('URL de sesión copiada al portapapeles.')
  }

  const readClipboard = async () => {
    const text = await navigator.clipboard.readText()
    setClipboardTexto(text)
    setUltimaAccion('Portapapeles leído correctamente.')
  }

  const handleDrop: React.DragEventHandler<HTMLDivElement> = (event) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    setArchivoArrastrado(file?.name ?? null)
    setUltimaAccion(file ? `Archivo recibido: ${file.name}` : 'Drop sin archivo válido.')
  }

  return (
    <main className="desktop-shell">
      <div className="window-controls">
        <button type="button" aria-label="Minimizar">−</button>
        <button type="button" aria-label="Maximizar">□</button>
        <button type="button" aria-label="Cerrar">×</button>
      </div>

      <header>
        <p className="eyebrow">Qrypta Desktop</p>
        <h1>Cliente Escritorio</h1>
        <p className="subtle">Base inicial lista para integrar E2E, grupos y sincronizacion.</p>
      </header>

      <div className="menu-bar">
        <button type="button" onClick={() => setMenuAbierto((prev) => !prev)}>
          Menú
        </button>
        <div className={`menu-content ${menuAbierto ? 'open' : ''}`}>
          <button type="button" onClick={() => setUltimaAccion('Menú: Abrir conversación')}>Abrir conversación</button>
          <button type="button" onClick={() => setUltimaAccion('Menú: Exportar historial cifrado')}>Exportar historial</button>
          <button type="button" onClick={() => setUltimaAccion('Menú: Preferencias de seguridad')}>Preferencias</button>
        </div>
      </div>

      <section className="panel-grid">
        <article>
          <h2>Estado</h2>
          <p>{ultimaAccion}</p>
        </article>
        <article>
          <h2>Mensajeria</h2>
          <p>Interfaz base creada para Windows y Linux con atajos.</p>
          <ul>
            {ATAJOS.map((atajo) => (
              <li key={atajo.clave}>
                <strong>{atajo.clave}</strong>: {atajo.accion}
              </li>
            ))}
          </ul>
        </article>
        <article>
          <h2>Integracion</h2>
          <p>Conectar con servidor FastAPI + WebSocket.</p>
          <div className="action-row">
            <button type="button" onClick={notify}>Notificar</button>
            <button type="button" onClick={copyToClipboard}>Copiar sesión</button>
            <button type="button" onClick={readClipboard}>Leer portapapeles</button>
          </div>
        </article>
      </section>

      <section
        className="drop-zone"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <h2>Drag and Drop</h2>
        <p>Suelta un archivo para asociarlo a una conversación segura.</p>
        <p>{archivoArrastrado ? `Último archivo: ${archivoArrastrado}` : 'Sin archivos arrastrados.'}</p>
      </section>

      <section className="clipboard-preview">
        <h2>Clipboard Manager</h2>
        <p>{clipboardTexto || 'No se ha leído contenido del portapapeles aún.'}</p>
      </section>
    </main>
  )
}
