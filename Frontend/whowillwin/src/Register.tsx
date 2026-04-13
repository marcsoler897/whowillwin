import { useState } from 'react'
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
  const [loading, setLoading] = useState(false)

  async function handleRegister() {
    setError('')
    setLoading(true)
    try {
      const res = await fetch('http://localhost:5081/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          Prefteam_id: prefTeamId,
          Name: name,
          Email: email,
          Password: password,
        }),
      })

      if (!res.ok) {
        const data = await res.json()
        setError(data.message ?? 'Registration failed')
        return
      }

      const data = await res.json()
      console.log('Registered:', data)
      alert('Registered successfully!')
      onGoToLogin()
    } catch {
      setError('Could not connect to server')
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
