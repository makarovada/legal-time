import { useEffect, useState } from 'react'
import api from '../services/api'
import { Plus, Edit, Trash2 } from 'lucide-react'
import MatterModal from '../components/MatterModal'

const Matters = () => {
  const [matters, setMatters] = useState([])
  const [contracts, setContracts] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingMatter, setEditingMatter] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [mattersRes, contractsRes] = await Promise.all([
        api.get('/matters'),
        api.get('/contracts'),
      ])
      // Убеждаемся, что данные - массивы
      const mattersData = Array.isArray(mattersRes.data) ? mattersRes.data : []
      const contractsData = Array.isArray(contractsRes.data) ? contractsRes.data : []
      
      console.log('Matters - Fetched data:', {
        matters: mattersData.length,
        contracts: contractsData.length,
        mattersSample: mattersData[0],
        contractsSample: contractsData[0]
      })
      
      setMatters(mattersData)
      setContracts(contractsData)
    } catch (error) {
      console.error('Error fetching data:', error)
      console.error('Error response:', error.response?.data)
      // При ошибке устанавливаем пустые массивы
      setMatters([])
      setContracts([])
      alert('Ошибка при загрузке данных: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingMatter(null)
    setIsModalOpen(true)
  }

  const handleEdit = (matter) => {
    setEditingMatter(matter)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить это дело?')) {
      return
    }
    try {
      await api.delete(`/matters/${id}`)
      fetchData()
    } catch (error) {
      console.error('Error deleting matter:', error)
      alert('Ошибка при удалении дела')
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingMatter(null)
    fetchData()
  }

  const getContractName = (contractId) => {
    const contract = contracts.find((c) => c.id === contractId)
    return contract ? contract.number || `Договор #${contract.id}` : 'Неизвестно'
  }

  if (loading) {
    return <div className="text-jira-gray">Загрузка...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-jira-gray">Дела</h1>
          <p className="text-sm text-jira-gray mt-1">
            Управление юридическими делами
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors"
        >
          <Plus size={20} />
          <span>Добавить дело</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-jira-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-jira-gray-light">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Код
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Название
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Договор
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Описание
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-jira-border">
              {matters.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-jira-gray">
                    Нет дел. Создайте первое дело.
                  </td>
                </tr>
              ) : (
                matters.map((matter) => (
                  <tr key={matter.id} className="hover:bg-jira-gray-light">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-jira-gray">
                      {matter.code}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {matter.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {getContractName(matter.contract_id)}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray max-w-xs truncate">
                      {matter.description || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(matter)}
                          className="text-jira-blue hover:text-jira-blue-dark"
                          title="Редактировать"
                        >
                          <Edit size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(matter.id)}
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
        <MatterModal
          matter={editingMatter}
          contracts={contracts}
          onClose={handleModalClose}
        />
      )}
    </div>
  )
}

export default Matters

