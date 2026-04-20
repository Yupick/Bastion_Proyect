import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, expect, test, beforeEach } from 'vitest'
import App from './App'
import { useUiStore } from './store/uiStore'

function renderWithProviders() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  localStorage.clear()
  useUiStore.setState({ activeContactId: 'c1', sidebarOpen: true })
})

describe('Cliente web', () => {
  test('renderiza cabecera principal', () => {
    renderWithProviders()
    expect(screen.getByText('Mensajeria Segura')).toBeInTheDocument()
  })

  test('muestra el panel lateral de contactos', () => {
    renderWithProviders()
    expect(screen.getByRole('heading', { name: 'Contactos' })).toBeInTheDocument()
  })

  test('navega a la sección Ajustes', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    expect(screen.getByRole('heading', { name: 'Config panel' })).toBeInTheDocument()
  })

  test('navega a la sección Dispositivos', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Dispositivos' }))
    expect(screen.getByRole('heading', { name: 'Dispositivos enlazados' })).toBeInTheDocument()
  })

  test('navega a la sección Contactos', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Contactos' }))
    expect(screen.getByRole('heading', { name: 'Resumen de contactos' })).toBeInTheDocument()
  })

  test('vuelve a la sección Chats desde Ajustes', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    fireEvent.click(screen.getByRole('button', { name: 'Chats' }))
    expect(screen.getByText('Canal cifrado')).toBeInTheDocument()
  })

  test('registro local genera mnemonic en sección Ajustes', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    fireEvent.click(screen.getByRole('button', { name: 'Registro local' }))
    expect(screen.getByText(/Mnemonic generada:/)).toBeInTheDocument()
  })

  test('login con mnemonic inválida muestra error', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    fireEvent.click(screen.getByRole('button', { name: 'Login BIP-39' }))
    expect(screen.getByText(/Error de login|Mnemonic BIP-39 invalida/)).toBeInTheDocument()
  })

  test('login correcto con mnemonic válida marca sesión autenticada', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    // Primero registrar para obtener mnemonic
    fireEvent.click(screen.getByRole('button', { name: 'Registro local' }))
    const textoMnemonic = screen.getByText(/Mnemonic generada:/).textContent ?? ''
    const mnemonic = textoMnemonic.replace('Mnemonic generada: ', '').trim()
    // Login con mnemonic generada
    const input = screen.getByPlaceholderText('Ingresa 12 o 24 palabras')
    fireEvent.change(input, { target: { value: mnemonic } })
    fireEvent.click(screen.getByRole('button', { name: 'Login BIP-39' }))
    expect(screen.getAllByText('Sesion autenticada').length).toBeGreaterThan(0)
  })

  test('cierre de sesión desde Ajustes', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar sesion' }))
    expect(screen.getByText('Sesion cerrada')).toBeInTheDocument()
  })

  test('refresh JWT desde Ajustes (sin sesión muestra error)', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    fireEvent.click(screen.getByRole('button', { name: 'Refresh JWT' }))
    expect(screen.getByText(/Error renovando token|No hay refresh token/)).toBeInTheDocument()
  })

  test('typing en textarea muestra indicador de escritura', async () => {
    renderWithProviders()
    const textarea = screen.getByPlaceholderText('Escribe un mensaje seguro...')
    fireEvent.change(textarea, { target: { value: 'probando' } })
    expect(screen.getByText('Escribiendo mensaje cifrado...')).toBeInTheDocument()
  })

  test('agregar emoji inserta el carácter en el textarea', () => {
    renderWithProviders()
    const textarea = screen.getByPlaceholderText('Escribe un mensaje seguro...')
    fireEvent.click(screen.getByRole('button', { name: '🔐' }))
    expect((textarea as HTMLTextAreaElement).value).toBe('🔐')
  })

  test('enviar mensaje lo agrega a la lista', async () => {
    renderWithProviders()
    const textarea = screen.getByPlaceholderText('Escribe un mensaje seguro...')
    fireEvent.change(textarea, { target: { value: 'Mensaje de test' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar' }))
    await waitFor(() => {
      expect(screen.getByText('Mensaje de test')).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  test('cambiar URL WebSocket en sección Dispositivos', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Dispositivos' }))
    const input = screen.getByDisplayValue('ws://localhost:8000/ws')
    fireEvent.change(input, { target: { value: 'ws://servidor.local:9000/ws' } })
    expect((input as HTMLInputElement).value).toBe('ws://servidor.local:9000/ws')
  })

  test('toggle privacidad alta en Ajustes', () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    const checkboxes = screen.getAllByRole('checkbox')
    const privacidad = checkboxes[0]
    fireEvent.click(privacidad)
    expect((privacidad as HTMLInputElement).checked).toBe(false)
  })

  test('Activar Push muestra estado (sin soporte en jsdom)', async () => {
    renderWithProviders()
    fireEvent.click(screen.getByRole('button', { name: 'Ajustes' }))
    fireEvent.click(screen.getByRole('button', { name: 'Activar Push' }))
    // En jsdom Notification no está disponible
    await waitFor(() => {
      expect(screen.getByText(/Push no soportado|Push habilitado|Push sin configurar/)).toBeInTheDocument()
    })
  })
})
