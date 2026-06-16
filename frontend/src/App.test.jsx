import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import App from './App'

const mockItems = [
  { id: 1, name: 'Item One', description: 'First' },
  { id: 2, name: 'Item Two', description: 'Second' },
]

beforeEach(() => {
  global.fetch = vi.fn((url, opts) => {
    if (!opts || opts.method === 'GET' || !opts.method) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(mockItems) })
    }
    if (opts.method === 'POST') {
      const body = JSON.parse(opts.body)
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ id: 99, ...body }),
      })
    }
    if (opts.method === 'DELETE') {
      return Promise.resolve({ ok: true })
    }
  })
})

describe('App', () => {
  it('renders the heading', async () => {
    render(<App />)
    expect(screen.getByText('CI/CD Demo App')).toBeInTheDocument()
  })

  it('loads and displays items', async () => {
    render(<App />)
    await waitFor(() => expect(screen.getByText('Item One')).toBeInTheDocument())
    expect(screen.getByText('Item Two')).toBeInTheDocument()
  })

  it('adds a new item', async () => {
    render(<App />)
    await waitFor(() => screen.getByText('Item One'))
    fireEvent.change(screen.getByPlaceholderText('Name'), { target: { value: 'New Item' } })
    fireEvent.click(screen.getByText('Add'))
    await waitFor(() => expect(screen.getByText('Item added!')).toBeInTheDocument())
  })
})
