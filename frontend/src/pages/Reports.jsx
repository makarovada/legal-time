import { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { FileSpreadsheet } from 'lucide-react'

const Reports = () => {
  const { user } = useAuth()
  const isSeniorOrAdmin = user?.role === 'admin' || user?.role === 'senior_lawyer'

  const [employees, setEmployees] = useState([])
  const [clients, setClients] = useState([])
  const [contracts, setContracts] = useState([])
  const [matters, setMatters] = useState([])

  const [filters, setFilters] = useState({
    employeeId: '',
    clientId: '',
    contractId: '',
    matterId: '',
    startDate: '',
    endDate: '',
  })

  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    if (!isSeniorOrAdmin) {
      setLoading(false)
      return
    }

    const fetchAll = async () => {
      try {
        const [employeesRes, clientsRes, contractsRes, mattersRes] = await Promise.all([
          api.get('/employees'),
          api.get('/clients'),
          api.get('/contracts'),
          api.get('/matters'),
        ])

        setEmployees(Array.isArray(employeesRes.data) ? employeesRes.data : [])
        setClients(Array.isArray(clientsRes.data) ? clientsRes.data : [])
        setContracts(Array.isArray(contractsRes.data) ? contractsRes.data : [])
        setMatters(Array.isArray(mattersRes.data) ? mattersRes.data : [])
      } catch (error) {
        console.error('Error loading report filters:', error)
        alert(
          'Ошибка при загрузке данных для отчёта: ' +
            (error.response?.data?.detail || error.message)
        )
      } finally {
        setLoading(false)
      }
    }

    fetchAll()
  }, [isSeniorOrAdmin])

  const handleDownload = async () => {
    setDownloading(true)
    try {
      const params = new URLSearchParams()
      if (filters.employeeId) params.append('employee_id', filters.employeeId)
      if (filters.clientId) params.append('client_id', filters.clientId)
      if (filters.contractId) params.append('contract_id', filters.contractId)
      if (filters.matterId) params.append('matter_id', filters.matterId)
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)

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
      setDownloading(false)
    }
  }

  if (!isSeniorOrAdmin) {
    return (
      <div className="text-jira-gray">
        У вас нет прав для формирования отчёта.
      </div>
    )
  }

  if (loading) {
    return <div className="text-jira-gray">Загрузка данных для отчёта...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-jira-gray">Отчёт по времени</h1>
          <p className="text-sm text-jira-gray mt-1">
            Формирование Excel-отчёта по одобренным таймшитам
          </p>
        </div>
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <FileSpreadsheet size={20} />
          <span>{downloading ? 'Формирование...' : 'Скачать отчёт'}</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-jira-border p-6 space-y-4">
        <h2 className="text-lg font-semibold text-jira-gray mb-2">Фильтры</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
              value={filters.clientId}
              onChange={(e) => setFilters({ ...filters, clientId: e.target.value })}
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
              value={filters.contractId}
              onChange={(e) => setFilters({ ...filters, contractId: e.target.value })}
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
              value={filters.matterId}
              onChange={(e) => setFilters({ ...filters, matterId: e.target.value })}
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
        </div>
      </div>
    </div>
  )
}

export default Reports


