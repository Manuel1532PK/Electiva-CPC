import { type ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

type Props = {
  children: ReactNode
  requiredRole?: string | string[]
}

export function ProtectedRoute({ children, requiredRole }: Props) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <p>Cargando...</p>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const roles = Array.isArray(requiredRole) ? requiredRole : requiredRole ? [requiredRole] : null
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}