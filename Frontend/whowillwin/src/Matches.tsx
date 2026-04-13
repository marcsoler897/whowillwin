import { useEffect, useMemo, useState } from 'react'
import './Matches.css'

interface Season {
  id: number
  startDate: string
  endDate: string
}

interface Match {
  id: number
  homeTeam: { id: number; name: string }
  awayTeam: { id: number; name: string }
  utcDate: string
  status: string
  matchday: number
  score: { fullTime: { home: number | null; away: number | null } }
}

interface Player {
  id: number
  name: string
  position: string
}

const COMPETITION_ID = 2014

function useSquad(teamId: number | null) {
  const [squad, setSquad] = useState<Player[]>([])
  useEffect(() => {
    if (teamId === null) return
    setSquad([])
    fetch(`http://localhost:5081/teams/${teamId}`)
      .then(r => r.json())
      .then(data => setSquad(data.squad ?? []))
  }, [teamId])
  return squad
}

export default function Matches() {
  const [seasons, setSeasons] = useState<Season[]>([])
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null)
  const [matches, setMatches] = useState<Match[]>([])
  const [selectedMatchday, setSelectedMatchday] = useState<number | null>(null)
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null)
  const [loading, setLoading] = useState(false)

  const homeSquad = useSquad(selectedMatch?.homeTeam.id ?? null)
  const awaySquad = useSquad(selectedMatch?.awayTeam.id ?? null)

  useEffect(() => {
    fetch(`http://localhost:5081/competitions/${COMPETITION_ID}/seasons`)
      .then(r => r.json())
      .then(data => {
        const today = new Date().toISOString().slice(0, 10)
        const future: Season[] = (data.seasons ?? []).filter((s: Season) => s.endDate >= today)
        setSeasons(future)
        if (future.length > 0)
          setSelectedSeason(new Date(future[0].startDate).getFullYear())
      })
  }, [])

  useEffect(() => {
    if (selectedSeason === null) return
    setLoading(true)
    setSelectedMatchday(null)
    setSelectedMatch(null)
    fetch(`http://localhost:5081/competitions/${COMPETITION_ID}/matches?season=${selectedSeason}`)
      .then(r => r.json())
      .then(data => {
        const ms: Match[] = data.matches ?? []
        setMatches(ms)
        const firstUpcoming = ms.find(m => m.status !== 'FINISHED')
        const autoDay = firstUpcoming ? firstUpcoming.matchday : ms[ms.length - 1]?.matchday ?? null
        setSelectedMatchday(autoDay)
        setSelectedMatch(firstUpcoming ?? ms[ms.length - 1] ?? null)
      })
      .finally(() => setLoading(false))
  }, [selectedSeason])

  const matchdays = useMemo(
    () => [...new Set(matches.map(m => m.matchday))].sort((a, b) => a - b),
    [matches]
  )

  const isPastMatchday = (day: number) =>
    matches.filter(m => m.matchday === day).every(m => m.status === 'FINISHED')

  const dayMatches = matches.filter(m => m.matchday === selectedMatchday)

  const handleDayClick = (day: number) => {
    setSelectedMatchday(day)
    const first = matches.find(m => m.matchday === day && m.status !== 'FINISHED')
      ?? matches.find(m => m.matchday === day)
      ?? null
    setSelectedMatch(first)
  }

  const played = (m: Match) => m.status === 'FINISHED'
  const seasonLabel = selectedSeason ? `${selectedSeason}/${String(selectedSeason + 1).slice(2)}` : ''

  const byPosition = (squad: Player[]) => {
    const order = ['Goalkeeper', 'Defence', 'Midfield', 'Offence']
    return [...squad].sort((a, b) => order.indexOf(a.position) - order.indexOf(b.position))
  }

  return (
    <>
      <h1 className="match-title">Match Predictor</h1>

      <div className="season-row">
        <select
          className="tm-season-select"
          value={selectedSeason ?? ''}
          onChange={e => setSelectedSeason(Number(e.target.value))}
        >
          {seasons.map(s => {
            const year = new Date(s.startDate).getFullYear()
            return <option key={s.id} value={year}>{year}/{String(year + 1).slice(2)}</option>
          })}
        </select>
        <span className="season-label-text">Season {seasonLabel}</span>
      </div>

      {!loading && matchdays.length > 0 && (
        <div className="tm-matchdays">
          {matchdays.map(day => (
            <button
              key={day}
              className={[
                'tm-day-btn',
                selectedMatchday === day ? 'tm-day-active' : '',
                isPastMatchday(day) ? 'tm-day-past' : 'tm-day-future',
              ].join(' ')}
              onClick={() => handleDayClick(day)}
            >
              {day}
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <p className="tm-empty">Loading...</p>
      ) : selectedMatch ? (
        <div className="match-grid">
          <div className="team-col team-left">
            <h2 className="team-name">{selectedMatch.homeTeam.name}</h2>
            {byPosition(homeSquad).map(p => (
              <p key={p.id} className="player">{p.name}</p>
            ))}
          </div>

          <div className="match-center">
            <p className="match-date-inline">
              {new Date(selectedMatch.utcDate).toLocaleDateString([], { day: '2-digit', month: '2-digit', year: 'numeric' })}
            </p>
            {played(selectedMatch) ? (
              <p className="match-score">
                {selectedMatch.score.fullTime.home} – {selectedMatch.score.fullTime.away}
              </p>
            ) : (
              <p className="match-time">
                {new Date(selectedMatch.utcDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            )}
            {dayMatches.length > 1 && (
              <div className="match-other-list">
                {dayMatches.filter(m => m.id !== selectedMatch.id).map(m => (
                  <button key={m.id} className="match-other-btn" onClick={() => setSelectedMatch(m)}>
                    {m.homeTeam.name} vs {m.awayTeam.name}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="team-col team-right">
            <h2 className="team-name">{selectedMatch.awayTeam.name}</h2>
            {byPosition(awaySquad).map(p => (
              <p key={p.id} className="player">{p.name}</p>
            ))}
          </div>
        </div>
      ) : (
        <p className="tm-empty">No matches found.</p>
      )}
    </>
  )
}
