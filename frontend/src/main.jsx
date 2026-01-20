import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Обработка ошибок
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error)
  event.preventDefault()
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  event.preventDefault()
})

try {
  const root = ReactDOM.createRoot(document.getElementById('root'))
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  )
} catch (error) {
  console.error('Failed to render app:', error)
  document.getElementById('root').innerHTML = `
    <div style="padding: 20px; font-family: sans-serif;">
      <h1>Ошибка загрузки приложения</h1>
      <p>${error.message}</p>
      <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow: auto;">
        ${error.stack}
      </pre>
    </div>
  `
}

