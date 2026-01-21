import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { 
  LayoutDashboard, 
  Clock, 
  FileText, 
  Users, 
  FileCheck,
  UserCog,
  LogOut 
} from 'lucide-react'

const Layout = () => {
  const { logout, user } = useAuth()
  const location = useLocation()
  const isAdmin = user?.role === 'admin'
  const isSeniorOrAdmin = user?.role === 'admin' || user?.role === 'senior_lawyer'

  const navigation = [
    { name: 'Дашборд', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Учёт времени', href: '/time-entries', icon: Clock },
    { name: 'Дела', href: '/matters', icon: FileText },
    { name: 'Клиенты', href: '/clients', icon: Users },
    { name: 'Договоры', href: '/contracts', icon: FileCheck },
    ...(isAdmin ? [{ name: 'Сотрудники', href: '/employees', icon: UserCog }] : []),
    ...(isSeniorOrAdmin ? [{ name: 'Ставки', href: '/rates', icon: FileText }] : []),
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-jira-gray-light">
      {/* Header */}
      <header className="bg-white border-b border-jira-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-jira-blue">LegalTime</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={logout}
                className="flex items-center space-x-2 px-3 py-2 text-sm text-jira-gray hover:text-jira-blue"
              >
                <LogOut size={16} />
                <span>Выйти</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-jira-border min-h-[calc(100vh-4rem)] flex-shrink-0">
          <nav className="p-4 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive(item.href)
                      ? 'bg-jira-blue text-white'
                      : 'text-jira-gray hover:bg-jira-gray-light'
                  }`}
                >
                  <Icon size={20} />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-x-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout

