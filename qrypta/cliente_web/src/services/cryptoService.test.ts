import { describe, expect, test } from 'vitest'
import { decryptMessage, encryptMessage } from './cryptoService'

describe('cryptoService', () => {
  test('encryptMessage produce una cadena base64', async () => {
    const encrypted = await encryptMessage('hola mundo')
    expect(typeof encrypted).toBe('string')
    expect(encrypted.length).toBeGreaterThan(0)
    // Debe ser base64 decodable
    const decoded = JSON.parse(atob(encrypted))
    expect(decoded).toHaveProperty('nonce')
    expect(decoded).toHaveProperty('cipher')
  })

  test('decryptMessage recupera el texto original', async () => {
    const texto = 'Mensaje secreto Qrypta'
    const encrypted = await encryptMessage(texto)
    const decrypted = await decryptMessage(encrypted)
    expect(decrypted).toBe(texto)
  })

  test('mensajes distintos generan ciphertexts distintos', async () => {
    const a = await encryptMessage('alpha')
    const b = await encryptMessage('beta')
    expect(a).not.toBe(b)
  })

  test('mismo texto encriptado dos veces produce IVs distintos', async () => {
    const texto = 'repetido'
    const a = await encryptMessage(texto)
    const b = await encryptMessage(texto)
    const da = JSON.parse(atob(a))
    const db = JSON.parse(atob(b))
    expect(da.nonce).not.toBe(db.nonce)
  })
})
