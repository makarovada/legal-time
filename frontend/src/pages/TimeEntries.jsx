import { useEffect, useState } from 'react'
import { format } from 'date-fns'
import api from '../services/api'
import { Plus, Edit, Trash2, CheckCircle } from 'lucide-react'
import TimeEntryModal from '../components/TimeEntryModal'

const TimeEntries = () => {
  const [entries, setEntries] = useState([])
  const [matters, setMatters] = useState([])
  const [activityTypes, setActivityTypes] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingEntry, setEditingEntry] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [entriesRes, mattersRes, activityTypesRes] = await Promise.all([
        api.get('/time-entries'),
        api.get('/matters'),
        api.get('/activity-types'),
      ])
      // Убеждаемся, что данные - массивы
      const entriesData = Array.isArray(entriesRes.data) ? entriesRes.data : []
      const mattersData = Array.isArray(mattersRes.data) ? mattersRes.data : []
      const activityTypesData = Array.isArray(activityTypesRes.data) ? activityTypesRes.data : []
      
      console.log('Fetched data:', {
        entries: entriesData.length,
        matters: mattersData.length,
        activityTypes: activityTypesData.length,
        entriesSample: entriesData[0],
        mattersSample: mattersData[0],
        activityTypesSample: activityTypesData[0]
      })
      
      setEntries(entriesData)
      setMatters(mattersData)
      setActivityTypes(activityTypesData)
    } catch (error) {
      console.error('Error fetching data:', error)
      console.error('Error response:', error.response?.data)
      // При ошибке устанавливаем пустые массивы
      setEntries([])
      setMatters([])
      setActivityTypes([])
      alert('Ошибка при загрузке данных: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingEntry(null)
    setIsModalOpen(true)
  }

  const handleEdit = (entry) => {
    setEditingEntry(entry)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту запись?')) {
      return
    }
    try {
      await api.delete(`/time-entries/${id}`)
      fetchData()
    } catch (error) {
      console.error('Error deleting entry:', error)
      alert('Ошибка при удалении записи')
    }
  }

  const handleApprove = async (id) => {
    try {
      await api.patch(`/time-entries/${id}/approve`)
      fetchData()
    } catch (error) {
      console.error('Error approving entry:', error)
      alert('Ошибка при одобрении записи')
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingEntry(null)
    fetchData()
  }

  const getMatterName = (matterId) => {
    const matter = matters.find((m) => m.id === matterId)
    return matter ? `${matter.code} - ${matter.name}` : 'Неизвестно'
  }

  const getActivityTypeName = (activityTypeId) => {
    const activity = activityTypes.find((a) => a.id === activityTypeId)
    return activity ? activity.name : 'Неизвестно'
  }

  if (loading) {
    return <div className="text-jira-gray">Загрузка...</div>
  }

  // Убеждаемся, что entries - массив
  const entriesArray = Array.isArray(entries) ? entries : []
  const totalHours = entriesArray.reduce((sum, entry) => sum + (entry.hours || 0), 0)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-jira-gray">Учёт времени</h1>
          <p className="text-sm text-jira-gray mt-1">
            Всего часов: <span className="font-semibold">{totalHours.toFixed(1)}</span>
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors"
        >
          <Plus size={20} />
          <span>Добавить запись</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-jira-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-jira-gray-light">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Дата
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Дело
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Тип активности
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Часы
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Описание
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Статус
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-jira-border">
              {entriesArray.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-4 text-center text-jira-gray">
                    Нет записей. Создайте первую запись времени.
                  </td>
                </tr>
              ) : (
                entriesArray.map((entry) => (
                  <tr key={entry.id} className="hover:bg-jira-gray-light">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-jira-gray">
                      {format(new Date(entry.date), 'dd MMM yyyy')}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {getMatterName(entry.matter_id)}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {getActivityTypeName(entry.activity_type_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-jira-gray">
                      {entry.hours}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray max-w-xs truncate">
                      {entry.description || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          entry.status === 'approved'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {entry.status === 'approved' ? 'Одобрено' : 'Черновик'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(entry)}
                          className="text-jira-blue hover:text-jira-blue-dark"
                          title="Редактировать"
                        >
                          <Edit size={16} />
                        </button>
                        {entry.status === 'draft' && (
                          <button
                            onClick={() => handleApprove(entry.id)}
                            className="text-green-600 hover:text-green-700"
                            title="Одобрить"
                          >
                            <CheckCircle size={16} />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(entry.id)}
                          className="text-red-600 hover:text-red-700"
                          title="Удалить"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <TimeEntryModal
          entry={editingEntry}
          matters={matters}
          activityTypes={activityTypes}
          onClose={handleModalClose}
        />
      )}
    </div>
  )
}

export default TimeEntries

