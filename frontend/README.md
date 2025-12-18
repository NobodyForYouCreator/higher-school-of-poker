# Frontend (React + Vite + TypeScript + Tailwind)

## Требования

- Node.js 18+ (рекомендуется 20+)

## Настройка

1) Создай файл `frontend/.env` на базе `frontend/.env.example`.
2) Укажи адреса бэкенда:

- `VITE_API_BASE_URL` — REST API (пример: `http://localhost:8000`)
- `VITE_WS_BASE_URL` — WebSocket (пример: `ws://localhost:8000`)

## Запуск

```bash
cd frontend
npm install
npm run dev
```

## Авторизация

- JWT хранится в `localStorage` по ключу `hsepoker.access_token`.
- В dev-режиме на странице `/login` есть кнопка **Dev: войти без бэка** (ставит фиктивный токен).

