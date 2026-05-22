import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import {
  getLaboratorios,
  crearLaboratorio,
  actualizarLaboratorio,
  toggleEstadoLaboratorio,
} from '../services/laboratorios'

const EMPTY_FORM = { nombre: '', ubicacion: '', capacidad_maxima: '', recursos_disponibles: '' }

const LaboratoriosPage = () => {
  const { rol } = useAuth()
  const navigate = useNavigate()
  const esAdmin = rol === 'ADMIN'

  const [labs, setLabs] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const [modalAbierto, setModalAbierto] = useState(false)
  const [labEditando, setLabEditando] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [guardando, setGuardando] = useState(false)
  const [errorModal, setErrorModal] = useState(null)

  const cargarLabs = () => {
    setCargando(true)
    getLaboratorios()
      .then(setLabs)
      .catch(() => setError('No se pudieron cargar los laboratorios'))
      .finally(() => setCargando(false))
  }

  useEffect(() => { cargarLabs() }, [])

  const abrirCrear = () => {
    setLabEditando(null)
    setForm(EMPTY_FORM)
    setErrorModal(null)
    setModalAbierto(true)
  }

  const abrirEditar = (lab) => {
    setLabEditando(lab)
    setForm({
      nombre: lab.nombre || '',
      ubicacion: lab.ubicacion || '',
      capacidad_maxima: lab.capacidad_maxima || '',
      recursos_disponibles: lab.recursos_disponibles || '',
    })
    setErrorModal(null)
    setModalAbierto(true)
  }

  const cerrarModal = () => {
    setModalAbierto(false)
    setLabEditando(null)
    setForm(EMPTY_FORM)
    setErrorModal(null)
  }

  const handleGuardar = async () => {
    if (!form.nombre.trim() || !form.ubicacion.trim() || !form.capacidad_maxima) {
      setErrorModal('Nombre, ubicación y capacidad son obligatorios.')
      return
    }
    setGuardando(true)
    setErrorModal(null)
    try {
      const payload = {
        nombre: form.nombre.trim(),
        ubicacion: form.ubicacion.trim(),
        capacidad_maxima: Number(form.capacidad_maxima),
        recursos_disponibles: form.recursos_disponibles.trim() || null,
      }
      if (labEditando) {
        await actualizarLaboratorio(labEditando.laboratorio_id, payload)
      } else {
        await crearLaboratorio(payload)
      }
      cerrarModal()
      cargarLabs()
    } catch (err) {
      setErrorModal(err?.response?.data?.detail || 'Error al guardar')
    } finally {
      setGuardando(false)
    }
  }

  const handleToggleEstado = async (lab) => {
    try {
      await toggleEstadoLaboratorio(lab.laboratorio_id)
      cargarLabs()
    } catch {
      alert('No se pudo cambiar el estado del laboratorio')
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Navbar />
      <div style={{ padding: 24 }}>

        <div style={s.header}>
          <h2 style={s.title}>Laboratorios</h2>
          <div style={{ display: 'flex', gap: 10 }}>
            {esAdmin && (
              <button style={s.btnSecondary} onClick={abrirCrear}>
                + Nuevo laboratorio
              </button>
            )}
            <button style={s.btnPrimary} onClick={() => navigate('/reservas/nueva')}>
              + Nueva reserva
            </button>
          </div>
        </div>

        {cargando && <p style={s.msg}>Cargando...</p>}
        {error && <p style={{ ...s.msg, color: '#dc2626' }}>{error}</p>}

        <div style={s.grid}>
          {labs.map((lab) => (
            <div key={lab.laboratorio_id} style={s.card}>
              <div style={s.statusRow}>
                <span style={{ ...s.dot, background: lab.estado ? '#1D9E75' : '#A32D2D' }} />
                <span style={{ fontSize: 12, color: lab.estado ? '#0F6E56' : '#A32D2D' }}>
                  {lab.estado ? 'Activo' : 'Inactivo'}
                </span>
              </div>
              <p style={s.name}>{lab.nombre}</p>
              <p style={s.meta}>📍 {lab.ubicacion}</p>
              <p style={s.meta}>👥 Capacidad: {lab.capacidad_maxima}</p>
              {lab.recursos_disponibles && (
                <p style={s.meta}>🖥 {lab.recursos_disponibles}</p>
              )}

              {esAdmin ? (
                <div style={{ display: 'flex', gap: 6, marginTop: 14 }}>
                  <button style={s.btnEditar} onClick={() => abrirEditar(lab)}>
                    Editar
                  </button>
                  <button
                    style={{ ...s.btnToggle, background: lab.estado ? '#fef2f2' : '#f0fdf4', color: lab.estado ? '#dc2626' : '#166534' }}
                    onClick={() => handleToggleEstado(lab)}
                  >
                    {lab.estado ? 'Desactivar' : 'Activar'}
                  </button>
                </div>
              ) : (
                <button
                  style={{ ...s.btnReservar, opacity: lab.estado ? 1 : 0.4 }}
                  disabled={!lab.estado}
                  onClick={() => navigate('/reservas/nueva', { state: { lab } })}
                >
                  Reservar →
                </button>
              )}
            </div>
          ))}
        </div>

        {!cargando && labs.length === 0 && !error && (
          <p style={s.msg}>No hay laboratorios registrados aún.</p>
        )}
      </div>

      {modalAbierto && (
        <div style={s.overlay}>
          <div style={s.modal}>
            <h3 style={s.modalTitle}>
              {labEditando ? 'Editar laboratorio' : 'Nuevo laboratorio'}
            </h3>

            <label style={s.label}>Nombre *</label>
            <input
              style={s.input}
              value={form.nombre}
              onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))}
              placeholder="Ej: Lab de Informática A"
            />

            <label style={s.label}>Ubicación *</label>
            <input
              style={s.input}
              value={form.ubicacion}
              onChange={e => setForm(f => ({ ...f, ubicacion: e.target.value }))}
              placeholder="Ej: Bloque B, Piso 2"
            />

            <label style={s.label}>Capacidad máxima *</label>
            <input
              style={s.input}
              type="number"
              min="1"
              value={form.capacidad_maxima}
              onChange={e => setForm(f => ({ ...f, capacidad_maxima: e.target.value }))}
              placeholder="Ej: 30"
            />

            <label style={s.label}>Recursos disponibles</label>
            <input
              style={s.input}
              value={form.recursos_disponibles}
              onChange={e => setForm(f => ({ ...f, recursos_disponibles: e.target.value }))}
              placeholder="Ej: 30 PCs, proyector, pizarra"
            />

            {errorModal && <p style={s.errorText}>{errorModal}</p>}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 20 }}>
              <button style={s.btnCancelar} onClick={cerrarModal} disabled={guardando}>
                Cancelar
              </button>
              <button style={s.btnPrimary} onClick={handleGuardar} disabled={guardando}>
                {guardando ? 'Guardando...' : labEditando ? 'Guardar cambios' : 'Crear laboratorio'}
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
  btnSecondary: { background: '#fff', color: '#185FA5', border: '1px solid #185FA5', borderRadius: 8, padding: '8px 18px', fontSize: 14, fontWeight: 500, cursor: 'pointer' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 14 },
  card: { background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e5e7eb' },
  statusRow: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 },
  dot: { width: 8, height: 8, borderRadius: '50%', flexShrink: 0 },
  name: { fontSize: 15, fontWeight: 600, margin: '0 0 6px', color: '#1a1a2e' },
  meta: { fontSize: 12, color: '#666', margin: '3px 0' },
  btnReservar: { width: '100%', marginTop: 14, padding: 8, background: 'transparent', border: '1px solid #ddd', borderRadius: 8, fontSize: 13, cursor: 'pointer', color: '#1a1a2e' },
  btnEditar: { flex: 1, padding: '7px 0', background: '#f0f6ff', color: '#185FA5', border: '1px solid #c7d9f0', borderRadius: 8, fontSize: 12, cursor: 'pointer', fontWeight: 500 },
  btnToggle: { flex: 1, padding: '7px 0', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 12, cursor: 'pointer', fontWeight: 500 },
  msg: { textAlign: 'center', color: '#999', marginTop: 40, fontSize: 14 },
  overlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
  modal: { background: '#fff', borderRadius: 14, padding: 28, width: 420, maxWidth: '92vw', boxShadow: '0 8px 32px rgba(0,0,0,0.18)' },
  modalTitle: { fontSize: 17, fontWeight: 600, margin: '0 0 20px', color: '#1a1a2e' },
  label: { display: 'block', fontSize: 12, color: '#555', marginBottom: 4, marginTop: 12 },
  input: { width: '100%', padding: '9px 12px', border: '1px solid #ddd', borderRadius: 8, fontSize: 13, boxSizing: 'border-box' },
  errorText: { color: '#dc2626', fontSize: 12, marginTop: 8 },
  btnCancelar: { padding: '8px 18px', background: '#f5f5f5', color: '#555', border: 'none', borderRadius: 8, fontSize: 13, cursor: 'pointer' },
}

export default LaboratoriosPage
