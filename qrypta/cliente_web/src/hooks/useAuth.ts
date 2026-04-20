import { useCallback, useState } from 'react'
import {
  getStoredAccessToken,
  loginWithMnemonic,
  logoutSession,
  refreshAccessToken,
  registerLocalIdentity,
  registerWebAuthnCredential,
} from '../services/authService'

export function useAuth() {
  const [token, setToken] = useState(() => getStoredAccessToken())
  const [authStatus, setAuthStatus] = useState('Sesion sin token local')

  const register = useCallback(() => {
    const mnemonic = registerLocalIdentity()
    setAuthStatus('Identidad local registrada')
    return mnemonic
  }, [])

  const login = useCallback((mnemonic: string) => {
    const pair = loginWithMnemonic(mnemonic)
    setToken(pair.accessToken)
    setAuthStatus('Sesion autenticada')
    return pair
  }, [])

  const refresh = useCallback(() => {
    const pair = refreshAccessToken()
    setToken(pair.accessToken)
    setAuthStatus('Token renovado')
    return pair
  }, [])

  const registerWebAuthn = useCallback(async () => {
    await registerWebAuthnCredential()
    setAuthStatus('WebAuthn registrado')
  }, [])

  const logout = useCallback(() => {
    logoutSession()
    setToken('')
    setAuthStatus('Sesion cerrada')
  }, [])

  return {
    token,
    isAuthenticated: token.length > 0,
    authStatus,
    register,
    login,
    refresh,
    registerWebAuthn,
    logout,
  }
}
