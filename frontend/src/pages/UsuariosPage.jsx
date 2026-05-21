import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import { getUsuarios, crearUsuario } from '../services/usuarios'

const ROLES = ['ADMIN', 'COORDINADOR', 'DOCENTE', 'CONSULTA']

const BADGE = {
  ADMIN:       { bg: '#eff6ff', color: '#1d4ed8' },
  COORDINADOR: { bg: '#f0fdf4', color: '#166534' },
  DOCENTE:     { bg: '#fefce8', color: '#854d0e' },
  CONSULTA:    { bg: '#f8fafc', color: '#64748b' },
}

const UsuariosPage = () => {
  const [usuarios, setUsuarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [mostrarForm, setMostrarForm] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const [exito, setExito] = useState(false)

  const [form, setForm] = useState({ email: '', password: '', rol: 'DOCENTE' })
  const [formError, setFormError] = useState(null)

  const cargar = () => {
    setCargando(true)
    getUsuarios()
      .then(setUsuarios)
      .catch(() => setError('No se pudieron cargar los usuarios.'))
      .finally(() => setCargando(false))
  }

  useEffect(() => { cargar() }, [])

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleCrear = async () => {
    if (!form.email.trim() || !form.password.trim()) {
      setFormError('Email y contraseña son requeridos.')
      return
    }
    setEnviando(true)
    setFormError(null)
    try {
      await crearUsuario(form)
      setExito(true)
      setForm({ email: '', password: '', rol: 'DOCENTE' })
      setMostrarForm(false)
      cargar()
      setTimeout(() => setExito(false), 3000)
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Error al crear el usuario.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Navbar />
      <div style={{ padding: 24 }}>

        <div style={s.header}>
          <h2 style={s.title}>Gestión de usuarios</h2>
          <button style={s.btnPrimary} onClick={() => { setMostrarForm(!mostrarForm); setFormError(null) }}>
            {mostrarForm ? 'Cancelar' : '+ Nuevo usuario'}
          </button>
        </div>

        {exito && <div style={s.success}>Usuario creado correctamente.</div>}
        {error && <div style={s.error}>{error}</div>}

        {mostrarForm && (
          <div style={s.formCard}>
            <h3 style={s.formTitle}>Crear nuevo usuario</h3>
            {formError && <div style={s.error}>{formError}</div>}
            <div style={s.formGrid}>
              <div>
                <label style={s.label}>Email</label>
                <input
                  style={s.input}
                  type="email"
                  name="email"
                  placeholder="usuario@universidad.edu"
                  value={form.email}
                  onChange={handleChange}
                />
              </div>
              <div>
                <label style={s.label}>Contraseña</label>
                <input
                  style={s.input}
                  type="password"
                  name="password"
                  placeholder="Mínimo 8 caracteres"
                  value={form.password}
                  onChange={handleChange}
                />
              </div>
              <div>
                <label style={s.label}>Rol</label>
                <select style={s.input} name="rol" value={form.rol} onChange={handleChange}>
                  {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
            </div>
            <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
              <button style={s.btnPrimary} onClick={handleCrear} disabled={enviando}>
                {enviando ? 'Creando...' : 'Crear usuario'}
              </button>
            </div>
          </div>
        )}

        {cargando && <p style={s.msg}>Cargando...</p>}

        {!cargando && (
          <div style={s.tableWrap}>
            <table style={s.table}>
              <thead>
                <tr style={s.thead}>
                  <th style={s.th}>#</th>
                  <th style={s.th}>Email</th>
                  <th style={s.th}>Rol</th>
                  <th style={s.th}>Estado</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.length === 0 && (
                  <tr><td colSpan={4} style={s.empty}>No hay usuarios.</td></tr>
                )}
                {usuarios.map(u => {
                  const badge = BADGE[u.rol] || {}
                  return (
                    <tr key={u.usuario_id} style={s.tr}>
                      <td style={s.td}>#{u.usuario_id}</td>
                      <td style={s.td}>{u.email}</td>
                      <td style={s.td}>
                        <span style={{ ...s.badge, background: badge.bg, color: badge.color }}>
                          {u.rol}
                        </span>
                      </td>
                      <td style={s.td}>
                        <span style={{ ...s.badge, background: u.activo ? '#f0fdf4' : '#fef2f2', color: u.activo ? '#166534' : '#dc2626' }}>
                          {u.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                    </tr>
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
  btnPrimary: { background: '#185FA5', color: '#fff', border: 'none', padding: '9px 20px', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer' },
  formCard: { background: '#fff', borderRadius: 12, padding: 24, border: '1px solid #e5e7eb', marginBottom: 20 },
  formTitle: { margin: '0 0 16px', fontSize: 15, fontWeight: 600, color: '#1a1a2e' },
  formGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 14 },
  label: { display: 'block', fontSize: 12, color: '#555', fontWeight: 500, marginBottom: 5 },
  input: { width: '100%', padding: '9px 12px', border: '1px solid #ddd', borderRadius: 8, fontSize: 13, boxSizing: 'border-box' },
  tableWrap: { background: '#fff', borderRadius: 12, border: '1px solid #e5e7eb', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse' },
  thead: { background: '#f8fafc' },
  th: { padding: '10px 16px', textAlign: 'left', fontSize: 12, color: '#555', fontWeight: 500, borderBottom: '1px solid #e5e7eb' },
  tr: { borderBottom: '1px solid #f1f5f9' },
  td: { padding: '12px 16px', fontSize: 13, color: '#1a1a2e' },
  badge: { display: 'inline-block', padding: '3px 10px', borderRadius: 100, fontSize: 11, fontWeight: 500 },
  empty: { textAlign: 'center', padding: 40, color: '#999', fontSize: 14 },
  success: { background: '#f0fdf4', color: '#166534', padding: '10px 14px', borderRadius: 8, marginBottom: 14, fontSize: 13 },
  error: { background: '#fef2f2', color: '#dc2626', padding: '10px 14px', borderRadius: 8, marginBottom: 14, fontSize: 13 },
  msg: { textAlign: 'center', color: '#999', marginTop: 40, fontSize: 14 },
}

export default UsuariosPage
