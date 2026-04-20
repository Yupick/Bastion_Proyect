import { describe, expect, test, beforeEach } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useUiStore } from './uiStore'

beforeEach(() => {
  useUiStore.setState({ activeContactId: 'c1', sidebarOpen: true })
})

describe('uiStore', () => {
  test('estado inicial por defecto', () => {
    const { result } = renderHook(() => useUiStore())
    expect(result.current.activeContactId).toBe('c1')
    expect(result.current.sidebarOpen).toBe(true)
  })

  test('setActiveContactId actualiza el contacto activo', () => {
    const { result } = renderHook(() => useUiStore())
    act(() => {
      result.current.setActiveContactId('c3')
    })
    expect(result.current.activeContactId).toBe('c3')
  })

  test('toggleSidebar alterna entre abierto y cerrado', () => {
    const { result } = renderHook(() => useUiStore())
    act(() => {
      result.current.toggleSidebar()
    })
    expect(result.current.sidebarOpen).toBe(false)
    act(() => {
      result.current.toggleSidebar()
    })
    expect(result.current.sidebarOpen).toBe(true)
  })
})
