import { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Edit, Trash2 } from 'lucide-react'
import ContractModal from '../components/ContractModal'

const Contracts = () => {
  const { user } = useAuth()
  const isSeniorOrAdmin = user?.role === 'senior_lawyer' || user?.role === 'admin'
  const [contracts, setContracts] = useState([])
  const [clients, setClients] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingContract, setEditingContract] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [contractsRes, clientsRes] = await Promise.all([
        api.get('/contracts'),
        api.get('/clients'),
      ])
      // Убеждаемся, что данные - массивы
      const contractsData = Array.isArray(contractsRes.data) ? contractsRes.data : []
      const clientsData = Array.isArray(clientsRes.data) ? clientsRes.data : []
      
      console.log('Contracts - Fetched data:', {
        contracts: contractsData.length,
        clients: clientsData.length,
        contractsSample: contractsData[0],
        clientsSample: clientsData[0]
      })
      
      setContracts(contractsData)
      setClients(clientsData)
    } catch (error) {
      console.error('Error fetching data:', error)
      console.error('Error response:', error.response?.data)
      // При ошибке устанавливаем пустые массивы
      setContracts([])
      setClients([])
      alert('Ошибка при загрузке данных: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingContract(null)
    setIsModalOpen(true)
  }

  const handleEdit = (contract) => {
    setEditingContract(contract)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить этот договор?')) {
      return
    }
    try {
      await api.delete(`/contracts/${id}`)
      fetchData()
    } catch (error) {
      console.error('Error deleting contract:', error)
      alert('Ошибка при удалении договора')
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingContract(null)
    fetchData()
  }

  const getClientName = (clientId) => {
    const client = clients.find((c) => c.id === clientId)
    return client ? client.name : 'Неизвестно'
  }

  if (loading) {
    return <div className="text-jira-gray">Загрузка...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-jira-gray">Договоры</h1>
          <p className="text-sm text-jira-gray mt-1">
            Управление договорами с клиентами
          </p>
        </div>
        {isSeniorOrAdmin && (
          <button
            onClick={handleCreate}
            className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors"
          >
            <Plus size={20} />
            <span>Добавить договор</span>
          </button>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-jira-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-jira-gray-light">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Номер
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Клиент
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Дата
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-jira-gray uppercase tracking-wider">
                  {isSeniorOrAdmin ? 'Действия' : ''}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-jira-border">
              {contracts.length === 0 ? (
                <tr>
                  <td colSpan={isSeniorOrAdmin ? 4 : 3} className="px-6 py-4 text-center text-jira-gray">
                    Нет договоров. Создайте первый договор.
                  </td>
                </tr>
              ) : (
                contracts.map((contract) => (
                  <tr key={contract.id} className="hover:bg-jira-gray-light">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-jira-gray">
                      {contract.number || `Договор #${contract.id}`}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {getClientName(contract.client_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-jira-gray">
                      {contract.date
                        ? new Date(contract.date).toLocaleDateString('ru-RU')
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {isSeniorOrAdmin && (
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleEdit(contract)}
                            className="text-jira-blue hover:text-jira-blue-dark"
                            title="Редактировать"
                          >
                            <Edit size={16} />
                          </button>
                          <button
                            onClick={() => handleDelete(contract.id)}
                            className="text-red-600 hover:text-red-700"
                            title="Удалить"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <ContractModal
          contract={editingContract}
          clients={clients}
          onClose={handleModalClose}
        />
      )}
    </div>
  )
}

export default Contracts

