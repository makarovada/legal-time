import { useState, useEffect } from 'react'
import api from '../services/api'
import { X } from 'lucide-react'
import { getErrorMessage } from '../utils/errorHandler'

const EmployeeModal = ({ employee, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'lawyer',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (employee) {
      setFormData({
        name: employee.name,
        email: employee.email,
        password: '', // Не показываем пароль при редактировании
        role: employee.role,
      })
    } else {
      setFormData({
        name: '',
        email: '',
        password: '',
        role: 'lawyer',
      })
    }
  }, [employee])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    // Валидация
    if (!formData.name.trim()) {
      setError('Имя обязательно')
      return
    }
    if (!formData.email.trim()) {
      setError('Email обязателен')
      return
    }
    if (!employee && !formData.password) {
      setError('Пароль обязателен при создании')
      return
    }
    
    setLoading(true)

    try {
      const dataToSend = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        role: formData.role,
      }
      
      // Добавляем пароль только если он указан или это создание
      if (formData.password || !employee) {
        dataToSend.password = formData.password
      }
      
      if (employee) {
        await api.put(`/employees/${employee.id}`, dataToSend)
      } else {
        await api.post('/employees', dataToSend)
      }
      onClose()
    } catch (err) {
      setError(getErrorMessage(err, 'Ошибка при сохранении сотрудника'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-jira-border">
          <h2 className="text-xl font-semibold text-jira-gray">
            {employee ? 'Редактировать сотрудника' : 'Новый сотрудник'}
          </h2>
          <button
            onClick={onClose}
            className="text-jira-gray hover:text-jira-gray-dark"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Имя *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-2 focus:ring-jira-blue"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Email *
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-2 focus:ring-jira-blue"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Пароль {employee ? '(оставьте пустым, чтобы не менять)' : '*'}
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-2 focus:ring-jira-blue"
              required={!employee}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Роль *
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-2 focus:ring-jira-blue"
              required
            >
              <option value="lawyer">Юрист</option>
              <option value="senior_lawyer">Старший юрист</option>
              <option value="admin">Администратор</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-jira-gray hover:text-jira-gray-dark border border-jira-border rounded-md"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Сохранение...' : employee ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EmployeeModal

