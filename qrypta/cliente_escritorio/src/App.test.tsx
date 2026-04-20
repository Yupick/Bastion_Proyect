import { render, screen } from '@testing-library/react'
import { describe, expect, test } from 'vitest'
import { App } from './App'

describe('Cliente escritorio', () => {
  test('renderiza el título principal', () => {
    render(<App />)
    expect(screen.getByText('Cliente Escritorio')).toBeInTheDocument()
  })

  test('muestra sección de Drag and Drop', () => {
    render(<App />)
    expect(screen.getByText('Drag and Drop')).toBeInTheDocument()
  })
})
