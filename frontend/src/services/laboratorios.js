import api from './api'

const safeId = (id) => {
  const n = Number(id)
  if (!Number.isInteger(n) || n <= 0) throw new Error(`ID inválido: ${id}`)
  return n
}

// GET /laboratorios/ — no requiere auth
export const getLaboratorios = (params = {}) =>
  api.get('/laboratorios/', { params }).then((r) => r.data)
// params opcionales: { skip, limit }

// GET /laboratorios/{id}
export const getLaboratorio = (id) =>
  api.get(`/laboratorios/${safeId(id)}`).then((r) => r.data)

// POST /laboratorios/
export const crearLaboratorio = (data) =>
  api.post('/laboratorios/', data).then((r) => r.data)
// data: { nombre, ubicacion, capacidad_maxima, recursos_disponibles?, estado? }

// PUT /laboratorios/{id}
export const actualizarLaboratorio = (id, data) =>
  api.put(`/laboratorios/${safeId(id)}`, data).then((r) => r.data)

// PATCH /laboratorios/{id}/estado — activa/desactiva
export const toggleEstadoLaboratorio = (id) =>
  api.patch(`/laboratorios/${safeId(id)}/estado`).then((r) => r.data)
