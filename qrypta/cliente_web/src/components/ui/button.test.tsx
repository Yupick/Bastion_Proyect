import { describe, expect, test } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Button } from './button'

describe('Button component', () => {
  test('renderiza con texto correcto', () => {
    render(<Button>Enviar</Button>)
    expect(screen.getByRole('button', { name: 'Enviar' })).toBeInTheDocument()
  })

  test('aplica clases de variante secondary', () => {
    render(<Button variant="secondary">Cancelar</Button>)
    const btn = screen.getByRole('button', { name: 'Cancelar' })
    expect(btn.className).toContain('bg-emerald-50')
  })

  test('aplica clases de tamaño sm', () => {
    render(<Button size="sm">Pequeño</Button>)
    expect(screen.getByRole('button').className).toContain('h-8')
  })

  test('acepta className extra', () => {
    render(<Button className="mi-clase">Test</Button>)
    expect(screen.getByRole('button').className).toContain('mi-clase')
  })

  test('se deshabilita correctamente', () => {
    render(<Button disabled>Bloqueado</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
