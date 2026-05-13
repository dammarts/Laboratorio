import api from './api'
 
// GET /reportes/uso-laboratorio
export const getUsoLaboratorio = (params = {}) =>
  api.get('/reportes/uso-laboratorio', { params }).then(r => r.data)
// params opcionales: { laboratorio_id, usuario_id, fecha_desde, fecha_hasta }
// Respuesta: [{ laboratorio_id, nombre, total_reservas, horas_ocupadas, reservas_canceladas }]
 
// GET /reportes/ocupacion-mensual
export const getOcupacionMensual = (mes, anio) =>
  api.get('/reportes/ocupacion-mensual', { params: { mes, anio } }).then(r => r.data)
// Respuesta: [{ mes, anio, laboratorio_id, nombre, total_reservas, porcentaje_ocupacion }]
 
// GET /reportes/por-docente
export const getReporteDocente = (params = {}) =>
  api.get('/reportes/por-docente', { params }).then(r => r.data)
// params opcionales: { laboratorio_id, usuario_id, fecha_desde, fecha_hasta }
// Respuesta: [{ usuario_id, email, total_reservas, laboratorios_usados, ultima_reserva }]
 
// GET /reportes/uso-laboratorio/csv
export const descargarUsoCSV = (params = {}) => {
  const query = new URLSearchParams(params).toString()
  const token = localStorage.getItem('token')
  const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/reportes/uso-laboratorio/csv${query ? '?' + query : ''}`
  const a = document.createElement('a')
  a.href = url
  a.setAttribute('download', 'uso_laboratorio.csv')
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      a.href = URL.createObjectURL(blob)
      a.click()
    })
}
 
// GET /reportes/por-docente/csv
export const descargarDocenteCSV = (params = {}) => {
  const query = new URLSearchParams(params).toString()
  const token = localStorage.getItem('token')
  const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/reportes/por-docente/csv${query ? '?' + query : ''}`
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.setAttribute('download', 'reporte_docentes.csv')
      a.click()
    })
}