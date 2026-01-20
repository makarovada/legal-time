import { useState, useEffect } from 'react'
import api from '../services/api'
import { X } from 'lucide-react'
import { getErrorMessage } from '../utils/errorHandler'

const TimeEntryModal = ({ entry, matters, activityTypes, onClose }) => {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    matter_id: '',
    activity_type_id: '',
    hours: '',
    description: '',
    rate_id: null,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (entry) {
      setFormData({
        date: entry.date,
        matter_id: entry.matter_id,
        activity_type_id: entry.activity_type_id,
        hours: entry.hours,
        description: entry.description || '',
        rate_id: entry.rate_id || null,
      })
    }
  }, [entry])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = {
        ...formData,
        hours: parseFloat(formData.hours),
        matter_id: parseInt(formData.matter_id),
        activity_type_id: parseInt(formData.activity_type_id),
      }

      if (entry) {
        await api.put(`/time-entries/${entry.id}`, data)
      } else {
        await api.post('/time-entries', data)
      }
      onClose()
    } catch (err) {
      setError(getErrorMessage(err, 'Ошибка при сохранении записи'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-jira-border">
          <h2 className="text-xl font-semibold text-jira-gray">
            {entry ? 'Редактировать запись' : 'Новая запись времени'}
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
                Дата *
              </label>
              <input
                type="date"
                required
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Часы *
              </label>
              <input
                type="number"
                step="0.25"
                min="0"
                required
                value={formData.hours}
                onChange={(e) => setFormData({ ...formData, hours: e.target.value })}
                className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
                placeholder="0.0"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Дело *
            </label>
            <select
              required
              value={formData.matter_id}
              onChange={(e) => setFormData({ ...formData, matter_id: e.target.value })}
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
            >
              <option value="">Выберите дело</option>
              {matters.map((matter) => (
                <option key={matter.id} value={matter.id}>
                  {matter.code} - {matter.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-jira-gray mb-1">
              Тип активности *
            </label>
            <select
              required
              value={formData.activity_type_id}
              onChange={(e) =>
                setFormData({ ...formData, activity_type_id: e.target.value })
              }
              className="w-full px-3 py-2 border border-jira-border rounded-md focus:outline-none focus:ring-jira-blue focus:border-jira-blue"
            >
              <option value="">Выберите тип активности</option>
              {activityTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
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
              placeholder="Опишите выполненную работу..."
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
              {loading ? 'Сохранение...' : entry ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default TimeEntryModal

