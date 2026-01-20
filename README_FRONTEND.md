# LegalTime Frontend

Фронтенд для системы учёта времени для юристов, выполненный в стиле Jira/JiraTempo.

## Технологии

- **React 18** - UI библиотека
- **Vite** - сборщик и dev-сервер
- **React Router** - маршрутизация
- **Tailwind CSS** - стилизация в стиле Jira
- **Axios** - HTTP клиент
- **Lucide React** - иконки

## Установка

```bash
cd frontend
npm install
```

## Разработка

```bash
npm run dev
```

Фронтенд будет доступен на http://localhost:3000 с проксированием API запросов на http://localhost:8000

## Сборка

```bash
npm run build
```

Собранные файлы будут в папке `static/` в корне проекта, откуда FastAPI будет их раздавать.

## Структура

```
frontend/
├── src/
│   ├── components/      # Переиспользуемые компоненты
│   ├── contexts/        # React контексты (Auth)
│   ├── pages/          # Страницы приложения
│   ├── services/       # API клиент
│   ├── App.jsx         # Главный компонент
│   └── main.jsx        # Точка входа
├── index.html
├── package.json
└── vite.config.js
```

## Страницы

- **Login** - Авторизация
- **Dashboard** - Дашборд с общей статистикой
- **Time Entries** - Учёт времени (главная страница, как в Jira Tempo)
- **Matters** - Управление делами
- **Clients** - Управление клиентами
- **Contracts** - Управление договорами

## Интеграция с бэкендом

Все API запросы идут на `/api/*` и проксируются на FastAPI бэкенд.

Токен авторизации хранится в localStorage и автоматически добавляется в заголовки запросов.

