import * as bip39 from 'bip39'

type TokenPair = {
  accessToken: string
  refreshToken: string
  expiresAt: number
}

const ACCESS_TOKEN_KEY = 'qrypta-jwt'
const REFRESH_TOKEN_KEY = 'qrypta-refresh-token'
const EXPIRES_AT_KEY = 'qrypta-jwt-exp'
const IDENTITY_KEY = 'qrypta-identity-mnemonic'

function toB64Url(data: string) {
  return btoa(data).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '')
}

function buildToken(payload: Record<string, string | number>) {
  const header = toB64Url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = toB64Url(JSON.stringify(payload))
  const signature = toB64Url(crypto.randomUUID())
  return `${header}.${body}.${signature}`
}

function nowMs() {
  return Date.now()
}

function persist(pair: TokenPair) {
  localStorage.setItem(ACCESS_TOKEN_KEY, pair.accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, pair.refreshToken)
  localStorage.setItem(EXPIRES_AT_KEY, String(pair.expiresAt))
}

function clearPersisted() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(EXPIRES_AT_KEY)
}

export function registerLocalIdentity() {
  const mnemonic = bip39.generateMnemonic(256)
  localStorage.setItem(IDENTITY_KEY, mnemonic)
  return mnemonic
}

export function loginWithMnemonic(mnemonicCandidate: string) {
  const mnemonic = mnemonicCandidate.trim().toLowerCase().replace(/\s+/g, ' ')
  if (!bip39.validateMnemonic(mnemonic)) {
    throw new Error('Mnemonic BIP-39 invalida')
  }

  localStorage.setItem(IDENTITY_KEY, mnemonic)

  const expiresAt = nowMs() + 15 * 60 * 1000
  const accessToken = buildToken({ sub: 'qrypta-web-user', scope: 'chat', exp: Math.floor(expiresAt / 1000) })
  const refreshToken = buildToken({ sub: 'qrypta-web-user', scope: 'refresh', iat: Math.floor(nowMs() / 1000) })

  const pair = { accessToken, refreshToken, expiresAt }
  persist(pair)
  return pair
}

export function getStoredAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY) ?? ''
}

export function getStoredRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY) ?? ''
}

export function refreshAccessToken() {
  const refreshToken = getStoredRefreshToken()
  if (!refreshToken) {
    throw new Error('No hay refresh token para renovar sesion')
  }

  const expiresAt = nowMs() + 15 * 60 * 1000
  const accessToken = buildToken({ sub: 'qrypta-web-user', scope: 'chat', exp: Math.floor(expiresAt / 1000) })
  const pair = { accessToken, refreshToken, expiresAt }
  persist(pair)
  return pair
}

export function logoutSession() {
  clearPersisted()
}

export async function registerWebAuthnCredential() {
  if (typeof window === 'undefined' || !window.PublicKeyCredential || !navigator.credentials) {
    throw new Error('WebAuthn no soportado en este navegador')
  }

  const challenge = crypto.getRandomValues(new Uint8Array(32))
  const userId = crypto.getRandomValues(new Uint8Array(32))

  await navigator.credentials.create({
    publicKey: {
      rp: { name: 'Qrypta Web', id: window.location.hostname || 'localhost' },
      user: {
        id: userId,
        name: 'qrypta-web-user',
        displayName: 'Qrypta Web User',
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

  localStorage.setItem('qrypta-webauthn-enabled', 'true')
}
