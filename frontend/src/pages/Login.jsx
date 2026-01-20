import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Scale } from 'lucide-react'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(email, password)
    setLoading(false)

    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-jira-gray-light">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Scale className="text-jira-blue" size={48} />
          </div>
          <h2 className="text-3xl font-bold text-jira-gray">LegalTime</h2>
          <p className="mt-2 text-sm text-jira-gray">Учёт времени для юристов</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-jira-gray mb-1">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-jira-border rounded-md placeholder-gray-400 text-jira-gray focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
                placeholder="your.email@example.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-jira-gray mb-1">
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-jira-border rounded-md placeholder-gray-400 text-jira-gray focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-jira-blue hover:bg-jira-blue-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-jira-blue disabled:opacity-50"
            >
              {loading ? 'Вход...' : 'Войти'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Login

