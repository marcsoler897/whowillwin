import { useEffect, useMemo, useState } from 'react'
import { getMatches, getSeasons, getSquad, type Match, type Player, type Season } from '../services/matchService'

const COMPETITION_ID = 2014

export function useMatches() {
  const [seasons, setSeasons] = useState<Season[]>([])
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null)
  const [matches, setMatches] = useState<Match[]>([])
  const [selectedMatchday, setSelectedMatchday] = useState<number | null>(null)
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getSeasons(COMPETITION_ID)
      .then(all => {
        const today = new Date().toISOString().slice(0, 10)
        const future = all.filter(s => s.endDate >= today)
        setSeasons(future)
        if (future.length > 0)
          setSelectedSeason(new Date(future[0].startDate).getFullYear())
      })
      .catch(() => setError('Could not load seasons'))
  }, [])

  useEffect(() => {
    if (selectedSeason === null) return
    setLoading(true)
    setError('')
    setSelectedMatchday(null)
    setSelectedMatch(null)
    getMatches(COMPETITION_ID, selectedSeason)
      .then(ms => {
        setMatches(ms)
        const firstUpcoming = ms.find(m => m.status !== 'FINISHED')
        const autoDay = firstUpcoming ? firstUpcoming.matchday : (ms[ms.length - 1]?.matchday ?? null)
        setSelectedMatchday(autoDay)
        setSelectedMatch(firstUpcoming ?? ms[ms.length - 1] ?? null)
      })
      .catch(() => setError('Could not load matches'))
      .finally(() => setLoading(false))
  }, [selectedSeason])

  const matchdays = useMemo(
    () => [...new Set(matches.map(m => m.matchday))].sort((a, b) => a - b),
    [matches]
  )

  const dayMatches = matches.filter(m => m.matchday === selectedMatchday)

  const isPastMatchday = (day: number) =>
    matches.filter(m => m.matchday === day).every(m => m.status === 'FINISHED')

  function selectMatchday(day: number) {
    setSelectedMatchday(day)
    const first =
      matches.find(m => m.matchday === day && m.status !== 'FINISHED') ??
      matches.find(m => m.matchday === day) ??
      null
    setSelectedMatch(first)
  }

  return {
    seasons,
    selectedSeason,
    setSelectedSeason,
    matches,
    matchdays,
    dayMatches,
    selectedMatchday,
    selectedMatch,
    setSelectedMatch,
    loading,
    error,
    isPastMatchday,
    selectMatchday,
  }
}

export function useSquad(teamId: number | null) {
  const [squad, setSquad] = useState<Player[]>([])

  useEffect(() => {
    if (teamId === null) return
    setSquad([])
    getSquad(teamId).catch(() => {})
      .then(players => { if (players) setSquad(players) })
  }, [teamId])

  return squad
}
