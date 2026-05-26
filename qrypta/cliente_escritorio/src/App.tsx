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

const WORD_BANK = [
  'nodo',
  'firma',
  'canal',
  'clave',
  'cifrado',
  'grupo',
  'sesion',
  'respaldo',
  'sync',
  'dispositivo',
  'seguro',
  'latencia',
  'auditado',
  'llave',
  'privado',
  'publico',
]

type DesktopBackup = {
  alias: string
  mnemonic: string
  devices: string[]
  exportedAt: string
}

function toBase64(bytes: Uint8Array) {
  return btoa(String.fromCharCode(...bytes))
}

function fromBase64(raw: string) {
  return Uint8Array.from(atob(raw), (char) => char.charCodeAt(0))
}

async function deriveKey(passphrase: string) {
  const raw = new TextEncoder().encode(`qrypta-desktop-backup:${passphrase}`)
  const digest = await crypto.subtle.digest('SHA-256', raw)
  return crypto.subtle.importKey('raw', digest, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt'])
}

async function encryptBackup(snapshot: DesktopBackup, passphrase: string) {
  if (passphrase.trim().length < 8) {
    throw new Error('Passphrase demasiado corta')
  }

  const iv = crypto.getRandomValues(new Uint8Array(12))
  const key = await deriveKey(passphrase)
  const clear = new TextEncoder().encode(JSON.stringify(snapshot))
  const cipher = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, clear)

  return btoa(
    JSON.stringify({
      alg: 'aes-gcm',
      iv: toBase64(iv),
      ct: toBase64(new Uint8Array(cipher)),
    }),
  )
}

async function decryptBackup(blob: string, passphrase: string): Promise<DesktopBackup> {
  const payload = JSON.parse(atob(blob)) as { iv: string; ct: string }
  const key = await deriveKey(passphrase)
  const clear = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: fromBase64(payload.iv) },
    key,
    fromBase64(payload.ct),
  )

  return JSON.parse(new TextDecoder().decode(clear)) as DesktopBackup
}

function generateMnemonic() {
  return Array.from({ length: 24 }, () => WORD_BANK[Math.floor(Math.random() * WORD_BANK.length)]).join(' ')
}

export function App() {
  const [ultimaAccion, setUltimaAccion] = useState('Sin acciones recientes.')
  const [archivoArrastrado, setArchivoArrastrado] = useState<string | null>(null)
  const [clipboardTexto, setClipboardTexto] = useState('')
  const [menuAbierto, setMenuAbierto] = useState(false)
  const [alias, setAlias] = useState('desktop-operator')
  const [mnemonic, setMnemonic] = useState('')
  const [groupId, setGroupId] = useState('ops-desktop')
  const [groupMembers, setGroupMembers] = useState('desktop-operator,movil-01')
  const [groupMessage, setGroupMessage] = useState('')
  const [groupTimeline, setGroupTimeline] = useState<string[]>([])
  const [deviceAlias, setDeviceAlias] = useState('Workstation Linux')
  const [linkedDevices, setLinkedDevices] = useState<string[]>(['Movil principal'])
  const [backupPassphrase, setBackupPassphrase] = useState('')
  const [backupBlob, setBackupBlob] = useState('')

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

  const registerLocal = () => {
    const generated = generateMnemonic()
    setMnemonic(generated)
    setUltimaAccion('Identidad local generada con frase de recuperación.')
  }

  const createGroup = () => {
    const gid = groupId.trim()
    if (!gid) {
      setUltimaAccion('Group ID inválido')
      return
    }

    setGroupTimeline((prev) => [`Grupo ${gid} creado con ${groupMembers}`, ...prev].slice(0, 8))
    setUltimaAccion(`Grupo ${gid} creado`)
  }

  const sendGroupMessage = () => {
    const message = groupMessage.trim()
    if (!message) {
      return
    }
    setGroupTimeline((prev) => [`${alias}: ${message}`, ...prev].slice(0, 8))
    setGroupMessage('')
    setUltimaAccion('Mensaje de grupo enviado')
  }

  const linkDevice = () => {
    const candidate = deviceAlias.trim()
    if (!candidate) {
      return
    }

    setLinkedDevices((prev) => {
      if (prev.includes(candidate)) {
        return prev
      }
      return [...prev, candidate]
    })
    setUltimaAccion(`Dispositivo ${candidate} vinculado`)
  }

  const unlinkDevice = (target: string) => {
    setLinkedDevices((prev) => prev.filter((item) => item !== target))
    setUltimaAccion(`Dispositivo ${target} desvinculado`)
  }

  const exportBackup = async () => {
    try {
      const blob = await encryptBackup(
        {
          alias,
          mnemonic,
          devices: linkedDevices,
          exportedAt: new Date().toISOString(),
        },
        backupPassphrase,
      )
      setBackupBlob(blob)
      setUltimaAccion('Backup cifrado exportado')
    } catch (error) {
      setUltimaAccion(error instanceof Error ? `Error backup: ${error.message}` : 'Error exportando backup')
    }
  }

  const restoreBackup = async () => {
    try {
      const restored = await decryptBackup(backupBlob, backupPassphrase)
      setAlias(restored.alias)
      setMnemonic(restored.mnemonic)
      setLinkedDevices(restored.devices)
      setUltimaAccion(`Backup restaurado (${restored.exportedAt})`)
    } catch (error) {
      setUltimaAccion(error instanceof Error ? `Error restore: ${error.message}` : 'Error restaurando backup')
    }
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
        <p className="subtle">MVP Fase 13c: registro local, grupos, sync y backup/restore.</p>
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
        <article>
          <h2>Registro local</h2>
          <p>Alias y frase de recuperación para identidad local.</p>
          <div className="form-grid">
            <input className="plain-input" value={alias} onChange={(event) => setAlias(event.target.value)} />
            <button type="button" onClick={registerLocal}>Generar identidad</button>
            <textarea className="plain-input" value={mnemonic} onChange={(event) => setMnemonic(event.target.value)} />
          </div>
        </article>
        <article>
          <h2>Grupos</h2>
          <p>Gestión base de miembros y timeline local cifrado.</p>
          <div className="form-grid">
            <input className="plain-input" value={groupId} onChange={(event) => setGroupId(event.target.value)} />
            <input className="plain-input" value={groupMembers} onChange={(event) => setGroupMembers(event.target.value)} />
            <button type="button" onClick={createGroup}>Crear grupo</button>
            <input className="plain-input" value={groupMessage} onChange={(event) => setGroupMessage(event.target.value)} />
            <button type="button" onClick={sendGroupMessage}>Enviar al grupo</button>
          </div>
          <ul className="timeline-list">
            {groupTimeline.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h2>Sync multi-dispositivo</h2>
          <p>Vinculación y revocación de dispositivos autorizados.</p>
          <div className="form-grid">
            <input className="plain-input" value={deviceAlias} onChange={(event) => setDeviceAlias(event.target.value)} />
            <button type="button" onClick={linkDevice}>Vincular</button>
          </div>
          <ul className="timeline-list">
            {linkedDevices.map((device) => (
              <li key={device}>
                <span>{device}</span>
                <button type="button" onClick={() => unlinkDevice(device)}>Revocar</button>
              </li>
            ))}
          </ul>
        </article>
        <article>
          <h2>Backup y restore</h2>
          <p>Exportación cifrada AES-GCM y restauración local.</p>
          <div className="form-grid">
            <input
              className="plain-input"
              type="password"
              value={backupPassphrase}
              onChange={(event) => setBackupPassphrase(event.target.value)}
              placeholder="Passphrase"
            />
            <div className="action-row">
              <button type="button" onClick={exportBackup}>Exportar</button>
              <button type="button" onClick={restoreBackup}>Restaurar</button>
            </div>
            <textarea className="plain-input" value={backupBlob} onChange={(event) => setBackupBlob(event.target.value)} />
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
