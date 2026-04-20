import { beforeEach, describe, expect, test } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAuth } from './useAuth'

beforeEach(() => {
  localStorage.clear()
})

describe('useAuth', () => {
  test('estado inicial sin token', () => {
    const { result } = renderHook(() => useAuth())
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.token).toBe('')
  })

  test('register crea identidad local', () => {
    const { result } = renderHook(() => useAuth())
    let mnemonic: string
    act(() => {
      mnemonic = result.current.register()
    })
    expect(mnemonic!.trim().split(/\s+/)).toHaveLength(24)
    expect(result.current.authStatus).toBe('Identidad local registrada')
  })

  test('login autentica con mnemonic valida', () => {
    const { result } = renderHook(() => useAuth())
    let mnemonic: string
    act(() => {
      mnemonic = result.current.register()
    })
    act(() => {
      result.current.login(mnemonic)
    })
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.token.length).toBeGreaterThan(0)
    expect(result.current.authStatus).toBe('Sesion autenticada')
  })

  test('logout limpia el token', () => {
    const { result } = renderHook(() => useAuth())
    act(() => {
      const mnemonic = result.current.register()
      result.current.login(mnemonic)
    })
    act(() => {
      result.current.logout()
    })
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.token).toBe('')
    expect(result.current.authStatus).toBe('Sesion cerrada')
  })

  test('refresh renueva el token', () => {
    const { result } = renderHook(() => useAuth())
    let tokenAntes: string
    act(() => {
      const mnemonic = result.current.register()
      result.current.login(mnemonic)
      tokenAntes = result.current.token
    })
    act(() => {
      result.current.refresh()
    })
    expect(result.current.token).not.toBe(tokenAntes)
    expect(result.current.authStatus).toBe('Token renovado')
  })
})
