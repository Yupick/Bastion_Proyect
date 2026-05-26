export type BackupSnapshot = {
  alias: string
  mnemonic: string
  deviceLinks: string[]
  exportedAt: string
}

function toBase64(bytes: Uint8Array) {
  return btoa(String.fromCharCode(...bytes))
}

function fromBase64(raw: string) {
  return Uint8Array.from(atob(raw), (char) => char.charCodeAt(0))
}

async function deriveKey(passphrase: string) {
  const keyMaterial = new TextEncoder().encode(`qrypta-web-backup:${passphrase}`)
  const digest = await crypto.subtle.digest('SHA-256', keyMaterial)
  return crypto.subtle.importKey('raw', digest, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt'])
}

export async function exportEncryptedBackup(snapshot: BackupSnapshot, passphrase: string) {
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

export async function importEncryptedBackup(blob: string, passphrase: string): Promise<BackupSnapshot> {
  const parsed = JSON.parse(atob(blob)) as { iv: string; ct: string }
  const key = await deriveKey(passphrase)
  const clear = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: fromBase64(parsed.iv) },
    key,
    fromBase64(parsed.ct),
  )

  return JSON.parse(new TextDecoder().decode(clear)) as BackupSnapshot
}
