import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import { getLaboratorios } from '../services/laboratorios'
import {
  getHorariosPorLab,
  crearHorario,
  actualizarHorario,
  bloquearHorario,
  desbloquearHorario,
} from '../services/horarios'

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

const EMPTY_FORM = { dia_semana: 0, hora_inicio: '08:00', hora_fin: '10:00' }
const EMPTY_BLOQUEO = { fecha_bloqueo: '', motivo_bloqueo: '' }

const HorariosPage = () => {
  const [labs, setLabs] = useState([])
  const [labSeleccionado, setLabSeleccionado] = useState('')
  const [horarios, setHorarios] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  // Modal horario (crear/editar)
  const [modalHorario, setModalHorario] = useState(false)
  const [horarioEditando, setHorarioEditando] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [guardando, setGuardando] = useState(false)
  const [errorModal, setErrorModal] = useState(null)

  // Modal bloqueo
  const [modalBloqueo, setModalBloqueo] = useState(false)
  const [horarioBloquear, setHorarioBloquear] = useState(null)
  const [formBloqueo, setFormBloqueo] = useState(EMPTY_BLOQUEO)
  const [guardandoBloqueo, setGuardandoBloqueo] = useState(false)
  const [errorBloqueo, setErrorBloqueo] = useState(null)

  useEffect(() => {
    getLaboratorios()
      .then(data => {
        setLabs(data)
        if (data.length > 0) setLabSeleccionado(String(data[0].laboratorio_id))
      })
      .catch(() => setError('No se pudieron cargar los laboratorios'))
  }, [])

  useEffect(() => {
    if (!labSeleccionado) return
    setCargando(true)
    setError(null)
    getHorariosPorLab(labSeleccionado)
      .then(data => setHorarios(Array.isArray(data) ? data : []))
      .catch(() => setError('No se pudieron cargar los horarios'))
      .finally(() => setCargando(false))
  }, [labSeleccionado])

  const recargar = () => {
    if (!labSeleccionado) return
    getHorariosPorLab(labSeleccionado)
      .then(data => setHorarios(Array.isArray(data) ? data : []))
      .catch(() => {})
  }

  // --- Horario modal ---
  const abrirCrear = () => {
    setHorarioEditando(null)
    setForm(EMPTY_FORM)
    setErrorModal(null)
    setModalHorario(true)
  }

  const abrirEditar = (h) => {
    setHorarioEditando(h)
    setForm({ dia_semana: h.dia_semana, hora_inicio: h.hora_inicio, hora_fin: h.hora_fin })
    setErrorModal(null)
    setModalHorario(true)
  }

  const cerrarModalHorario = () => {
    setModalHorario(false)
    setHorarioEditando(null)
    setErrorModal(null)
  }

  const handleGuardarHorario = async () => {
    if (!form.hora_inicio || !form.hora_fin) {
      setErrorModal('Hora inicio y hora fin son obligatorias.')
      return
    }
    if (form.hora_inicio >= form.hora_fin) {
      setErrorModal('La hora de fin debe ser posterior a la hora de inicio.')
      return
    }
    setGuardando(true)
    setErrorModal(null)
    try {
      if (horarioEditando) {
        await actualizarHorario(horarioEditando.horario_id, form)
      } else {
        await crearHorario({ ...form, laboratorio_id: Number(labSeleccionado) })
      }
      cerrarModalHorario()
      recargar()
    } catch (err) {
      setErrorModal(err?.response?.data?.detail || 'Error al guardar el horario')
    } finally {
      setGuardando(false)
    }
  }

  // --- Bloqueo modal ---
  const abrirBloqueo = (h) => {
    setHorarioBloquear(h)
    setFormBloqueo(EMPTY_BLOQUEO)
    setErrorBloqueo(null)
    setModalBloqueo(true)
  }

  const cerrarModalBloqueo = () => {
    setModalBloqueo(false)
    setHorarioBloquear(null)
    setErrorBloqueo(null)
  }

  const handleBloquear = async () => {
    if (!formBloqueo.fecha_bloqueo || !formBloqueo.motivo_bloqueo.trim()) {
      setErrorBloqueo('La fecha y el motivo son obligatorios.')
      return
    }
    setGuardandoBloqueo(true)
    setErrorBloqueo(null)
    try {
      await bloquearHorario(horarioBloquear.horario_id, {
        fecha_bloqueo: formBloqueo.fecha_bloqueo,
        motivo_bloqueo: formBloqueo.motivo_bloqueo.trim(),
      })
      cerrarModalBloqueo()
      recargar()
    } catch (err) {
      setErrorBloqueo(err?.response?.data?.detail || 'Error al bloquear el horario')
    } finally {
      setGuardandoBloqueo(false)
    }
  }

  const handleDesbloquear = async (h) => {
    try {
      await desbloquearHorario(h.horario_id)
      recargar()
    } catch {
      alert('No se pudo desbloquear el horario')
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Navbar />
      <div style={{ padding: 24 }}>

        <div style={s.header}>
          <h2 style={s.title}>Gestión de Horarios</h2>
          <button style={s.btnPrimary} onClick={abrirCrear} disabled={!labSeleccionado}>
            + Nuevo horario
          </button>
        </div>

        <div style={s.filtroRow}>
          <label style={s.label}>Laboratorio</label>
          <select
            style={s.select}
            value={labSeleccionado}
            onChange={e => setLabSeleccionado(e.target.value)}
          >
            {labs.map(lab => (
              <option key={lab.laboratorio_id} value={lab.laboratorio_id}>
                {lab.nombre}
              </option>
            ))}
          </select>
        </div>

        {error && <p style={s.errorText}>{error}</p>}
        {cargando && <p style={s.msg}>Cargando horarios...</p>}

        {!cargando && horarios.length === 0 && !error && (
          <p style={s.msg}>No hay horarios configurados para este laboratorio.</p>
        )}

        {!cargando && horarios.length > 0 && (
          <div style={s.tableWrap}>
            <table style={s.table}>
              <thead>
                <tr style={s.thead}>
                  <th style={s.th}>Día</th>
                  <th style={s.th}>Hora inicio</th>
                  <th style={s.th}>Hora fin</th>
                  <th style={s.th}>Estado</th>
                  <th style={s.th}>Fecha bloqueo</th>
                  <th style={s.th}>Motivo</th>
                  <th style={s.th}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {horarios.map(h => (
                  <tr key={h.horario_id} style={s.tr}>
                    <td style={s.td}>{DIAS[h.dia_semana] ?? h.dia_semana}</td>
                    <td style={s.td}>{h.hora_inicio}</td>
                    <td style={s.td}>{h.hora_fin}</td>
                    <td style={s.td}>
                      <span style={{
                        ...s.badge,
                        background: h.disponible ? '#f0fdf4' : '#fef2f2',
                        color: h.disponible ? '#166534' : '#dc2626',
                      }}>
                        {h.disponible ? 'Disponible' : 'Bloqueado'}
                      </span>
                    </td>
                    <td style={s.td}>{h.fecha_bloqueo || '—'}</td>
                    <td style={s.td}>{h.motivo_bloqueo || '—'}</td>
                    <td style={s.td}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button style={s.btnAccion} onClick={() => abrirEditar(h)}>
                          Editar
                        </button>
                        {h.disponible ? (
                          <button
                            style={{ ...s.btnAccion, color: '#dc2626', borderColor: '#fecaca' }}
                            onClick={() => abrirBloqueo(h)}
                          >
                            Bloquear
                          </button>
                        ) : (
                          <button
                            style={{ ...s.btnAccion, color: '#166534', borderColor: '#bbf7d0' }}
                            onClick={() => handleDesbloquear(h)}
                          >
                            Desbloquear
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal crear/editar horario */}
      {modalHorario && (
        <div style={s.overlay}>
          <div style={s.modal}>
            <h3 style={s.modalTitle}>
              {horarioEditando ? 'Editar horario' : 'Nuevo horario'}
            </h3>

            <label style={s.labelModal}>Día de la semana</label>
            <select
              style={s.input}
              value={form.dia_semana}
              onChange={e => setForm(f => ({ ...f, dia_semana: Number(e.target.value) }))}
            >
              {DIAS.map((d, i) => (
                <option key={i} value={i}>{d}</option>
              ))}
            </select>

            <label style={s.labelModal}>Hora inicio</label>
            <input
              style={s.input}
              type="time"
              value={form.hora_inicio}
              onChange={e => setForm(f => ({ ...f, hora_inicio: e.target.value }))}
            />

            <label style={s.labelModal}>Hora fin</label>
            <input
              style={s.input}
              type="time"
              value={form.hora_fin}
              onChange={e => setForm(f => ({ ...f, hora_fin: e.target.value }))}
            />

            {errorModal && <p style={s.errorMsg}>{errorModal}</p>}

            <div style={s.modalActions}>
              <button style={s.btnCancelar} onClick={cerrarModalHorario} disabled={guardando}>
                Cancelar
              </button>
              <button style={s.btnPrimary} onClick={handleGuardarHorario} disabled={guardando}>
                {guardando ? 'Guardando...' : horarioEditando ? 'Guardar cambios' : 'Crear horario'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal bloquear horario */}
      {modalBloqueo && (
        <div style={s.overlay}>
          <div style={s.modal}>
            <h3 style={s.modalTitle}>Bloquear horario</h3>
            <p style={{ fontSize: 13, color: '#666', marginBottom: 16 }}>
              {DIAS[horarioBloquear?.dia_semana]} · {horarioBloquear?.hora_inicio} – {horarioBloquear?.hora_fin}
            </p>

            <label style={s.labelModal}>Fecha de bloqueo</label>
            <input
              style={s.input}
              type="date"
              value={formBloqueo.fecha_bloqueo}
              onChange={e => setFormBloqueo(f => ({ ...f, fecha_bloqueo: e.target.value }))}
            />

            <label style={s.labelModal}>Motivo</label>
            <input
              style={s.input}
              value={formBloqueo.motivo_bloqueo}
              onChange={e => setFormBloqueo(f => ({ ...f, motivo_bloqueo: e.target.value }))}
              placeholder="Ej: Mantenimiento preventivo"
            />

            {errorBloqueo && <p style={s.errorMsg}>{errorBloqueo}</p>}

            <div style={s.modalActions}>
              <button style={s.btnCancelar} onClick={cerrarModalBloqueo} disabled={guardandoBloqueo}>
                Cancelar
              </button>
              <button
                style={{ ...s.btnPrimary, background: '#dc2626' }}
                onClick={handleBloquear}
                disabled={guardandoBloqueo}
              >
                {guardandoBloqueo ? 'Bloqueando...' : 'Bloquear'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const s = {
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  title: { fontSize: 20, fontWeight: 600, margin: 0, color: '#1a1a2e' },
  btnPrimary: { background: '#185FA5', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', fontSize: 14, fontWeight: 500, cursor: 'pointer' },
  filtroRow: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20, flexWrap: 'wrap' },
  label: { fontSize: 13, color: '#555', fontWeight: 500 },
  select: { padding: '8px 12px', border: '1px solid #ddd', borderRadius: 8, fontSize: 13, background: '#fff', minWidth: 220 },
  tableWrap: { background: '#fff', borderRadius: 12, border: '1px solid #e5e7eb', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse' },
  thead: { background: '#f8fafc' },
  th: { padding: '10px 16px', textAlign: 'left', fontSize: 12, color: '#555', fontWeight: 500, borderBottom: '1px solid #e5e7eb' },
  tr: { borderBottom: '1px solid #f1f5f9' },
  td: { padding: '11px 16px', fontSize: 13, color: '#1a1a2e' },
  badge: { display: 'inline-block', padding: '3px 10px', borderRadius: 100, fontSize: 11, fontWeight: 500 },
  btnAccion: { padding: '5px 12px', background: '#fff', border: '1px solid #e5e7eb', borderRadius: 6, fontSize: 12, cursor: 'pointer', color: '#185FA5' },
  msg: { textAlign: 'center', color: '#999', marginTop: 40, fontSize: 14 },
  errorText: { color: '#dc2626', fontSize: 13, marginBottom: 12 },
  overlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
  modal: { background: '#fff', borderRadius: 14, padding: 28, width: 400, maxWidth: '92vw', boxShadow: '0 8px 32px rgba(0,0,0,0.18)' },
  modalTitle: { fontSize: 17, fontWeight: 600, margin: '0 0 16px', color: '#1a1a2e' },
  labelModal: { display: 'block', fontSize: 12, color: '#555', marginBottom: 4, marginTop: 12 },
  input: { width: '100%', padding: '9px 12px', border: '1px solid #ddd', borderRadius: 8, fontSize: 13, boxSizing: 'border-box' },
  errorMsg: { color: '#dc2626', fontSize: 12, marginTop: 8 },
  modalActions: { display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 20 },
  btnCancelar: { padding: '8px 18px', background: '#f5f5f5', color: '#555', border: 'none', borderRadius: 8, fontSize: 13, cursor: 'pointer' },
}

export default HorariosPage
