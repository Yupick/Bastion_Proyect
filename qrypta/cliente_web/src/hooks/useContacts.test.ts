import { describe, expect, test } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useContacts } from './useContacts'

describe('useContacts', () => {
  test('devuelve lista de contactos no vacía', () => {
    const { result } = renderHook(() => useContacts())
    expect(result.current.contacts.length).toBeGreaterThan(0)
  })

  test('cada contacto tiene los campos requeridos', () => {
    const { result } = renderHook(() => useContacts())
    for (const c of result.current.contacts) {
      expect(c).toHaveProperty('id')
      expect(c).toHaveProperty('nombre')
      expect(c).toHaveProperty('estado')
      expect(['online', 'offline']).toContain(c.estado)
    }
  })

  test('la lista es estable entre re-renders', () => {
    const { result, rerender } = renderHook(() => useContacts())
    const first = result.current.contacts
    rerender()
    expect(result.current.contacts).toBe(first)
  })
})
