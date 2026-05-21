import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { getLaboratorios } from '../services/laboratorios'
 
const LaboratoriosPage = () => {
  const [labs, setLabs] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
 
  useEffect(() => {
    getLaboratorios()
      .then(setLabs)
      .catch(() => setError('No se pudieron cargar los laboratorios'))
      .finally(() => setCargando(false))
  }, [])
 
  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Navbar />
      <div style={{ padding: 24 }}>
        <div style={s.header}>
          <h2 style={s.title}>Laboratorios disponibles</h2>
          <button style={s.btnPrimary} onClick={() => navigate('/reservas/nueva')}>
            + Nueva reserva
          </button>
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
              <button
                style={{ ...s.btnReservar, opacity: lab.estado ? 1 : 0.4 }}
                disabled={!lab.estado}
                onClick={() => navigate('/reservas/nueva', { state: { lab } })}
              >
                Reservar →
              </button>
            </div>
          ))}
        </div>
 
        {!cargando && labs.length === 0 && !error && (
          <p style={s.msg}>No hay laboratorios registrados aún.</p>
        )}
      </div>
    </div>
  )
}
 
const s = {
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  title: { fontSize: 20, fontWeight: 600, margin: 0, color: '#1a1a2e' },
  btnPrimary: { background: '#185FA5', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', fontSize: 14, fontWeight: 500, cursor: 'pointer' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 14 },
  card: { background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e5e7eb' },
  statusRow: { display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 },
  dot: { width: 8, height: 8, borderRadius: '50%', flexShrink: 0 },
  name: { fontSize: 15, fontWeight: 600, margin: '0 0 6px', color: '#1a1a2e' },
  meta: { fontSize: 12, color: '#666', margin: '3px 0' },
  btnReservar: { width: '100%', marginTop: 14, padding: 8, background: 'transparent', border: '1px solid #ddd', borderRadius: 8, fontSize: 13, cursor: 'pointer', color: '#1a1a2e' },
  msg: { textAlign: 'center', color: '#999', marginTop: 40, fontSize: 14 },
}
 
export default LaboratoriosPage