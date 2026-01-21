import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import api from '../services/api'
import { getErrorMessage } from '../utils/errorHandler'

const RateModal = ({ rate, employees, contracts, onClose }) => {
  const [formData, setFormData] = useState({
    value: '',
    type: 'default', // default | employee | contract
    employee_id: '',
    contract_id: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (rate) {
      let type = 'default'
      if (rate.contract_id) type = 'contract'
      else if (rate.employee_id) type = 'employee'

      setFormData({
        value: rate.value,
        type,
        employee_id: rate.employee_id || '',
        contract_id: rate.contract_id || '',
      })
    } else {
      setFormData({
        value: '',
        type: 'default',
        employee_id: '',
        contract_id: '',
      })
    }
  }, [rate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const payload = {
        value: parseFloat(formData.value),
        employee_id: null,
        contract_id: null,
      }

      if (formData.type === 'employee') {
        payload.employee_id = formData.employee_id ? parseInt(formData.employee_id) : null
      } else if (formData.type === 'contract') {
        payload.contract_id = formData.contract_id ? parseInt(formData.contract_id) : null
      }

      if (rate) {
        await api.put(`/rates/${rate.id}`, payload)
      } else {
        await api.post('/rates', payload)
      }
      onClose()
    } catch (err) {
      setError(getErrorMessage(err, 'Ошибка при сохранении ставки'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-jira-border">
          <h2 className="text-xl font-semibold text-jira-gray">
            {rate ? 'Редактировать ставку' : 'Новая ставка'}
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Значение ставки *
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                required
                value={formData.value}
                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
                placeholder="Например, 4000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Тип ставки *
              </label>
              <select
                value={formData.type}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    type: e.target.value,
                    employee_id: '',
                    contract_id: '',
                  })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
              >
                <option value="default">Дефолтная (по умолчанию)</option>
                <option value="employee">Индивидуальная для юриста</option>
                <option value="contract">По договору</option>
              </select>
            </div>
          </div>

          {formData.type === 'employee' && (
            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Юрист *
              </label>
              <select
                required
                value={formData.employee_id}
                onChange={(e) =>
                  setFormData({ ...formData, employee_id: e.target.value })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
              >
                <option value="">Выберите юриста</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name} ({emp.email})
                  </option>
                ))}
              </select>
            </div>
          )}

          {formData.type === 'contract' && (
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
                {contracts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.number} — {c.client?.name || ''}
                  </option>
                ))}
              </select>
            </div>
          )}

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
              {loading ? 'Сохранение...' : rate ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RateModal


