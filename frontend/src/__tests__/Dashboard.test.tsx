import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Dashboard from '../pages/Dashboard'

describe('Dashboard', () => {
  it('renders the Dashboard heading', () => {
    render(<Dashboard />)
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
  })
})
