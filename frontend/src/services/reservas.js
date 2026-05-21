import api from './api'

// GET /reservas/
export const getReservas = (params = {}) =>
  api.get('/reservas/', { params }).then((r) => r.data)
// params opcionales: { laboratorio_id, usuario_creador_id, estado, fecha_desde, fecha_hasta }
// estado: 'ACTIVA' | 'CANCELADA' | 'REPROGRAMADA'

// GET /reservas/{id}
export const getReserva = (id) =>
  api.get(`/reservas/${id}`).then((r) => r.data)

// POST /reservas/
export const crearReserva = (data) =>
  api.post('/reservas/', data).then((r) => r.data)
// data: { laboratorio_id, curso, fecha, hora_inicio, hora_fin }
// fecha: 'YYYY-MM-DD' | hora_inicio/hora_fin: 'HH:MM:SS'

// PATCH /reservas/{id}/cancelar
export const cancelarReserva = (id, motivo) =>
  api.patch(`/reservas/${id}/cancelar`, { motivo }).then((r) => r.data)
// motivo: string (1-500 chars)

// PATCH /reservas/{id}/reprogramar
export const reprogramarReserva = (id, data) =>
  api.patch(`/reservas/${id}/reprogramar`, data).then((r) => r.data)
// data: { fecha, hora_inicio, hora_fin }
