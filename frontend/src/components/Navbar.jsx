import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Navbar = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { logout, rol, usuario } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const esAdmin = rol === 'ADMIN'
  const puedeVerReportes = rol === 'ADMIN' || rol === 'COORDINADOR'

  const links = [
    { path: '/laboratorios', label: 'Laboratorios', visible: true },
    { path: '/reservas/nueva', label: 'Nueva reserva', visible: true },
    { path: '/historial', label: 'Historial', visible: true },
    { path: '/reportes', label: 'Reportes', visible: puedeVerReportes },
    { path: '/admin/horarios', label: 'Horarios', visible: puedeVerReportes },
    { path: '/admin/usuarios', label: 'Usuarios', visible: esAdmin },
  ]

  return (
    <nav style={s.nav}>
      <span style={s.brand}>🔬 LabReservas</span>
      <div style={s.links}>
        {links.filter(l => l.visible).map((l) => (
          <button
            key={l.path}
            style={{ ...s.link, ...(location.pathname === l.path ? s.active : {}) }}
            onClick={() => navigate(l.path)}
          >
            {l.label}
          </button>
        ))}
      </div>
      <div style={s.right}>
        {usuario?.email && <span style={s.email}>{usuario.email}</span>}
        <button style={s.logout} onClick={handleLogout}>Cerrar sesión</button>
      </div>
    </nav>
  )
}
 
const s = {
  nav: { background: '#0C447C', padding: '0 24px', display: 'flex', alignItems: 'center', height: 52, gap: 8 },
  brand: { color: '#E6F1FB', fontWeight: 600, fontSize: 15, marginRight: 16 },
  links: { display: 'flex', gap: 4, flex: 1 },
  link: { background: 'none', border: 'none', color: '#85B7EB', padding: '6px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
  active: { color: '#E6F1FB', background: '#185FA5' },
  right: { display: 'flex', alignItems: 'center', gap: 12 },
  email: { color: '#85B7EB', fontSize: 12 },
  logout: { background: 'none', border: '1px solid #378ADD', color: '#85B7EB', padding: '5px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
}
 
export default Navbar