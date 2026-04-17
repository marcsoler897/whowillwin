import { useState } from 'react'
import './App.css'
import Register from './Register'
import Login from './Login'
import Matches from './Matches'
import { isTokenValid, logout } from './services/authService'

type Page = 'home' | 'register' | 'login'

function App() {
  const [page, setPage] = useState<Page>(() => isTokenValid() ? 'home' : 'login')

  function navigate(target: Page) {
    if ((target === 'login' || target === 'register') && isTokenValid()) {
      setPage('home')
      return
    }
    setPage(target)
  }

  function handleLogout() {
    logout()
    setPage('login')
  }

  if (page === 'register') {
    return <Register onGoToLogin={() => navigate('login')} />
  }

  if (page === 'login') {
    return <Login onGoToRegister={() => navigate('register')} onLoginSuccess={() => setPage('home')} />
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
          <li>
            <a href="#" onClick={e => { e.preventDefault(); handleLogout() }}>Logout</a>
          </li>
        </ul>
      </nav>

      <main className="main-content">
        <Matches />
      </main>
    </div>
  )
}

export default App
