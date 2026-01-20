/**
 * Преобразует ошибку от API в читаемую строку
 * @param {Error} error - Объект ошибки от axios
 * @param {string} defaultMessage - Сообщение по умолчанию
 * @returns {string} - Строка с ошибкой
 */
export const getErrorMessage = (error, defaultMessage = 'Произошла ошибка') => {
  if (!error) return defaultMessage

  // Если это строка, возвращаем как есть
  if (typeof error === 'string') return error

  // Обрабатываем ответ от API
  const detail = error.response?.data?.detail

  if (!detail) {
    return error.message || defaultMessage
  }

  // Если detail - строка
  if (typeof detail === 'string') {
    return detail
  }

  // Если detail - массив (ошибки валидации FastAPI)
  if (Array.isArray(detail)) {
    return detail.map(err => {
      if (typeof err === 'string') return err
      if (err.msg) return err.msg
      if (err.loc && err.msg) {
        return `${err.loc.join('.')}: ${err.msg}`
      }
      return JSON.stringify(err)
    }).join(', ')
  }

  // Если detail - объект
  if (typeof detail === 'object') {
    if (detail.msg) return detail.msg
    if (detail.message) return detail.message
    return JSON.stringify(detail)
  }

  return defaultMessage
}

