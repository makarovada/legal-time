import { useState, useEffect } from 'react'
import api from '../services/api'
import { X } from 'lucide-react'
import { getErrorMessage } from '../utils/errorHandler'

const ContractModal = ({ contract, clients, onClose }) => {
  const [formData, setFormData] = useState({
    number: '',
    client_id: '',
    date: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (contract) {
      setFormData({
        number: contract.number || '',
        client_id: contract.client_id,
        date: contract.date
          ? new Date(contract.date).toISOString().split('T')[0]
          : '',
      })
    }
  }, [contract])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = {
        ...formData,
        client_id: parseInt(formData.client_id),
      }

      if (contract) {
        await api.put(`/contracts/${contract.id}`, data)
      } else {
        await api.post('/contracts', data)
      }
      onClose()
    } catch (err) {
      setError(getErrorMessage(err, 'Ошибка при сохранении договора'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-jira-border">
          <h2 className="text-xl font-semibold text-jira-gray">
            {contract ? 'Редактировать договор' : 'Новый договор'}
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
              Номер договора
            </label>
            <input
              type="text"
              value={formData.number}
              onChange={(e) => setFormData({ ...formData, number: e.target.value })}
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
              placeholder="Номер договора"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Клиент *
            </label>
            <select
              required
              value={formData.client_id}
              onChange={(e) =>
                setFormData({ ...formData, client_id: e.target.value })
              }
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
            >
              <option value="">Выберите клиента</option>
              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Дата договора *
            </label>
            <input
              type="date"
              required
              value={formData.date}
              onChange={(e) =>
                setFormData({ ...formData, date: e.target.value })
              }
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
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
              {loading ? 'Сохранение...' : contract ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ContractModal

