import { useEffect, useState } from 'react'
import { format } from 'date-fns'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Edit, Trash2, CheckCircle, Filter, X } from 'lucide-react'
import TimeEntryModal from '../components/TimeEntryModal'

const TimeEntries = () => {
  const { user } = useAuth()
  const isSeniorOrAdmin = user?.role === 'senior_lawyer' || user?.role === 'admin'
  
  const [activeTab, setActiveTab] = useState('my') // 'my' или 'pending'
  const [entries, setEntries] = useState([])
  const [matters, setMatters] = useState([])
  const [activityTypes, setActivityTypes] = useState([])
  const [employees, setEmployees] = useState([])
  const [clients, setClients] = useState([])
  const [contracts, setContracts] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingEntry, setEditingEntry] = useState(null)
  
  // Фильтры для вкладки "На одобрение"
  const [filters, setFilters] = useState({
    employeeId: '',
    startDate: '',
    endDate: '',
    status: 'draft',
  })
  const [showFilters, setShowFilters] = useState(false)

  // Фильтры для вкладки "Отчёт"
  const [reportFilters, setReportFilters] = useState({
    employeeId: '',
    clientId: '',
    contractId: '',
    matterId: '',
    startDate: '',
    endDate: '',
  })
  const [reportDownloading, setReportDownloading] = useState(false)

  useEffect(() => {
    fetchData()
    if (isSeniorOrAdmin) {
      fetchEmployees()
    }
  }, [])

  useEffect(() => {
    if (activeTab === 'my') {
      fetchMyEntries()
    } else if (activeTab === 'pending' && isSeniorOrAdmin) {
      fetchPendingEntries()
    }
  }, [activeTab])

  const fetchData = async () => {
    try {
      const [mattersRes, activityTypesRes, clientsRes, contractsRes] = await Promise.all([
        api.get('/matters'),
        api.get('/activity-types'),
        api.get('/clients'),
        api.get('/contracts'),
      ])
      const mattersData = Array.isArray(mattersRes.data) ? mattersRes.data : []
      const activityTypesData = Array.isArray(activityTypesRes.data) ? activityTypesRes.data : []
      const clientsData = Array.isArray(clientsRes.data) ? clientsRes.data : []
      const contractsData = Array.isArray(contractsRes.data) ? contractsRes.data : []

      setMatters(mattersData)
      setActivityTypes(activityTypesData)
      setClients(clientsData)
      setContracts(contractsData)
    } catch (error) {
      console.error('Error fetching data:', error)
      setMatters([])
      setActivityTypes([])
    }
  }

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/employees')
      setEmployees(Array.isArray(response.data) ? response.data : [])
    } catch (error) {
      console.error('Error fetching employees:', error)
      setEmployees([])
    }
  }

  const fetchMyEntries = async () => {
    try {
      setLoading(true)
      const response = await api.get('/time-entries')
      const entriesData = Array.isArray(response.data) ? response.data : []
      setEntries(entriesData)
    } catch (error) {
      console.error('Error fetching my entries:', error)
      setEntries([])
      alert('Ошибка при загрузке данных: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const fetchPendingEntries = async () => {
    try {
      setLoading(true)
      const response = await api.get('/time-entries/pending')
      const entriesData = Array.isArray(response.data) ? response.data : []
      setEntries(entriesData)
    } catch (error) {
      console.error('Error fetching pending entries:', error)
      setEntries([])
      if (error.response?.status !== 403) {
        alert('Ошибка при загрузке данных: ' + (error.response?.data?.detail || error.message))
      }
    } finally {
      setLoading(false)
    }
  }

  const applyFilters = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filters.employeeId) params.append('employee_id', filters.employeeId)
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.status) params.append('status', filters.status)
      
      const response = await api.get(`/time-entries/filter?${params.toString()}`)
      const entriesData = Array.isArray(response.data) ? response.data : []
      setEntries(entriesData)
      setShowFilters(false)
    } catch (error) {
      console.error('Error filtering entries:', error)
      setEntries([])
      alert('Ошибка при фильтрации: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const clearFilters = () => {
    setFilters({
      employeeId: '',
      startDate: '',
      endDate: '',
      status: 'draft',
    })
    fetchPendingEntries()
  }

  const handleReportDownload = async () => {
    setReportDownloading(true)
    try {
      const params = new URLSearchParams()
      if (reportFilters.employeeId) params.append('employee_id', reportFilters.employeeId)
      if (reportFilters.clientId) params.append('client_id', reportFilters.clientId)
      if (reportFilters.contractId) params.append('contract_id', reportFilters.contractId)
      if (reportFilters.matterId) params.append('matter_id', reportFilters.matterId)
      if (reportFilters.startDate) params.append('start_date', reportFilters.startDate)
      if (reportFilters.endDate) params.append('end_date', reportFilters.endDate)

      const response = await api.get(`/time-entries/report?${params.toString()}`, {
        responseType: 'blob',
      })

      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'time_entries_report.xlsx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading report:', error)
      alert('Ошибка при формировании отчёта: ' + (error.response?.data?.detail || error.message))
    } finally {
      setReportDownloading(false)
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
      if (activeTab === 'my') {
        fetchMyEntries()
      } else {
        fetchPendingEntries()
      }
    } catch (error) {
      console.error('Error deleting entry:', error)
      alert('Ошибка при удалении записи: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleApprove = async (id, employeeId) => {
    // Проверка: старший юрист не может одобрить свой таймшит через обычный интерфейс
    if (user?.role === 'senior_lawyer' && employeeId === user.id) {
      alert('Вы не можете одобрить свой собственный таймшит через этот интерфейс. Используйте фильтр для просмотра всех таймшитов.')
      return
    }
    
    try {
      await api.patch(`/time-entries/${id}/approve`)
      if (activeTab === 'my') {
        fetchMyEntries()
      } else {
        fetchPendingEntries()
      }
    } catch (error) {
      console.error('Error approving entry:', error)
      alert('Ошибка при одобрении записи: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingEntry(null)
    if (activeTab === 'my') {
      fetchMyEntries()
    } else {
      fetchPendingEntries()
    }
  }

  const getMatterName = (matterId) => {
    const matter = matters.find((m) => m.id === matterId)
    return matter ? `${matter.code} - ${matter.name}` : 'Неизвестно'
  }

  const getActivityTypeName = (activityTypeId) => {
    const activity = activityTypes.find((a) => a.id === activityTypeId)
    return activity ? activity.name : 'Неизвестно'
  }

  const getEmployeeName = (employeeId) => {
    const employee = employees.find((e) => e.id === employeeId)
    return employee ? employee.name : 'Неизвестно'
  }

  if (loading && entries.length === 0) {
    return <div className="text-jira-gray">Загрузка...</div>
  }

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

      {/* Вкладки для старших юристов и админов */}
      {isSeniorOrAdmin && (
        <div className="border-b border-jira-border">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => {
                setActiveTab('my')
                fetchMyEntries()
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'my'
                  ? 'border-jira-blue text-jira-blue'
                  : 'border-transparent text-jira-gray hover:text-jira-gray hover:border-jira-gray'
              }`}
            >
              Мои таймшиты
            </button>
            <button
              onClick={() => {
                setActiveTab('pending')
                fetchPendingEntries()
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'pending'
                  ? 'border-jira-blue text-jira-blue'
                  : 'border-transparent text-jira-gray hover:text-jira-gray hover:border-jira-gray'
              }`}
            >
              На одобрение
            </button>
            <button
              onClick={() => {
                setActiveTab('report')
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'report'
                  ? 'border-jira-blue text-jira-blue'
                  : 'border-transparent text-jira-gray hover:text-jira-gray hover:border-jira-gray'
              }`}
            >
              Отчёт
            </button>
          </nav>
        </div>
      )}

      {/* Фильтры для вкладки "На одобрение" */}
      {isSeniorOrAdmin && activeTab === 'pending' && (
        <div className="bg-white rounded-lg shadow-sm border border-jira-border p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-jira-gray">Фильтры</h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-2 px-3 py-1 text-sm text-jira-gray hover:text-jira-blue border border-jira-border rounded-md"
              >
                <Filter size={16} />
                <span>{showFilters ? 'Скрыть фильтры' : 'Показать фильтры'}</span>
              </button>
              {(filters.employeeId || filters.startDate || filters.endDate) && (
                <button
                  onClick={clearFilters}
                  className="flex items-center space-x-2 px-3 py-1 text-sm text-red-600 hover:text-red-700 border border-red-300 rounded-md"
                >
                  <X size={16} />
                  <span>Очистить</span>
                </button>
              )}
            </div>
          </div>
          
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-jira-gray mb-1">
                  Сотрудник
                </label>
                <select
                  value={filters.employeeId}
                  onChange={(e) => setFilters({ ...filters, employeeId: e.target.value })}
                  className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
                >
                  <option value="">Все сотрудники</option>
                  {employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-jira-gray mb-1">
                  Дата начала
                </label>
                <input
                  type="date"
                  value={filters.startDate}
                  onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
                  className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-jira-gray mb-1">
                  Дата окончания
                </label>
                <input
                  type="date"
                  value={filters.endDate}
                  onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
                  className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
                />
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={applyFilters}
                  className="w-full px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors"
                >
                  Применить
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Вкладка "Отчёт" для старших юристов и админов */}
      {isSeniorOrAdmin && activeTab === 'report' && (
        <div className="bg-white rounded-lg shadow-sm border border-jira-border p-6 space-y-4">
          <h2 className="text-lg font-semibold text-jira-gray">Фильтры для отчёта (одобренные таймшиты)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Сотрудник
              </label>
              <select
                value={reportFilters.employeeId}
                onChange={(e) =>
                  setReportFilters({ ...reportFilters, employeeId: e.target.value })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
              >
                <option value="">Все сотрудники</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name} ({emp.email})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Клиент
              </label>
              <select
                value={reportFilters.clientId}
                onChange={(e) =>
                  setReportFilters({ ...reportFilters, clientId: e.target.value })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
              >
                <option value="">Все клиенты</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Договор
              </label>
              <select
                value={reportFilters.contractId}
                onChange={(e) =>
                  setReportFilters({ ...reportFilters, contractId: e.target.value })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
              >
                <option value="">Все договоры</option>
                {contracts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.number}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Дело
              </label>
              <select
                value={reportFilters.matterId}
                onChange={(e) =>
                  setReportFilters({ ...reportFilters, matterId: e.target.value })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
              >
                <option value="">Все дела</option>
                {matters.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.code} - {m.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Дата начала
              </label>
              <input
                type="date"
                value={reportFilters.startDate}
                onChange={(e) =>
                  setReportFilters({ ...reportFilters, startDate: e.target.value })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-jira-gray mb-1">
                Дата окончания
              </label>
              <input
                type="date"
                value={reportFilters.endDate}
                onChange={(e) =>
                  setReportFilters({ ...reportFilters, endDate: e.target.value })
                }
                className="w-full px-3 py-2 border border-jira-border rounded-md text-sm"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleReportDownload}
              disabled={reportDownloading}
              className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{reportDownloading ? 'Формирование отчёта...' : 'Скачать отчёт'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Основная таблица таймшитов (для вкладок "Мои таймшиты" и "На одобрение") */}
      {activeTab !== 'report' && (
        <div className="bg-white rounded-lg shadow-sm border border-jira-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
            <thead className="bg-jira-gray-light">
              <tr>
                {isSeniorOrAdmin && activeTab === 'pending' && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                    Сотрудник
                  </th>
                )}
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
                  Ставка
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
                  <td colSpan={isSeniorOrAdmin && activeTab === 'pending' ? 8 : 7} className="px-6 py-4 text-center text-jira-gray">
                    {activeTab === 'pending' ? 'Нет записей на одобрение' : 'Нет записей. Создайте первую запись времени.'}
                  </td>
                </tr>
              ) : (
                entriesArray.map((entry) => (
                  <tr key={entry.id} className="hover:bg-jira-gray-light">
                    {isSeniorOrAdmin && activeTab === 'pending' && (
                      <td className="px-6 py-4 text-sm text-jira-gray">
                        {getEmployeeName(entry.employee_id)}
                      </td>
                    )}
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-jira-gray">
                      {entry.rate?.value ?? entry.rate_value ?? '-'}
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
                        {entry.status === 'draft' && isSeniorOrAdmin && (
                          <button
                            onClick={() => handleApprove(entry.id, entry.employee_id)}
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
      )}

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

