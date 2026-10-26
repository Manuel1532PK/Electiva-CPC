import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { Suspense, lazy } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import Login from './pages/Login'
import ChatApp from './ChatApp'
import PatientDashboard from './pages/PatientDashboard'
import AdminPanel from './pages/AdminPanel'

const Register = lazy(() => import('./pages/Register'))

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '821096294804-8kt4ghsltbtu1q6djkpmi6hj9o6mudcb.apps.googleusercontent.com'

function RoleRedirect() {
  const { user } = useAuth()
  if (user?.role === 'paciente') return <Navigate to="/paciente" replace />
  if (user?.role === 'admin' || user?.role === 'super_admin') return <Navigate to="/admin" replace />
  return <ChatApp />
}

export default function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Suspense fallback={null}><Register /></Suspense>} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <RoleRedirect />
                </ProtectedRoute>
              }
            />
            <Route
              path="/paciente"
              element={
                <ProtectedRoute requiredRole="paciente">
                  <PatientDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredRole={['admin', 'super_admin']}>
                  <AdminPanel />
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat"
              element={
                <ProtectedRoute requiredRole="medico">
                  <ChatApp />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </GoogleOAuthProvider>
  )
}
