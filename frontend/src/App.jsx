import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import LoginPage from './pages/LoginPage'
import LaboratoriosPage from './pages/LaboratoriosPage'
import NuevaReservaPage from './pages/NuevaReservaPage'
import HistorialPage from './pages/HistorialPage'
import ReportesPage from './pages/ReportesPage'
import UsuariosPage from './pages/UsuariosPage'
import HorariosPage from './pages/HorariosPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/laboratorios"
            element={<PrivateRoute><LaboratoriosPage /></PrivateRoute>}
          />
          <Route
            path="/reservas/nueva"
            element={<PrivateRoute><NuevaReservaPage /></PrivateRoute>}
          />
          <Route
            path="/historial"
            element={<PrivateRoute><HistorialPage /></PrivateRoute>}
          />
          <Route
            path="/reportes"
            element={<PrivateRoute roles={['ADMIN', 'COORDINADOR']}><ReportesPage /></PrivateRoute>}
          />
          <Route
            path="/admin/usuarios"
            element={<PrivateRoute roles={['ADMIN']}><UsuariosPage /></PrivateRoute>}
          />
          <Route
            path="/admin/horarios"
            element={<PrivateRoute roles={['ADMIN', 'COORDINADOR']}><HorariosPage /></PrivateRoute>}
          />

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App

