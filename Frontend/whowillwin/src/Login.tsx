import { useState } from 'react'
import './Login.css'

interface LoginProps {
  onGoToRegister: () => void
  onLoginSuccess: () => void
}

export default function Login({ onGoToRegister, onLoginSuccess }: LoginProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleLogin() {
    setError('')
    setLoading(true)
    try {
      const res = await fetch('http://localhost:5081/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ Login: email, Password: password }),
      })

      if (!res.ok) {
        const data = await res.json()
        setError(data.message ?? 'Login failed')
        return
      }

      const data = await res.json()
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      onLoginSuccess()
    } catch {
      setError('Could not connect to server')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-sky">
        <h1 className="login-title">WhoWillWin</h1>

        <div className="login-cloud">
          <input
            className="login-input"
            type="email"
            placeholder="Gmail"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
        </div>

        <input
          className="login-input login-input-flat"
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />

        {error && <p className="login-error">{error}</p>}
      </div>

      <div className="login-hills">
        <button
          className="login-btn"
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <button className="login-link" onClick={onGoToRegister}>
          Don't have an account?
        </button>
      </div>
    </div>
  )
}
