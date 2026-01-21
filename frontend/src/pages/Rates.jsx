import { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Edit, Trash2 } from 'lucide-react'
import RateModal from '../components/RateModal'

const Rates = () => {
  const { user } = useAuth()
  const isSeniorOrAdmin = user?.role === 'admin' || user?.role === 'senior_lawyer'

  const [rates, setRates] = useState([])
  const [employees, setEmployees] = useState([])
  const [contracts, setContracts] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingRate, setEditingRate] = useState(null)

  useEffect(() => {
    fetchAll()
  }, [])

  const fetchAll = async () => {
    try {
      setLoading(true)
      const [ratesRes, employeesRes, contractsRes] = await Promise.all([
        api.get('/rates'),
        api.get('/employees'),
        api.get('/contracts'),
      ])

      setRates(Array.isArray(ratesRes.data) ? ratesRes.data : [])
      setEmployees(Array.isArray(employeesRes.data) ? employeesRes.data : [])
      setContracts(Array.isArray(contractsRes.data) ? contractsRes.data : [])
    } catch (error) {
      console.error('Error fetching rates:', error)
      setRates([])
      if (error.response?.status === 403) {
        alert('Недостаточно прав для просмотра ставок')
      } else {
        alert('Ошибка при загрузке ставок: ' + (error.response?.data?.detail || error.message))
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingRate(null)
    setIsModalOpen(true)
  }

  const handleEdit = (rate) => {
    setEditingRate(rate)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту ставку?')) {
      return
    }
    try {
      await api.delete(`/rates/${id}`)
      fetchAll()
    } catch (error) {
      console.error('Error deleting rate:', error)
      alert('Ошибка при удалении ставки: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingRate(null)
    fetchAll()
  }

  const getEmployeeName = (employeeId) => {
    if (!employeeId) return '-'
    const emp = employees.find((e) => e.id === employeeId)
    return emp ? `${emp.name} (${emp.email})` : employeeId
  }

  const getContractLabel = (contractId) => {
    if (!contractId) return '-'
    const c = contracts.find((c) => c.id === contractId)
    if (!c) return contractId
    return c.number
  }

  const getScopeLabel = (rate) => {
    if (rate.contract_id) return 'По договору'
    if (rate.employee_id) return 'Индивидуальная'
    return 'По умолчанию'
  }

  if (!isSeniorOrAdmin) {
    return (
      <div className="text-jira-gray">
        У вас нет прав для управления ставками.
      </div>
    )
  }

  if (loading) {
    return <div className="text-jira-gray">Загрузка...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-jira-gray">Ставки</h1>
          <p className="text-sm text-jira-gray mt-1">
            Управление ставками по умолчанию, индивидуальными и по договорам
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors"
        >
          <Plus size={20} />
          <span>Добавить ставку</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-jira-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-jira-gray-light">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Тип
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Юрист
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Договор
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Ставка
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-jira-border">
              {rates.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-jira-gray">
                    Ставки не найдены.
                  </td>
                </tr>
              ) : (
                rates.map((rate) => (
                  <tr key={rate.id} className="hover:bg-jira-gray-light">
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {getScopeLabel(rate)}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {getEmployeeName(rate.employee_id)}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {getContractLabel(rate.contract_id)}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-jira-gray">
                      {rate.value}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(rate)}
                          className="text-jira-blue hover:text-jira-blue-dark"
                          title="Редактировать"
                        >
                          <Edit size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(rate.id)}
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
        <RateModal
          rate={editingRate}
          employees={employees}
          contracts={contracts}
          onClose={handleModalClose}
        />
      )}
    </div>
  )
}

export default Rates


