import { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { Plus, Edit, Trash2 } from 'lucide-react'
import EmployeeModal from '../components/EmployeeModal'

const Employees = () => {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const response = await api.get('/employees')
      const employeesData = Array.isArray(response.data) ? response.data : []
      setEmployees(employeesData)
    } catch (error) {
      console.error('Error fetching employees:', error)
      setEmployees([])
      alert('Ошибка при загрузке данных: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingEmployee(null)
    setIsModalOpen(true)
  }

  const handleEdit = (employee) => {
    setEditingEmployee(employee)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить этого сотрудника?')) {
      return
    }
    try {
      await api.delete(`/employees/${id}`)
      fetchData()
    } catch (error) {
      console.error('Error deleting employee:', error)
      alert('Ошибка при удалении сотрудника: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingEmployee(null)
    fetchData()
  }

  const getRoleLabel = (role) => {
    const roleLabels = {
      lawyer: 'Юрист',
      senior_lawyer: 'Старший юрист',
      admin: 'Администратор',
    }
    return roleLabels[role] || role
  }

  const getRoleBadgeColor = (role) => {
    const colors = {
      lawyer: 'bg-blue-100 text-blue-800',
      senior_lawyer: 'bg-purple-100 text-purple-800',
      admin: 'bg-red-100 text-red-800',
    }
    return colors[role] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return <div className="text-jira-gray">Загрузка...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-jira-gray">Сотрудники</h1>
          <p className="text-sm text-jira-gray mt-1">
            {isAdmin ? 'Управление сотрудниками и их ролями' : 'Список сотрудников'}
          </p>
        </div>
        {isAdmin && (
          <button
            onClick={handleCreate}
            className="flex items-center space-x-2 px-4 py-2 bg-jira-blue text-white rounded-md hover:bg-jira-blue-dark transition-colors"
          >
            <Plus size={20} />
            <span>Добавить сотрудника</span>
          </button>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-jira-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-jira-gray-light">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Имя
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Роль
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-jira-gray uppercase tracking-wider">
                  {isAdmin ? 'Действия' : ''}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-jira-border">
              {employees.length === 0 ? (
                <tr>
                  <td colSpan={isAdmin ? 4 : 3} className="px-6 py-4 text-center text-jira-gray">
                    Нет сотрудников.
                  </td>
                </tr>
              ) : (
                employees.map((employee) => (
                  <tr key={employee.id} className="hover:bg-jira-gray-light">
                    <td className="px-6 py-4 text-sm font-medium text-jira-gray">
                      {employee.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
                      {employee.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getRoleBadgeColor(
                          employee.role
                        )}`}
                      >
                        {getRoleLabel(employee.role)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {isAdmin && (
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleEdit(employee)}
                            className="text-jira-blue hover:text-jira-blue-dark"
                            title="Редактировать"
                          >
                            <Edit size={16} />
                          </button>
                          <button
                            onClick={() => handleDelete(employee.id)}
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
        <EmployeeModal employee={editingEmployee} onClose={handleModalClose} />
      )}
    </div>
  )
}

export default Employees

