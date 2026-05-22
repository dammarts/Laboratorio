import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import { getReservas, cancelarReserva, reprogramarReserva } from '../services/reservas'

const BADGE = {
  ACTIVA:       { bg: '#f0fdf4', color: '#166534', label: 'Activa' },
  CANCELADA:    { bg: '#fef2f2', color: '#dc2626', label: 'Cancelada' },
  REPROGRAMADA: { bg: '#fffbeb', color: '#92400e', label: 'Reprogramada' },
}

const today = () => new Date().toISOString().split('T')[0]

const HistorialPage = () => {
  const [reservas, setReservas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [filtroEstado, setFiltroEstado] = useState('')
  const [error, setError] = useState(null)

  // cancelar
  const [cancelId, setCancelId] = useState(null)
  const [motivo, setMotivo] = useState('')

  // reprogramar
  const [reprogramarId, setReprogramarId] = useState(null)
  const [reprForm, setReprForm] = useState({ fecha: '', hora_inicio: '', hora_fin: '' })

  const cargar = (estado = '') => {
    setCargando(true)
    const params = estado ? { estado } : {}
    getReservas(params)
      .then(setReservas)
      .catch(() => setError('No se pudieron cargar las reservas.'))
      .finally(() => setCargando(false))
  }

  useEffect(() => { cargar(filtroEstado) }, [filtroEstado])

  const abrirCancelar = (id) => {
    setReprogramarId(null)
    setCancelId(cancelId === id ? null : id)
    setMotivo('')
    setError(null)
  }

  const abrirReprogramar = (r) => {
    setCancelId(null)
    setReprogramarId(reprogramarId === r.reserva_id ? null : r.reserva_id)
    setReprForm({ fecha: r.fecha || today(), hora_inicio: r.hora_inicio?.slice(0, 5) || '', hora_fin: r.hora_fin?.slice(0, 5) || '' })
    setError(null)
  }

  const handleCancelar = async (id) => {
    if (!motivo.trim()) return
    try {
      await cancelarReserva(id, motivo)
      setCancelId(null)
      setMotivo('')
      cargar(filtroEstado)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cancelar la reserva.')
    }
  }

  const handleReprogramar = async (id) => {
    if (!reprForm.fecha || !reprForm.hora_inicio || !reprForm.hora_fin) {
      setError('Completa fecha, hora inicio y hora fin.')
      return
    }
    if (reprForm.hora_inicio >= reprForm.hora_fin) {
      setError('La hora de fin debe ser posterior a la hora de inicio.')
      return
    }
    try {
      await reprogramarReserva(id, reprForm)
      setReprogramarId(null)
      cargar(filtroEstado)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al reprogramar la reserva.')
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Navbar />
      <div style={{ padding: 24 }}>
        <div style={s.header}>
          <h2 style={s.title}>Historial de reservas</h2>
          <select
            style={s.select}
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
          >
            <option value="">Todos los estados</option>
            <option value="ACTIVA">Activas</option>
            <option value="CANCELADA">Canceladas</option>
            <option value="REPROGRAMADA">Reprogramadas</option>
          </select>
        </div>

        {error && <div style={s.error}>{error}</div>}
        {cargando && <p style={s.msg}>Cargando...</p>}

        {!cargando && (
          <div style={s.tableWrap}>
            <table style={s.table}>
              <thead>
                <tr style={s.thead}>
                  <th style={s.th}>#</th>
                  <th style={s.th}>Curso</th>
                  <th style={s.th}>Fecha</th>
                  <th style={s.th}>Horario</th>
                  <th style={s.th}>Estado</th>
                  <th style={s.th}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {reservas.length === 0 && (
                  <tr>
                    <td colSpan={6} style={s.empty}>No hay reservas para mostrar.</td>
                  </tr>
                )}
                {reservas.map((r) => {
                  const badge = BADGE[r.estado] || {}
                  const cancelAbierto = cancelId === r.reserva_id
                  const reprAbierto = reprogramarId === r.reserva_id

                  return (
                    <>
                      <tr key={r.reserva_id} style={s.tr}>
                        <td style={s.td}>#{r.reserva_id}</td>
                        <td style={s.td}>{r.curso}</td>
                        <td style={s.td}>{r.fecha}</td>
                        <td style={s.td}>
                          {r.hora_inicio?.slice(0, 5)} – {r.hora_fin?.slice(0, 5)}
                        </td>
                        <td style={s.td}>
                          <span style={{ ...s.badge, background: badge.bg, color: badge.color }}>
                            {badge.label}
                          </span>
                        </td>
                        <td style={s.td}>
                          {r.estado === 'ACTIVA' && (
                            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                              <button
                                style={s.btnRepr}
                                onClick={() => abrirReprogramar(r)}
                              >
                                {reprAbierto ? 'Cerrar' : 'Reprogramar'}
                              </button>
                              <button
                                style={s.btnCancelar}
                                onClick={() => abrirCancelar(r.reserva_id)}
                              >
                                {cancelAbierto ? 'Cerrar' : 'Cancelar'}
                              </button>
                            </div>
                          )}
                          {r.motivo_cancelacion && (
                            <span style={s.motivo} title={r.motivo_cancelacion}>
                              💬 {r.motivo_cancelacion.slice(0, 30)}{r.motivo_cancelacion.length > 30 ? '...' : ''}
                            </span>
                          )}
                        </td>
                      </tr>

                      {cancelAbierto && (
                        <tr key={`cancel-${r.reserva_id}`}>
                          <td colSpan={6} style={s.inlineRow}>
                            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                              <input
                                style={{ ...s.input, flex: 1 }}
                                placeholder="Motivo de cancelación (requerido)"
                                value={motivo}
                                onChange={(e) => setMotivo(e.target.value)}
                              />
                              <button style={s.btnConfirmRed} onClick={() => handleCancelar(r.reserva_id)}>
                                Confirmar cancelación
                              </button>
                              <button style={s.btnClose} onClick={() => setCancelId(null)}>✕</button>
                            </div>
                          </td>
                        </tr>
                      )}

                      {reprAbierto && (
                        <tr key={`repr-${r.reserva_id}`}>
                          <td colSpan={6} style={s.inlineRowBlue}>
                            <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end', flexWrap: 'wrap' }}>
                              <div>
                                <label style={s.inlineLabel}>Nueva fecha</label>
                                <input
                                  style={s.input}
                                  type="date"
                                  min={today()}
                                  value={reprForm.fecha}
                                  onChange={e => setReprForm(f => ({ ...f, fecha: e.target.value }))}
                                />
                              </div>
                              <div>
                                <label style={s.inlineLabel}>Hora inicio</label>
                                <input
                                  style={s.input}
                                  type="time"
                                  value={reprForm.hora_inicio}
                                  onChange={e => setReprForm(f => ({ ...f, hora_inicio: e.target.value }))}
                                />
                              </div>
                              <div>
                                <label style={s.inlineLabel}>Hora fin</label>
                                <input
                                  style={s.input}
                                  type="time"
                                  value={reprForm.hora_fin}
                                  onChange={e => setReprForm(f => ({ ...f, hora_fin: e.target.value }))}
                                />
                              </div>
                              <button style={s.btnConfirmBlue} onClick={() => handleReprogramar(r.reserva_id)}>
                                Confirmar
                              </button>
                              <button style={s.btnClose} onClick={() => setReprogramarId(null)}>✕</button>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

const s = {
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 },
  title: { fontSize: 20, fontWeight: 600, margin: 0, color: '#1a1a2e' },
  select: { padding: '7px 12px', border: '1px solid #ddd', borderRadius: 8, fontSize: 13, background: '#fff' },
  tableWrap: { background: '#fff', borderRadius: 12, border: '1px solid #e5e7eb', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse' },
  thead: { background: '#f8fafc' },
  th: { padding: '10px 16px', textAlign: 'left', fontSize: 12, color: '#555', fontWeight: 500, borderBottom: '1px solid #e5e7eb' },
  tr: { borderBottom: '1px solid #f1f5f9' },
  td: { padding: '12px 16px', fontSize: 13, color: '#1a1a2e', verticalAlign: 'middle' },
  badge: { display: 'inline-block', padding: '3px 10px', borderRadius: 100, fontSize: 11, fontWeight: 500 },
  btnCancelar: { background: 'none', border: '1px solid #fca5a5', color: '#dc2626', padding: '4px 12px', borderRadius: 6, fontSize: 12, cursor: 'pointer' },
  btnRepr: { background: 'none', border: '1px solid #93c5fd', color: '#185FA5', padding: '4px 12px', borderRadius: 6, fontSize: 12, cursor: 'pointer' },
  motivo: { fontSize: 11, color: '#999', marginLeft: 8 },
  inlineRow: { padding: '10px 16px', background: '#fef9f9', borderBottom: '1px solid #f1f5f9' },
  inlineRowBlue: { padding: '12px 16px', background: '#f0f6ff', borderBottom: '1px solid #f1f5f9' },
  inlineLabel: { display: 'block', fontSize: 11, color: '#555', marginBottom: 4 },
  input: { padding: '7px 12px', border: '1px solid #ddd', borderRadius: 8, fontSize: 13 },
  btnConfirmRed: { background: '#dc2626', color: '#fff', border: 'none', padding: '7px 16px', borderRadius: 8, fontSize: 13, cursor: 'pointer', whiteSpace: 'nowrap' },
  btnConfirmBlue: { background: '#185FA5', color: '#fff', border: 'none', padding: '7px 16px', borderRadius: 8, fontSize: 13, cursor: 'pointer' },
  btnClose: { background: 'none', border: '1px solid #ddd', padding: '7px 12px', borderRadius: 8, fontSize: 13, cursor: 'pointer', color: '#666' },
  empty: { textAlign: 'center', padding: 40, color: '#999', fontSize: 14 },
  error: { background: '#fef2f2', color: '#dc2626', padding: '10px 14px', borderRadius: 8, marginBottom: 14, fontSize: 13 },
  msg: { textAlign: 'center', color: '#999', marginTop: 40, fontSize: 14 },
}

export default HistorialPage
