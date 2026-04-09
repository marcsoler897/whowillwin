import { useEffect, useState } from 'react'
import './TomorrowsMatches.css'

interface Match {
  id: number
  homeTeam: { name: string }
  awayTeam: { name: string }
  utcDate: string
  status: string
}

export default function TomorrowsMatches() {
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:5081/matches')
      .then(r => r.json())
      .then(data => setMatches(data.matches ?? []))
      .finally(() => setLoading(false))
  }, [])

  return (
    <section className="tm-section">
      <h2 className="tm-title">Tomorrow's Matches</h2>
      {loading ? (
        <p className="tm-empty">Loading...</p>
      ) : matches.length === 0 ? (
        <p className="tm-empty">No matches found.</p>
      ) : (
        <ul className="tm-list">
          {matches.map(m => (
            <li key={m.id} className="tm-row">
              <span className="tm-team">{m.homeTeam.name}</span>
              <span className="tm-vs">vs</span>
              <span className="tm-team">{m.awayTeam.name}</span>
              <span className="tm-time">
                {new Date(m.utcDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
