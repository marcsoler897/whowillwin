import { apiFetch } from './api'

interface LoginResponse {
  token: string
  user: object
}

interface RegisterResponse {
  message?: string
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ Login: email, Password: password }),
  })
}

export async function register(
  name: string,
  email: string,
  password: string,
  prefTeamId: string
): Promise<RegisterResponse> {
  return apiFetch<RegisterResponse>('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ Prefteam_id: prefTeamId, Name: name, Email: email, Password: password }),
  })
}

/** Decodes the JWT exp claim and returns true if the token exists and has not expired. */
export function isTokenValid(): boolean {
  const token = localStorage.getItem('token')
  if (!token) return false
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return typeof payload.exp === 'number' && payload.exp * 1000 > Date.now()
  } catch {
    return false
  }
}

export function logout(): void {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}
