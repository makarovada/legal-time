import { useEffect, useState } from 'react'
import api from '../services/api'
import { Plus, Edit, Trash2 } from 'lucide-react'
import ClientModal from '../components/ClientModal'

const Clients = () => {
  const [clients, setClients] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingClient, setEditingClient] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const response = await api.get('/clients')
      // Убеждаемся, что данные - массив
      const clientsData = Array.isArray(response.data) ? response.data : []
      
      console.log('Clients - Fetched data:', {
        clients: clientsData.length,
        clientsSample: clientsData[0],
        rawResponse: response.data
      })
      
      setClients(clientsData)
    } catch (error) {
      console.error('Error fetching clients:', error)
      console.error('Error response:', error.response?.data)
      // При ошибке устанавливаем пустой массив
      setClients([])
      alert('Ошибка при загрузке данных: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingClient(null)
    setIsModalOpen(true)
  }

  const handleEdit = (client) => {
    setEditingClient(client)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить этого клиента?')) {
      return
    }
    try {
      await api.delete(`/clients/${id}`)
      fetchData()
    } catch (error) {
      console.error('Error deleting client:', error)
      alert('Ошибка при удалении клиента')
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingClient(null)
    fetchData()
  }

  if (loading) {
    return <div className="text-jira-gray">Загрузка...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-jira-gray">Клиенты</h1>
          <p className="text-sm text-jira-gray mt-1">
            Управление клиентами
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors"
        >
          <Plus size={20} />
          <span>Добавить клиента</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-jira-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-jira-gray-light">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Название
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Тип
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-jira-border">
              {clients.length === 0 ? (
                <tr>
                  <td colSpan="3" className="px-6 py-4 text-center text-jira-gray">
                    Нет клиентов. Создайте первого клиента.
                  </td>
                </tr>
              ) : (
                clients.map((client) => (
                  <tr key={client.id} className="hover:bg-jira-gray-light">
                    <td className="px-6 py-4 text-sm font-medium text-jira-gray">
                      {client.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          client.type === 'legal'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {client.type === 'legal' ? 'Юридическое лицо' : 'Физическое лицо'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(client)}
                          className="text-jira-blue hover:text-jira-blue-dark"
                          title="Редактировать"
                        >
                          <Edit size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(client.id)}
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
        <ClientModal client={editingClient} onClose={handleModalClose} />
      )}
    </div>
  )
}

export default Clients

