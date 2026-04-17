import { useState } from 'react'
import { register } from './services/authService'
import './Register.css'

interface RegisterProps {
  onGoToLogin: () => void
}

export default function Register({ onGoToLogin }: RegisterProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [prefTeamId, setPrefTeamId] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  function validate(): string {
    if (!name.trim()) return 'Name is required'
    if (!email.trim()) return 'Email is required'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Enter a valid email'
    if (!password) return 'Password is required'
    if (password.length < 6) return 'Password must be at least 6 characters'
    return ''
  }

  async function handleRegister() {
    const validationError = validate()
    if (validationError) { setError(validationError); return }

    setError('')
    setSuccess('')
    setLoading(true)
    try {
      await register(name, email, password, prefTeamId)
      setSuccess('Registered successfully! Redirecting to login...')
      setTimeout(onGoToLogin, 1500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not connect to server')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-page">
      <div className="register-sky">
        <h1 className="register-title">WhoWillWin</h1>

        <div className="register-cloud">
          <input
            className="register-input"
            type="text"
            placeholder="Name"
            value={name}
            onChange={e => setName(e.target.value)}
          />
        </div>

        <input
          className="register-input register-input-flat"
          type="email"
          placeholder="Gmail"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />

        <input
          className="register-input register-input-flat"
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />

        {error && <p className="register-error">{error}</p>}
        {success && <p className="register-success">{success}</p>}
      </div>

      <div className="register-hills">
        <input
          className="register-input register-input-team"
          type="text"
          placeholder="Prefered Team (ID)"
          value={prefTeamId}
          onChange={e => setPrefTeamId(e.target.value)}
        />

        <button
          className="register-btn"
          onClick={handleRegister}
          disabled={loading}
        >
          {loading ? 'Registering...' : 'Register'}
        </button>

        <button className="register-link" onClick={onGoToLogin}>
          Already have an account
        </button>
      </div>
    </div>
  )
}
