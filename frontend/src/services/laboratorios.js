import api from './api'

// GET /laboratorios/ — no requiere auth
export const getLaboratorios = (params = {}) =>
  api.get('/laboratorios/', { params }).then((r) => r.data)
// params opcionales: { skip, limit }

// GET /laboratorios/{id}
export const getLaboratorio = (id) =>
  api.get(`/laboratorios/${Number(id)}`).then((r) => r.data)

// POST /laboratorios/
export const crearLaboratorio = (data) =>
  api.post('/laboratorios/', data).then((r) => r.data)
// data: { nombre, ubicacion, capacidad_maxima, recursos_disponibles?, estado? }

// PUT /laboratorios/{id}
export const actualizarLaboratorio = (id, data) =>
  api.put(`/laboratorios/${Number(id)}`, data).then((r) => r.data)

// PATCH /laboratorios/{id}/estado — activa/desactiva
export const toggleEstadoLaboratorio = (id) =>
  api.patch(`/laboratorios/${Number(id)}/estado`).then((r) => r.data)
