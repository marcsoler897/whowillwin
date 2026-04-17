import { apiFetch } from './api'

export interface Season {
  id: number
  startDate: string
  endDate: string
}

export interface Match {
  id: number
  homeTeam: { id: number; name: string }
  awayTeam: { id: number; name: string }
  utcDate: string
  status: string
  matchday: number
  score: { fullTime: { home: number | null; away: number | null } }
}

export interface Player {
  id: number
  name: string
  position: string
}

export async function getSeasons(competitionId: number): Promise<Season[]> {
  const data = await apiFetch<{ seasons: Season[] }>(`/competitions/${competitionId}/seasons`)
  return data.seasons ?? []
}

export async function getMatches(competitionId: number, season: number): Promise<Match[]> {
  const data = await apiFetch<{ matches: Match[] }>(
    `/competitions/${competitionId}/matches?season=${season}`
  )
  return data.matches ?? []
}

export async function getSquad(teamId: number): Promise<Player[]> {
  const data = await apiFetch<{ squad: Player[] }>(`/teams/${teamId}`)
  return data.squad ?? []
}

export async function getTomorrowsMatches(): Promise<Match[]> {
  const data = await apiFetch<{ matches: Match[] }>('/matches')
  return data.matches ?? []
}
