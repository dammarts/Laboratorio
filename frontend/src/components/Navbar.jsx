import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
 
const links = [
  { path: '/laboratorios', label: 'Laboratorios' },
  { path: '/reservas/nueva', label: 'Nueva reserva' },
  { path: '/historial', label: 'Historial' },
]
 
const Navbar = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { logout } = useAuth()
 
  const handleLogout = () => {
    logout()
    navigate('/login')
  }
 
  return (
    <nav style={s.nav}>
      <span style={s.brand}>🔬 LabReservas</span>
      <div style={s.links}>
        {links.map((l) => (
          <button
            key={l.path}
            style={{ ...s.link, ...(location.pathname === l.path ? s.active : {}) }}
            onClick={() => navigate(l.path)}
          >
            {l.label}
          </button>
        ))}
      </div>
      <button style={s.logout} onClick={handleLogout}>
        Cerrar sesión
      </button>
    </nav>
  )
}
 
const s = {
  nav: { background: '#0C447C', padding: '0 24px', display: 'flex', alignItems: 'center', height: 52, gap: 8 },
  brand: { color: '#E6F1FB', fontWeight: 600, fontSize: 15, marginRight: 16 },
  links: { display: 'flex', gap: 4, flex: 1 },
  link: { background: 'none', border: 'none', color: '#85B7EB', padding: '6px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
  active: { color: '#E6F1FB', background: '#185FA5' },
  logout: { background: 'none', border: '1px solid #378ADD', color: '#85B7EB', padding: '5px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 13 },
}
 
export default Navbar