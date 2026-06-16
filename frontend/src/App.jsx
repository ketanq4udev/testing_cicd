import { useState, useEffect } from 'react'
import './App.css'

const API = import.meta.env.VITE_API_URL || ''

function App() {
  const [items, setItems] = useState([])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchItems = async () => {
    try {
      const res = await fetch(`${API}/api/items/`)
      setItems(await res.json())
    } catch {
      setStatus('Failed to load items')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchItems() }, [])

  const addItem = async (e) => {
    e.preventDefault()
    if (!name.trim()) return
    const res = await fetch(`${API}/api/items/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description }),
    })
    if (res.ok) {
      setName('')
      setDescription('')
      setStatus('Item added!')
      fetchItems()
    } else {
      setStatus('Failed to add item')
    }
  }

  const deleteItem = async (id) => {
    await fetch(`${API}/api/items/${id}`, { method: 'DELETE' })
    fetchItems()
  }

  return (
    <div className="app">
      <header>
        <h1>CI/CD Demo App</h1>
        <p className="subtitle">FastAPI + React</p>
      </header>

      <main>
        <section className="card">
          <h2>Add Item</h2>
          <form onSubmit={addItem}>
            <input
              placeholder="Name"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
            <input
              placeholder="Description (optional)"
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
            <button type="submit">Add</button>
          </form>
          {status && <p className="status">{status}</p>}
        </section>

        <section className="card">
          <h2>Items {loading ? '…' : `(${items.length})`}</h2>
          {loading ? (
            <p>Loading...</p>
          ) : items.length === 0 ? (
            <p>No items yet.</p>
          ) : (
            <ul>
              {items.map(item => (
                <li key={item.id}>
                  <div>
                    <strong>{item.name}</strong>
                    {item.description && <span> — {item.description}</span>}
                  </div>
                  <button className="delete" onClick={() => deleteItem(item.id)}>Delete</button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
