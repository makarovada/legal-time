import { useState, useEffect } from 'react'
import api from '../services/api'
import { X } from 'lucide-react'
import { getErrorMessage } from '../utils/errorHandler'

const ClientModal = ({ client, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'legal',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (client) {
      setFormData({
        name: client.name,
        type: client.type,
      })
    }
  }, [client])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (client) {
        await api.put(`/clients/${client.id}`, formData)
      } else {
        await api.post('/clients', formData)
      }
      onClose()
    } catch (err) {
      setError(getErrorMessage(err, 'Ошибка при сохранении клиента'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-jira-border">
          <h2 className="text-xl font-semibold text-jira-gray">
            {client ? 'Редактировать клиента' : 'Новый клиент'}
          </h2>
          <button
            onClick={onClose}
            className="text-jira-gray hover:text-jira-blue"
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
              Название *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
              placeholder="Название клиента"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Тип *
            </label>
            <select
              required
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
            >
              <option value="legal">Юридическое лицо</option>
              <option value="physical">Физическое лицо</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-jira-border rounded-md text-jira-gray hover:bg-jira-gray-light"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark disabled:opacity-50"
            >
              {loading ? 'Сохранение...' : client ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ClientModal

