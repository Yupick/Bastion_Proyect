import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, test } from 'vitest'
import { cacheMessage, readCachedMessages } from './indexedDbService'

beforeEach(() => {
  // fake-indexeddb/auto restablece entre archivos; suficiente para tests independientes
})

describe('indexedDbService', () => {
  test('cacheMessage guarda y readCachedMessages recupera el mensaje', async () => {
    await cacheMessage('msg-1', 'Hola mundo', '2026-04-20T08:00:00Z')
    const mensajes = await readCachedMessages()
    const encontrado = mensajes.find((m) => m.id === 'msg-1')
    expect(encontrado).toBeDefined()
    expect(encontrado?.body).toBe('Hola mundo')
    expect(encontrado?.timestamp).toBe('2026-04-20T08:00:00Z')
  })

  test('readCachedMessages devuelve array (puede estar vacío o con datos)', async () => {
    const mensajes = await readCachedMessages()
    expect(Array.isArray(mensajes)).toBe(true)
  })

  test('cacheMessage actualiza (put) si el id ya existe', async () => {
    await cacheMessage('msg-dup', 'v1', '2026-04-20T08:00:00Z')
    await cacheMessage('msg-dup', 'v2', '2026-04-20T09:00:00Z')
    const mensajes = await readCachedMessages()
    const encontrados = mensajes.filter((m) => m.id === 'msg-dup')
    expect(encontrados).toHaveLength(1)
    expect(encontrados[0].body).toBe('v2')
  })
})
