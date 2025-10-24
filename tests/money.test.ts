import { describe, it, expect } from 'vitest'
import { currency } from '../lib/money'

describe('currency', () => {
  it('formats cents as BRL', () => {
    expect(currency(12345)).toContain('R$')
  })
})
