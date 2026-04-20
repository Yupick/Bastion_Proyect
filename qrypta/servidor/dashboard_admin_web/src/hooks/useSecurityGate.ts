import { useMemo, useState } from 'react'

type Role = 'admin' | 'operador' | 'analista'

type AuditLogger = (actor: string, action: string, detail?: string) => void

type SecurityGateOptions = {
  onAudit?: AuditLogger
}

const ACCESS_RULES: Record<Role, Array<'resumen' | 'auditoria' | 'usuarios' | 'servidores' | 'configuracion'>> = {
  admin: ['resumen', 'auditoria', 'usuarios', 'servidores', 'configuracion'],
  operador: ['resumen', 'usuarios', 'servidores'],
  analista: ['resumen', 'auditoria'],
}

const ACCESS_TOKEN_KEY = 'qrypta-admin-access-token'
const REFRESH_TOKEN_KEY = 'qrypta-admin-refresh-token'

function buildToken(payload: Record<string, string | number>) {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = btoa(JSON.stringify(payload))
  const signature = btoa(crypto.randomUUID())
  return `${header}.${body}.${signature}`
}

export function useSecurityGate(options?: SecurityGateOptions) {
  const audit = options?.onAudit
  const [role, setRole] = useState<Role>('admin')
  const [sessionExpiresIn, setSessionExpiresIn] = useState(30)
  const [totpCode, setTotpCode] = useState('')
  const [authenticated, setAuthenticated] = useState(false)
  const [securityStatus, setSecurityStatus] = useState('Sesion no autenticada')

  const allowed = useMemo(() => ACCESS_RULES[role], [role])

  const verifyTotp = () => {
    if (totpCode.trim() === '123456') {
      const now = Math.floor(Date.now() / 1000)
      const accessToken = buildToken({ sub: 'qrypta-admin', role, exp: now + 30 * 60 })
      const refreshToken = buildToken({ sub: 'qrypta-admin', scope: 'refresh', iat: now })
      localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
      setAuthenticated(true)
      setSecurityStatus('Sesion autenticada con JWT')
      audit?.('admin-ui', 'totp_login_success', `role=${role}`)
      return true
    }
    setSecurityStatus('Codigo 2FA invalido')
    audit?.('admin-ui', 'totp_login_failed', `role=${role}`)
    return false
  }

  const refreshSession = () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) {
      setSecurityStatus('No existe refresh token')
      return false
    }

    const now = Math.floor(Date.now() / 1000)
    const accessToken = buildToken({ sub: 'qrypta-admin', role, exp: now + 30 * 60 })
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    setSecurityStatus('Token renovado')
    audit?.('admin-ui', 'jwt_refresh_success', `role=${role}`)
    return true
  }

  const registerWebAuthn = async () => {
    if (!window.PublicKeyCredential || !navigator.credentials) {
      setSecurityStatus('WebAuthn no soportado')
      audit?.('admin-ui', 'webauthn_register_unsupported')
      return false
    }

    const challenge = crypto.getRandomValues(new Uint8Array(32))
    const userId = crypto.getRandomValues(new Uint8Array(32))

    await navigator.credentials.create({
      publicKey: {
        rp: { name: 'Qrypta Admin', id: window.location.hostname || 'localhost' },
        user: {
          id: userId,
          name: 'qrypta-admin',
          displayName: 'Qrypta Admin',
        },
        challenge,
        pubKeyCredParams: [{ type: 'public-key', alg: -7 }],
        timeout: 60000,
        authenticatorSelection: {
          residentKey: 'preferred',
          userVerification: 'preferred',
        },
        attestation: 'none',
      },
    })

    localStorage.setItem('qrypta-admin-webauthn-enabled', 'true')
    setSecurityStatus('WebAuthn registrado')
    audit?.('admin-ui', 'webauthn_register_success')
    return true
  }

  const authenticateWebAuthn = async () => {
    const enabled = localStorage.getItem('qrypta-admin-webauthn-enabled') === 'true'
    if (!enabled) {
      setSecurityStatus('WebAuthn no configurado')
      return false
    }

    if (!window.PublicKeyCredential || !navigator.credentials) {
      setSecurityStatus('WebAuthn no soportado')
      return false
    }

    const challenge = crypto.getRandomValues(new Uint8Array(32))
    await navigator.credentials.get({
      publicKey: {
        challenge,
        userVerification: 'preferred',
      },
    })

    setSecurityStatus('WebAuthn autenticado')
    audit?.('admin-ui', 'webauthn_auth_success')
    return true
  }

  const consumeSessionMinute = () => {
    setSessionExpiresIn((prev) => Math.max(0, prev - 1))
    audit?.('admin-ui', 'session_minute_consumed')
  }

  const logout = () => {
    setAuthenticated(false)
    setTotpCode('')
    setSessionExpiresIn(30)
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    setSecurityStatus('Sesion cerrada')
    audit?.('admin-ui', 'logout')
  }

  return {
    role,
    setRole,
    allowed,
    totpCode,
    setTotpCode,
    verifyTotp,
    refreshSession,
    registerWebAuthn,
    authenticateWebAuthn,
    authenticated,
    securityStatus,
    sessionExpiresIn,
    consumeSessionMinute,
    logout,
  }
}
