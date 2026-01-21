import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ErrorBoundary from './ErrorBoundary'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import TimeEntries from './pages/TimeEntries'
import Matters from './pages/Matters'
import Clients from './pages/Clients'
import Contracts from './pages/Contracts'
import Employees from './pages/Employees'
import Rates from './pages/Rates'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="time-entries" element={<TimeEntries />} />
              <Route path="matters" element={<Matters />} />
              <Route path="clients" element={<Clients />} />
              <Route path="contracts" element={<Contracts />} />
              <Route path="employees" element={<Employees />} />
              <Route path="rates" element={<Rates />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  )
}

// Обработка ошибок рендеринга
if (typeof window !== 'undefined') {
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason)
  })
}

export default App

