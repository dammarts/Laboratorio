import api from './api'

const safeId = (id) => {
  const n = Number(id)
  if (!Number.isInteger(n) || n <= 0) throw new Error(`ID inválido: ${id}`)
  return n
}

// GET /horarios/laboratorio/{laboratorio_id}
// Retorna los slots disponibles de un lab — úsalo para renderizar el picker de franjas
export const getHorariosPorLab = (laboratorio_id) =>
  api.get(`/horarios/laboratorio/${safeId(laboratorio_id)}`).then((r) => r.data)
// Respuesta: [{ horario_id, laboratorio_id, dia_semana (0=lun…6=dom),
//              hora_inicio, hora_fin, disponible, fecha_bloqueo?, motivo_bloqueo? }]

// GET /horarios/{id}
export const getHorario = (id) =>
  api.get(`/horarios/${safeId(id)}`).then((r) => r.data)

// POST /horarios/
export const crearHorario = (data) =>
  api.post('/horarios/', data).then((r) => r.data)
// data: { laboratorio_id, dia_semana, hora_inicio, hora_fin }

// PUT /horarios/{id}
export const actualizarHorario = (id, data) =>
  api.put(`/horarios/${safeId(id)}`, data).then((r) => r.data)

// PATCH /horarios/{id}/bloquear
export const bloquearHorario = (id, data) =>
  api.patch(`/horarios/${safeId(id)}/bloquear`, data).then((r) => r.data)
// data: { fecha_bloqueo: 'YYYY-MM-DD', motivo_bloqueo: string }

// PATCH /horarios/{id}/disponible
export const desbloquearHorario = (id) =>
  api.patch(`/horarios/${safeId(id)}/disponible`).then((r) => r.data)
