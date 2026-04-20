import { useState } from 'react'
import { platformSettings } from '../store/adminStore'

export function SettingsPage() {
  const [settings, setSettings] = useState(platformSettings)

  const updateNumber = (key: 'rateLimitPerMinute' | 'sessionTimeoutMinutes' | 'auditRetentionDays', value: string) => {
    setSettings((previous) => ({
      ...previous,
      [key]: Number(value),
    }))
  }

  return (
    <section className="card-page">
      <div className="card-head">
        <h2>Configuracion operativa</h2>
        <p>Ajustes base de seguridad, sesiones y retencion de auditoria.</p>
      </div>

      <form className="settings-form">
        <label>
          Rate limit (req/min)
          <input
            type="number"
            min={10}
            value={settings.rateLimitPerMinute}
            onChange={(event) => updateNumber('rateLimitPerMinute', event.target.value)}
          />
        </label>

        <label>
          Timeout de sesion (min)
          <input
            type="number"
            min={5}
            value={settings.sessionTimeoutMinutes}
            onChange={(event) => updateNumber('sessionTimeoutMinutes', event.target.value)}
          />
        </label>

        <label>
          Retencion de auditoria (dias)
          <input
            type="number"
            min={7}
            value={settings.auditRetentionDays}
            onChange={(event) => updateNumber('auditRetentionDays', event.target.value)}
          />
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={settings.allowDangerousRawSql}
            onChange={(event) =>
              setSettings((previous) => ({
                ...previous,
                allowDangerousRawSql: event.target.checked,
              }))
            }
          />
          Permitir operaciones Raw SQL peligrosas (solo emergencia)
        </label>

        <button type="button">Guardar configuracion</button>
      </form>
    </section>
  )
}
