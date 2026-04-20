import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, test } from 'vitest'
import App from './App'

describe('Admin dashboard web', () => {
  test('muestra autenticación inicial', () => {
    render(<App />)
    expect(screen.getByText('Ingreso administrativo')).toBeInTheDocument()
  })

  test('permite ingresar con código demo 2FA', async () => {
    render(<App />)
    fireEvent.change(screen.getByPlaceholderText('123456'), { target: { value: '123456' } })
    fireEvent.click(screen.getByText('Validar sesión'))
    expect(await screen.findByText('Centro de Control')).toBeInTheDocument()
  })
})
