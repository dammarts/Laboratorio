import { createContext, useContext, useState } from 'react'
import { login as loginService, logout as logoutService, isAuthenticated } from '../services/auth'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [autenticado, setAutenticado] = useState(isAuthenticated())
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const login = async (email, password) => {
    setCargando(true)
    setError(null)
    try {
      await loginService(email, password)
      setAutenticado(true)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Error al iniciar sesión'
      setError(msg)
      throw err
    } finally {
      setCargando(false)
    }
  }

  const logout = () => {
    logoutService()
    setAutenticado(false)
  }

  return (
    <AuthContext.Provider value={{ autenticado, login, logout, cargando, error }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
