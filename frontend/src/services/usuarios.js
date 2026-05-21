import api from './api'

export const getUsuarios = async () => {
  const { data } = await api.get('/usuarios/')
  return data
}

export const crearUsuario = async (datos) => {
  const { data } = await api.post('/auth/register', datos)
  return data
}
