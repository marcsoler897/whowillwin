import { useState } from 'react'
import './Matches.css'
import { useMatches, useSquad } from './hooks/useMatches'
import { getPrediction } from './services/matchService'
import type { Prediction } from './types/prediction'

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

  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [predLoading, setPredLoading] = useState(false)
  const [predError, setPredError] = useState<string | null>(null)

  async function handlePredict() {
    if (!selectedMatch) return
    setPrediction(null)
    setPredError(null)
    setPredLoading(true)
    try {
      const result = await getPrediction(selectedMatch.homeTeam.id, selectedMatch.awayTeam.id)
      setPrediction(result)
    } catch (e) {
      setPredError(e instanceof Error ? e.message : 'Prediction failed')
    } finally {
      setPredLoading(false)
    }
  }

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

            <button className="predict-btn" onClick={handlePredict} disabled={predLoading}>
              {predLoading ? 'Predicting…' : 'Predict'}
            </button>

            {predError && <p className="predict-error">{predError}</p>}

            {prediction && (
              <div className="predict-result">
                <span className="predict-pct">{prediction.homeWinChance}%</span>
                <span className="predict-label">vs</span>
                <span className="predict-pct">{prediction.awayWinChance}%</span>
                <p className="predict-elo">ELO: {prediction.homeElo} – {prediction.awayElo}</p>
              </div>
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
