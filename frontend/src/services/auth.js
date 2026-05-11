import api from './api'

// NOTA: /auth/login usa OAuth2 Password Bearer (form-urlencoded, no JSON)
// Este endpoint lo implementa Daniel en feature/auth

export const login = async (username, password) => {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  const { data } = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })

  localStorage.setItem('token', data.access_token)
  return data
}

export const logout = () => {
  localStorage.removeItem('token')
}

export const getToken = () => localStorage.getItem('token')
export const isAuthenticated = () => !!getToken()
