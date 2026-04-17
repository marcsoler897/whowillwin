import { useState } from 'react'
import { login } from './services/authService'
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

  function validate(): string {
    if (!email.trim()) return 'Email is required'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Enter a valid email'
    if (!password) return 'Password is required'
    return ''
  }

  async function handleLogin() {
    const validationError = validate()
    if (validationError) { setError(validationError); return }

    setError('')
    setLoading(true)
    try {
      const data = await login(email, password)
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      onLoginSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not connect to server')
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
