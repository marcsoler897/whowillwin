import { useState } from 'react'
import './App.css'
import Register from './Register'
import TomorrowsMatches from './TomorrowsMatches'

function App() {
  const [page, setPage] = useState<'home' | 'register'>('home')

  if (page === 'register') {
    return <Register onBack={() => setPage('home')} />
  }

  return (
    <div className="page">
      <nav className="navbar">
        <div className="nav-logo">
          <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v18M3 12h18M5.636 5.636l12.728 12.728M18.364 5.636L5.636 18.364" />
          </svg>
          <span>WhoWillWin</span>
        </div>
        <ul className="nav-links">
          <li><a href="#" className="active">Home</a></li>
          <li><a href="#">Record</a></li>
          <li><a href="#">Login</a></li>
          <li><a href="#" onClick={e => { e.preventDefault(); setPage('register') }}>Register</a></li>
        </ul>
      </nav>

      <main className="main-content">
        <p className="match-date">23/03/2026</p>
        <h1 className="match-title">Match Predictor</h1>
        <p className="season-label">Season x</p>

        <div className="match-grid">
          <div className="team-col team-left">
            <h2 className="team-name">Team A</h2>
            <p className="player">PLAYERS</p>
            <p className="player">PLAYERS</p>
            <p className="injured">INJURED PLAYERS</p>
          </div>

          <div className="match-center">
            <p className="match-option">Match Prefered Team vs next team</p>
            <p className="match-option">B. See other matches</p>
          </div>

          <div className="team-col team-right">
            <h2 className="team-name">Team B</h2>
            <p className="player">PLAYERS</p>
            <p className="player">PLAYERS</p>
            <p className="injured">INJURED PLAYERS</p>
          </div>
        </div>

        <TomorrowsMatches />
      </main>
    </div>
  )
}

export default App
