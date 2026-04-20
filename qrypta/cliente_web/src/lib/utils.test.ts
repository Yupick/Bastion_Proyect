import { describe, expect, test } from 'vitest'
import { cn } from './utils'

describe('cn (classname merge)', () => {
  test('combina clases simples', () => {
    expect(cn('foo', 'bar')).toBe('foo bar')
  })

  test('resuelve conflictos Tailwind (tailwind-merge)', () => {
    expect(cn('text-sm', 'text-lg')).toBe('text-lg')
    expect(cn('p-2', 'p-4')).toBe('p-4')
  })

  test('filtra valores falsy', () => {
    expect(cn('foo', false && 'bar', undefined, null, 'baz')).toBe('foo baz')
  })

  test('acepta objetos clsx', () => {
    expect(cn({ active: true, hidden: false })).toBe('active')
  })

  test('sin argumentos devuelve cadena vacía', () => {
    expect(cn()).toBe('')
  })
})
