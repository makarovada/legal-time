import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-jira-gray">Загрузка...</div>
      </div>
    )
  }

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute

