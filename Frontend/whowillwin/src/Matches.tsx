import { useEffect, useState } from 'react'
import './Matches.css'

interface Season {
  id: number
  startDate: string
  endDate: string
}

interface Match {
  id: number
  homeTeam: { name: string }
  awayTeam: { name: string }
  utcDate: string
  status: string
  score: { fullTime: { home: number | null; away: number | null } }
}

const COMPETITION_ID = 2014

export default function Matches() {
  const [seasons, setSeasons] = useState<Season[]>([])
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null)
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch(`http://localhost:5081/competitions/${COMPETITION_ID}/seasons`)
      .then(r => r.json())
      .then(data => {
        const today = new Date().toISOString().slice(0, 10)
        const future: Season[] = (data.seasons ?? []).filter(
          (s: Season) => s.endDate >= today
        )
        setSeasons(future)
        if (future.length > 0) {
          const year = new Date(future[0].startDate).getFullYear()
          setSelectedSeason(year)
        }
      })
  }, [])

  useEffect(() => {
    if (selectedSeason === null) return
    setLoading(true)
    fetch(`http://localhost:5081/competitions/${COMPETITION_ID}/matches?season=${selectedSeason}`)
      .then(r => r.json())
      .then(data => setMatches(data.matches ?? []))
      .finally(() => setLoading(false))
  }, [selectedSeason])

  const played = (m: Match) => m.status === 'FINISHED'

  return (
    <section className="tm-section">
      <div className="tm-header">
        <h2 className="tm-title">Matches</h2>
        <select
          className="tm-season-select"
          value={selectedSeason ?? ''}
          onChange={e => setSelectedSeason(Number(e.target.value))}
        >
          {seasons.map(s => {
            const year = new Date(s.startDate).getFullYear()
            return (
              <option key={s.id} value={year}>
                {year}/{String(year + 1).slice(2)}
              </option>
            )
          })}
        </select>
      </div>

      {loading ? (
        <p className="tm-empty">Loading...</p>
      ) : matches.length === 0 ? (
        <p className="tm-empty">No matches found.</p>
      ) : (
        <ul className="tm-list">
          {matches.map(m => (
            <li key={m.id} className={`tm-row ${played(m) ? 'tm-played' : ''}`}>
              <span className="tm-team">{m.homeTeam.name}</span>
              {played(m) ? (
                <span className="tm-score">
                  {m.score.fullTime.home} – {m.score.fullTime.away}
                </span>
              ) : (
                <span className="tm-vs">
                  {new Date(m.utcDate).toLocaleDateString([], { day: '2-digit', month: '2-digit' })}
                </span>
              )}
              <span className="tm-team tm-team-right">{m.awayTeam.name}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
