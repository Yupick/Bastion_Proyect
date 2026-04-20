import { beforeEach, describe, expect, test } from 'vitest'
import {
  getStoredAccessToken,
  getStoredRefreshToken,
  loginWithMnemonic,
  logoutSession,
  refreshAccessToken,
  registerLocalIdentity,
} from './authService'

beforeEach(() => {
  localStorage.clear()
})

describe('authService', () => {
  test('registerLocalIdentity genera mnemonic de 24 palabras', () => {
    const mnemonic = registerLocalIdentity()
    const palabras = mnemonic.trim().split(/\s+/)
    expect(palabras).toHaveLength(24)
    expect(localStorage.getItem('qrypta-identity-mnemonic')).toBe(mnemonic)
  })

  test('loginWithMnemonic almacena tokens con mnemonic valida', () => {
    const mnemonic = registerLocalIdentity()
    const pair = loginWithMnemonic(mnemonic)
    expect(pair.accessToken).toBeTruthy()
    expect(pair.refreshToken).toBeTruthy()
    expect(pair.expiresAt).toBeGreaterThan(Date.now())
    expect(getStoredAccessToken()).toBe(pair.accessToken)
    expect(getStoredRefreshToken()).toBe(pair.refreshToken)
  })

  test('loginWithMnemonic lanza error con mnemonic invalida', () => {
    expect(() => loginWithMnemonic('palabra invalida')).toThrow('Mnemonic BIP-39 invalida')
  })

  test('refreshAccessToken renueva el access token', () => {
    const mnemonic = registerLocalIdentity()
    const first = loginWithMnemonic(mnemonic)
    const renewed = refreshAccessToken()
    expect(renewed.accessToken).toBeTruthy()
    expect(renewed.accessToken).not.toBe(first.accessToken)
    expect(getStoredAccessToken()).toBe(renewed.accessToken)
  })

  test('refreshAccessToken lanza error sin refresh token previo', () => {
    expect(() => refreshAccessToken()).toThrow('No hay refresh token para renovar sesion')
  })

  test('logoutSession limpia los tokens del localStorage', () => {
    const mnemonic = registerLocalIdentity()
    loginWithMnemonic(mnemonic)
    logoutSession()
    expect(getStoredAccessToken()).toBe('')
    expect(getStoredRefreshToken()).toBe('')
  })
})
