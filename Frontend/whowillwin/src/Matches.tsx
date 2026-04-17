import './Matches.css'
import { useMatches, useSquad } from './hooks/useMatches'

const byPosition = (squad: { id: number; name: string; position: string }[]) => {
  const order = ['Goalkeeper', 'Defence', 'Midfield', 'Offence']
  return [...squad].sort((a, b) => order.indexOf(a.position) - order.indexOf(b.position))
}

export default function Matches() {
  const {
    seasons,
    selectedSeason,
    setSelectedSeason,
    matchdays,
    dayMatches,
    selectedMatchday,
    selectedMatch,
    setSelectedMatch,
    loading,
    error,
    isPastMatchday,
    selectMatchday,
  } = useMatches()

  const homeSquad = useSquad(selectedMatch?.homeTeam.id ?? null)
  const awaySquad = useSquad(selectedMatch?.awayTeam.id ?? null)

  const played = selectedMatch?.status === 'FINISHED'
  const seasonLabel = selectedSeason ? `${selectedSeason}/${String(selectedSeason + 1).slice(2)}` : ''

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

      {error && <p className="tm-empty">{error}</p>}

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
              onClick={() => selectMatchday(day)}
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
            {played ? (
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
        !error && <p className="tm-empty">No matches found.</p>
      )}
    </>
  )
}
