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

// Функция для декодирования JWT токена
const decodeToken = (token) => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Error decoding token:', error)
    return null
  }
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Декодируем токен для получения роли пользователя
      const decoded = decodeToken(token)
      if (decoded) {
        setUser({
          email: decoded.sub,
          role: decoded.role || 'lawyer',
        })
      }
    } else {
      setUser(null)
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
      
      // Декодируем токен для получения роли пользователя
      const decoded = decodeToken(access_token)
      if (decoded) {
        setUser({
          email: decoded.sub,
          role: decoded.role || 'lawyer',
        })
      }
      
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

