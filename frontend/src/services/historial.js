import api from './api'

// GET /reservas/historial
export const getHistorial = (params = {}) =>
  api.get('/reservas/historial', { params }).then((r) => r.data)
// params opcionales: { reserva_id, laboratorio_id, usuario_id, fecha_desde, fecha_hasta }
// Respuesta: [{ historial_id, reserva_id, usuario_id, accion, detalle, fecha }]
