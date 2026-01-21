import { useEffect, useState } from 'react'
import api from '../services/api'
import { Clock, FileText, Users, TrendingUp, Calendar, CheckCircle2, XCircle, Smartphone, Bell, RefreshCw } from 'lucide-react'
import { format } from 'date-fns'

const Dashboard = () => {
  console.log('=== Dashboard: Component START ===')
  console.log('Dashboard: Component rendered')
  
  const [stats, setStats] = useState({
    totalHours: 0,
    totalEntries: 0,
    pendingEntries: 0,
    approvedEntries: 0,
  })
  const [recentEntries, setRecentEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [googleConnected, setGoogleConnected] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [googleStatusLoading, setGoogleStatusLoading] = useState(true)
  
  console.log('Dashboard: State initialized')

  useEffect(() => {
    console.log('Dashboard: useEffect triggered')
    fetchDashboardData()
    checkGoogleStatus()
  }, [])

  const checkGoogleStatus = async () => {
    console.log('Dashboard: checkGoogleStatus called')
    try {
      setGoogleStatusLoading(true)
      console.log('Dashboard: Making API request to /auth/google/status')
      const response = await api.get('/auth/google/status')
      console.log('Dashboard: Google status response:', response.data)
      setGoogleConnected(response.data.connected || false)
    } catch (error) {
      console.error('Dashboard: Error checking Google status:', error)
      console.error('Dashboard: Error response:', error.response?.data)
      console.error('Dashboard: Error message:', error.message)
      // При ошибке считаем, что не подключено, но блок все равно показываем
      setGoogleConnected(false)
    } finally {
      setGoogleStatusLoading(false)
      console.log('Dashboard: checkGoogleStatus completed, googleConnected:', googleConnected)
    }
  }

  const handleGoogleAuth = async () => {
    try {
      setGoogleLoading(true)
      const response = await api.get('/auth/google/authorize')
      // Перенаправляем на страницу авторизации Google
      window.location.href = response.data.authorization_url
    } catch (error) {
      console.error('Error initiating Google auth:', error)
      alert('Ошибка при подключении Google Calendar: ' + (error.response?.data?.detail || error.message))
      setGoogleLoading(false)
    }
  }

  const fetchDashboardData = async () => {
    try {
      const [entriesResponse] = await Promise.all([
        api.get('/time-entries?limit=10'),
      ])

      const entries = Array.isArray(entriesResponse.data) ? entriesResponse.data : []
      const totalHours = entries.reduce((sum, entry) => sum + (entry.hours || 0), 0)
      const pendingEntries = entries.filter((e) => e.status === 'draft').length
      const approvedEntries = entries.filter((e) => e.status === 'approved').length

      setStats({
        totalHours: totalHours.toFixed(1),
        totalEntries: entries.length,
        pendingEntries,
        approvedEntries,
      })
      setRecentEntries(entries.slice(0, 5))
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Не возвращаем ранний выход - показываем все сразу, даже во время загрузки
  // if (loading) {
  //   return <div className="text-jira-gray">Загрузка...</div>
  // }

  const statCards = [
    {
      title: 'Всего часов',
      value: stats.totalHours,
      icon: Clock,
      color: 'bg-blue-500',
    },
    {
      title: 'Всего записей',
      value: stats.totalEntries,
      icon: FileText,
      color: 'bg-green-500',
    },
    {
      title: 'На проверке',
      value: stats.pendingEntries,
      icon: TrendingUp,
      color: 'bg-yellow-500',
    },
    {
      title: 'Одобрено',
      value: stats.approvedEntries,
      icon: Users,
      color: 'bg-purple-500',
    },
  ]

  console.log('Dashboard: Rendering, googleStatusLoading:', googleStatusLoading, 'googleConnected:', googleConnected)
  console.log('Dashboard: Block should be visible NOW')
  console.log('Dashboard: About to render Google Calendar block')

  return (
    <div className="space-y-6">
      {loading && (
        <div className="text-jira-gray text-center py-4">Загрузка данных...</div>
      )}
      
      <div>
        <h1 className="text-2xl font-bold text-jira-gray">Дашборд</h1>
        <p className="text-sm text-jira-gray mt-1">
          Обзор вашей работы за последний период
        </p>
      </div>

      {/* Google Calendar Integration - ВСЕГДА показываем блок */}
      {(() => {
        console.log('Dashboard: Rendering Google Calendar block JSX')
        return (
          <div 
            className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6"
            style={{ display: 'block' }}
          >
            <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-white p-2 rounded-lg shadow-sm">
                <Calendar className="text-blue-600" size={24} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  Интеграция с Google Calendar
                </h2>
                <div className="flex items-center space-x-2 mt-1">
                  {googleStatusLoading ? (
                    <>
                      <RefreshCw className="text-gray-400 animate-spin" size={16} />
                      <span className="text-sm text-gray-600">Проверка статуса...</span>
                    </>
                  ) : googleConnected ? (
                    <>
                      <CheckCircle2 className="text-green-600" size={16} />
                      <span className="text-sm text-green-700 font-medium">Подключено</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="text-gray-400" size={16} />
                      <span className="text-sm text-gray-600">Не подключено</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {!googleStatusLoading && !googleConnected && (
              <div className="space-y-3 mb-4">
                <p className="text-sm text-gray-700 font-medium">Преимущества интеграции:</p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start space-x-2">
                    <Smartphone className="text-blue-500 mt-0.5" size={16} />
                    <span><strong>Доступ на всех устройствах</strong> — ваши задачи видны везде: телефон, планшет, компьютер</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <Bell className="text-blue-500 mt-0.5" size={16} />
                    <span><strong>Напоминания о встречах</strong> — никогда не забудете про важные события и дедлайны</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <RefreshCw className="text-blue-500 mt-0.5" size={16} />
                    <span><strong>Автоматическая синхронизация</strong> — записи времени автоматически появляются в календаре</span>
                  </li>
                </ul>
              </div>
            )}

            {!googleStatusLoading && googleConnected && (
              <div className="space-y-3 mb-4">
                <p className="text-sm text-gray-700">
                  Ваш Google Calendar подключен. Создан отдельный календарь "LegalTime" для ваших записей времени.
                </p>
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={async () => {
                      try {
                        const response = await api.post('/time-entries/sync-to-calendar')
                        alert(`Синхронизация завершена!\nСинхронизировано: ${response.data.synced}\nОшибок: ${response.data.failed}`)
                        fetchDashboardData()
                      } catch (error) {
                        console.error('Error syncing entries:', error)
                        alert('Ошибка при синхронизации: ' + (error.response?.data?.detail || error.message))
                      }
                    }}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm font-medium"
                  >
                    <RefreshCw size={16} />
                    <span>Синхронизировать в календарь</span>
                  </button>
                  <button
                    onClick={async () => {
                      if (window.confirm('Импортировать события из Google Calendar в таймшиты? Будут созданы новые записи для событий, которых еще нет в системе.')) {
                        try {
                          const response = await api.post('/time-entries/sync-from-calendar?days_back=30&days_forward=30')
                          alert(`Импорт завершен!\nСоздано: ${response.data.created}\nПропущено: ${response.data.skipped}\nОшибок: ${response.data.failed}`)
                          fetchDashboardData()
                        } catch (error) {
                          console.error('Error syncing from calendar:', error)
                          alert('Ошибка при импорте: ' + (error.response?.data?.detail || error.message))
                        }
                      }
                    }}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors text-sm font-medium"
                  >
                    <Calendar size={16} />
                    <span>Импортировать из календаря</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="ml-4">
            {googleStatusLoading ? (
              <div className="px-6 py-3 bg-gray-100 text-gray-600 rounded-lg text-sm">
                Загрузка...
              </div>
            ) : !googleConnected ? (
              <button
                onClick={handleGoogleAuth}
                disabled={googleLoading}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Calendar size={20} />
                <span>{googleLoading ? 'Подключение...' : 'Подключить Google Calendar'}</span>
              </button>
            ) : (
              <div className="flex flex-col items-end space-y-2">
                <div className="px-4 py-2 bg-green-100 text-green-800 rounded-lg text-sm font-medium">
                  ✓ Интеграция активна
                </div>
                <button
                  onClick={async () => {
                    if (window.confirm('Вы уверены, что хотите отключить Google Calendar?')) {
                      try {
                        await api.post('/auth/google/disconnect')
                        setGoogleConnected(false)
                        alert('Google Calendar отключен')
                      } catch (error) {
                        console.error('Error disconnecting Google:', error)
                        alert('Ошибка при отключении Google Calendar')
                      }
                    }
                  }}
                  className="text-sm text-red-600 hover:text-red-700 underline"
                >
                  Отключить
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
        )
      })()}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.title}
              className="bg-white rounded-lg shadow-sm border border-jira-border p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-jira-gray">{stat.title}</p>
                  <p className="text-2xl font-bold text-jira-gray mt-2">
                    {stat.value}
                  </p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Entries */}
      <div className="bg-white rounded-lg shadow-sm border border-jira-border">
        <div className="p-6 border-b border-jira-border">
          <h2 className="text-lg font-semibold text-jira-gray">Последние записи</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-jira-gray-light">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-jira-gray uppercase tracking-wider">
                  Дата
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
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-jira-border">
              {recentEntries.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-4 text-center text-jira-gray">
                    Нет записей
                  </td>
                </tr>
              ) : (
                recentEntries.map((entry) => (
                  <tr key={entry.id} className="hover:bg-jira-gray-light">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-jira-gray">
                      {format(new Date(entry.date), 'dd MMM yyyy')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-jira-gray">
                      {entry.hours}
                    </td>
                    <td className="px-6 py-4 text-sm text-jira-gray">
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
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

