import api from './api'

export const login = async (email, password) => {
  const { data } = await api.post('/auth/login', { email, password })
  localStorage.setItem('token', data.access_token)
  return data
}

export const logout = () => {
  localStorage.removeItem('token')
}

export const getToken = () => localStorage.getItem('token')
export const isAuthenticated = () => !!getToken()