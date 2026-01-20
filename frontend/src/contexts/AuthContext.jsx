import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'
import api from '../services/api'
import { getErrorMessage } from '../utils/errorHandler'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Можно добавить запрос для получения информации о пользователе
    }
    setLoading(false)
  }, [token])

  const login = async (email, password) => {
    try {
      // Для OAuth2PasswordRequestForm нужен form-data формат
      // OAuth2 требует grant_type=password
      const formData = `grant_type=password&username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
      
      // Создаём отдельный запрос без дефолтных заголовков JSON
      // Vite проксирует /api на http://localhost:8000
      const response = await axios.post(
        '/api/auth/login',
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      )
      
      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      setToken(access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      console.error('Error response:', error.response?.data)
      return {
        success: false,
        error: getErrorMessage(error, 'Ошибка входа'),
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    delete api.defaults.headers.common['Authorization']
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, token }}>
      {children}
    </AuthContext.Provider>
  )
}

