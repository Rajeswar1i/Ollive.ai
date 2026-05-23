import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'

function Nav() {
  const location = useLocation()
  const linkStyle = (path: string) => ({
    color: location.pathname === path ? '#60a5fa' : '#94a3b8',
    textDecoration: 'none',
    fontSize: 14,
    fontWeight: 600,
    letterSpacing: '0.3px',
    paddingBottom: 2,
    borderBottom: location.pathname === path ? '2px solid #60a5fa' : '2px solid transparent',
  })
  return (
    <nav style={{
      padding: '12px 24px',
      borderBottom: '2px solid #1e293b',
      display: 'flex',
      gap: 24,
      background: '#0a0f1e',
      alignItems: 'center',
    }}>
      <span style={{ color: '#f1f5f9', fontWeight: 700, fontSize: 15, marginRight: 8, letterSpacing: '0.5px' }}>
        Ollive AI
      </span>
      <Link to="/" style={linkStyle('/')}>Chat</Link>
      <Link to="/dashboard" style={linkStyle('/dashboard')}>Dashboard</Link>
    </nav>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
