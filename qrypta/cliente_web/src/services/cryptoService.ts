const SESSION_KEY_ID = 'qrypta-session-key'

export async function getOrCreateSessionKey(): Promise<CryptoKey> {
  const existing = sessionStorage.getItem(SESSION_KEY_ID)
  if (existing) {
    const raw = Uint8Array.from(atob(existing), (char) => char.charCodeAt(0))
    return crypto.subtle.importKey('raw', raw, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt'])
  }

  const raw = crypto.getRandomValues(new Uint8Array(32))
  sessionStorage.setItem(SESSION_KEY_ID, btoa(String.fromCharCode(...raw)))
  return crypto.subtle.importKey('raw', raw, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt'])
}

export async function encryptMessage(clearText: string): Promise<string> {
  const key = await getOrCreateSessionKey()
  const nonce = crypto.getRandomValues(new Uint8Array(12))
  const cipherBuffer = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: nonce },
    key,
    new TextEncoder().encode(clearText),
  )

  const payload = {
    nonce: btoa(String.fromCharCode(...nonce)),
    cipher: btoa(String.fromCharCode(...new Uint8Array(cipherBuffer))),
  }

  return btoa(JSON.stringify(payload))
}

export async function decryptMessage(payloadB64: string): Promise<string> {
  const payload = JSON.parse(atob(payloadB64)) as { nonce: string; cipher: string }
  const key = await getOrCreateSessionKey()
  const nonce = Uint8Array.from(atob(payload.nonce), (char) => char.charCodeAt(0))
  const cipher = Uint8Array.from(atob(payload.cipher), (char) => char.charCodeAt(0))

  const clearBuffer = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: nonce },
    key,
    cipher,
  )

  return new TextDecoder().decode(clearBuffer)
}
