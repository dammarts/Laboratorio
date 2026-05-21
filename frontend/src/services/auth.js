import api from './api'

export const login = async (email, password) => {
  const { data } = await api.post('/auth/login', { email, password })
  localStorage.setItem('token', data.access_token)
  return data
}

export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('usuario')
}

export const getMe = async () => {
  const { data } = await api.get('/usuarios/me')
  localStorage.setItem('usuario', JSON.stringify(data))
  return data
}

export const getCachedUsuario = () => {
  try { return JSON.parse(localStorage.getItem('usuario')) } catch { return null }
}

export const getToken = () => localStorage.getItem('token')
export const isAuthenticated = () => !!getToken()