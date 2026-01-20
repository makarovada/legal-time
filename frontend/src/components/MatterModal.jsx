import { useState, useEffect } from 'react'
import api from '../services/api'
import { X } from 'lucide-react'
import { getErrorMessage } from '../utils/errorHandler'

const MatterModal = ({ matter, contracts, onClose }) => {
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    contract_id: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (matter) {
      setFormData({
        code: matter.code,
        name: matter.name,
        description: matter.description || '',
        contract_id: matter.contract_id,
      })
    }
  }, [matter])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = {
        ...formData,
        contract_id: parseInt(formData.contract_id),
      }

      if (matter) {
        await api.put(`/matters/${matter.id}`, data)
      } else {
        await api.post('/matters', data)
      }
      onClose()
    } catch (err) {
      setError(getErrorMessage(err, 'Ошибка при сохранении дела'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-jira-border">
          <h2 className="text-xl font-semibold text-jira-gray">
            {matter ? 'Редактировать дело' : 'Новое дело'}
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

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Код *
              </label>
              <input
                type="text"
                required
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
                placeholder="MAT-001"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Договор *
              </label>
              <select
                required
                value={formData.contract_id}
                onChange={(e) =>
                  setFormData({ ...formData, contract_id: e.target.value })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
              >
                <option value="">Выберите договор</option>
                {contracts.map((contract) => (
                  <option key={contract.id} value={contract.id}>
                    {contract.number || `Договор #${contract.id}`}
                  </option>
                ))}
              </select>
            </div>
          </div>

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
              placeholder="Название дела"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Описание
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows="4"
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
              placeholder="Описание дела..."
            />
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
              {loading ? 'Сохранение...' : matter ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default MatterModal

