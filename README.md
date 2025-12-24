# Текущие задачи

## 1. БЭКЕНД – ОСНОВА (Слава) ~3 недели

### Backend-Core
1. [x] Создать структуру проекта FastAPI.
2. [x] Настроить `.env`, конфигурации и CORS.
3. [x] Подключить Postgres и SQLAlchemy (async).
4. [x] Настроить Alembic (миграции).
5. [x] Написать Dockerfile для backend и docker-compose.

---

## 2. АВТОРИЗАЦИЯ (Слава + Яна) ~3 недели

### Auth
6. [x] Создать модель User в БД.
7. [x] Реализовать хеширование паролей.
8. [x] Реализовать JWT-авторизацию.
9. [x] Эндпоинт `POST /auth/register` — регистрация.
10. [x] Эндпоинт `POST /auth/login` — логин.
11. [x] Эндпоинт `GET /auth/me` — получение профиля.
12. [x] Написать тесты на авторизацию.

---

## 3. ЛОББИ И СТОЛЫ (REST) (Сергей) ~1 неделя

### Tables
13. [x] Создать модель Table (стол).
14. [ ] Создать модель Seat (место игрока).
15. [x] Эндпоинт `GET /tables` — список столов.
16. [x] Эндпоинт `POST /tables/create` — создание стола.
17. [x] Эндпоинт `GET /tables/{id}` — инфо стола.
18. [x] Эндпоинт `POST /tables/{id}/join` — сесть за стол.
19. [x] Эндпоинт `POST /tables/{id}/leave` — покинуть стол.
20. [x] Эндпоинт `POST /tables/{id}/spectate` — наблюдение.
21. [x] Тесты для лобби/столов.

---

## 4. ПОКЕРНЫЙ ДВИЖОК (ENGINE) (Никита + Сергей) ~1 неделя

### Core Engine
22. [x] Создать класс Card + enum Rank/Suit.
23. [x] Создать класс Deck (shuffle, draw, draw_many).
24. [x] Создать класс PlayerState (stack, карты, статус).
25. [x] Создать класс GameState (фаза, банк, борд, игроки).
26. [x] Реализовать переходы фаз (preflop → river → showdown).
27. [x] Реализовать действия fold/check/call/bet/raise.
28. [x] Реализовать HandEvaluator (оценка комбинаций).
29. [x] Реализовать определение победителей.
30. [x] Написать юнит-тесты на комбинации.
31. [x] Написать юнит-тесты на игровой сценарий.

---

## 5. GAME SERVICE (СЕРВИСНАЯ ЛОГИКА ИГРЫ) (Яна) ~1 неделя

### GameService
32. [ ] Реализовать сериализацию GameState в JSON.
33. [ ] Реализовать десериализацию GameState из JSON.
34. [x] Функция “start_hand(table_id)” — запуск раздачи.
35. [x] Функция “apply_action(table_id, user_id, action)” — игровой ход.
36. [x] Обновление pot, стека и текущей ставки.
37. [x] Закрытие раздачи и подсчёт победителей.
38. [x] Запись FinishedHand и PlayerInHand в БД.
39. [x] Обновление статистики игрока.
40. [ ] Функция “get_current_state(table_id)”.

---

## 6. WEBSOCKET (Денис) ~2 недели

### WebSocket API
41. [x] Реализовать эндпоинт `/ws/tables/{id}`.
42. [x] Реализовать чтение JWT из query-параметра.
43. [x] Реализовать TableConnection (данные по подключению).
44. [x] Реализовать ConnectionManager (регистрация/удаление подключений).
45. [x] Обработка `player_action` (fold/call/check/raise).
46. [x] Обработка `toggle_show_all` (зрительский режим).
47. [x] Рассылка состояния через WS (`table_state`).
48. [x] Реализовать фильтрацию карт по пользователю.
49. [x] Прописать структуру формата сообщений WS.

---

## 7. СТАТИСТИКА (Никита) ~1 неделя

### Stats
50. [x] Создать модель PlayerStats.
51. [x] Реализовать функцию обновления статы после раздачи.
52. [x] Эндпоинт `/stats/me/stats`.
53. [x] Эндпоинт `/stats/me/history`.
54. [x] Эндпоинт `/stats/{user_id}/stats`.
55. [x] Эндпоинт `/stats/{user_id}/history`.
56. [x] Тесты статистики.

---

## 8. ФРОНТЕНД (Денис) ~2 недели

### Frontend
57. [x] Инициализировать проект React + Vite + TS.
58. [x] Реализовать страницу Login/Register.
59. [x] Реализовать страницу Lobby (список столов).
60. [x] Реализовать страницу Table (игровой стол).
61. [x] Реализовать отображение борда, игроков, банка.
62. [x] Реализовать кнопки действий Fold/Call/Check/Raise.
63. [x] Интегрировать WebSocket (подключение + обновление состояния).
64. [x] Реализовать режим Spectator + переключатель “Показывать карты”.
65. [x] Реализовать страницу Profile (статы + история).

---

## 9. ДОКУМЕНТАЦИЯ (Все вместе) ~4 недели

### Docs
66. [x] Написать архитектурную диаграмму.
67. [x] Написать диаграмму взаимодействия WebSocket.
68. [ ] Нарисовать ER-диаграмму БД.
69. [x] Описание API (REST + WS).
70. [x] Финальное описание проекта для защиты.

### Архитектурная диаграмма

```text
Browser (SPA)
  |
  v
Nginx (hsepoker.ru)
  |-- "/" -----------> Static frontend (index.html + assets)
  |-- "/api/*" ------> FastAPI (Uvicorn via PM2) -> REST routers
  |-- "/ws/*" -------> FastAPI (Uvicorn via PM2) -> WS routers

FastAPI
  REST (/api)
    - /auth/*  -> users (Postgres)
    - /tables/* -> TableService -> TableStore (in-memory) + users (balance)
    - /stats/* -> Postgres (player_stats/player_games/finished_games)
  WebSocket (/ws/tables/:id)
    - validates JWT token
    - reads TableStore (in-memory)
    - calls GameService -> Poker Engine (Table/GameState)
    - persists hand results to Postgres

Poker Engine
  - Table (domain) + GameState (hand lifecycle)

Database (Postgres)
  - users
  - player_stats
  - finished_games
  - player_games

Migrations (Alembic) -> Postgres schema

CI/CD (GitHub Actions, self-hosted)
  - checks: pytest + flake8 + mypy
  - deploy (manual approval): sync backend + sync frontend build to /var/www/...
```

### Диаграмма взаимодействия WebSocket

```text
Browser                Nginx                 WS handler             TableStore      GameService      Poker Engine          Postgres
  |                      |                      |                      |              |               |                   |
  |--- WS connect ------>|--- upgrade --------->|                      |              |               |                   |
  |  /ws/tables/:id?jwt  |                      |--- decode jwt ------>|              |               |                   |
  |                      |                      |--- get table ------->|              |               |                   |
  |<-- table_state ------|<---------------------|--- build state ------|              |               |                   |
  |                      |                      |                      |              |               |                   |
  |--- player_action ----|--------------------->|                      |              |               |                   |
  |                      |                      |--- apply_action ------------------->|--- Table.apply_action ---------->|
  |                      |                      |                      |              |               |                   |
  |                      |                      |<-- updated state ----|              |               |                   |
  |<-- table_state ------|<---------------------|                      |              |               |                   |
  |                      |                      |                      |              |               |                   |
  |                      |                      |  if hand finished:   |              |               |                   |
  |                      |                      |--- record results -----------------------------------------------> (finished_games/player_games/player_stats)
  |                      |                      |--- table_state (reveal all hole cards) ------------------------>|
  |<-- table_state ------|<---------------------|                      |              |               |                   |
  |                      |                      |--- schedule next hand (delay)                                  |
  |                      |                      |--- start_hand -------------------------->|--- Table.start_game -------->|
  |<-- table_state ------|<---------------------|                      |              |               |                   |
```

### API (REST + WS)

Base URL:
- REST: `/api`
- WebSocket: `/ws`

Auth:
- `POST /api/auth/register` body: `{ "username": string, "password": string }` -> `{ "access_token": string, "token_type": "Bearer" }`
- `POST /api/auth/login` body: `{ "login": string, "password": string }` (или `{ "username": ... }`) -> `{ "access_token": string, "token_type": "Bearer" }`
- `GET /api/auth/me` header: `Authorization: Bearer <token>` -> `{ "id": int, "username": string, "balance": int }`

Tables (REST):
- `GET /api/tables/` -> `TableSummary[]` (приватные столы скрыты)
- `POST /api/tables/create` body: `{ "max_players": 2..9, "buy_in": int, "private": bool }` -> `TableSummary`
- `GET /api/tables/{table_id}` -> `TableDetail` (seats)
- `POST /api/tables/{table_id}/join` auth required -> `{ "ok": true }`
- `POST /api/tables/{table_id}/leave` auth required -> `{ "ok": true }`
- `POST /api/tables/{table_id}/spectate` auth required -> `{ "ok": true }`

Users:
- `GET /api/users/{user_id}` -> `{ "id": int, "username": string }`

Stats:
- `GET /api/stats/me/stats` auth required -> `PlayerStatsOut`
- `GET /api/stats/me/history?limit=1..500&offset>=0` auth required -> `PlayerHistoryEntry[]`
- `GET /api/stats/{user_id}/stats` -> `PlayerStatsOut`
- `GET /api/stats/{user_id}/history?limit=1..500&offset>=0` -> `PlayerHistoryEntry[]`

Health:
- `GET /api/health` -> `200 OK`
- `GET /api/health/settings` -> `{ api_prefix, cors_origins, database_url, env_source }`

Errors (REST):
- Format: `{"detail":{"code": "<string>", "message": "<string>"}}`

WebSocket:
- Connect: `ws(s)://<host>/ws/tables/{table_id}?token=<jwt>`

Client -> Server messages:
- `{ "type": "player_action", "payload": { "action": "fold|check|call|bet|raise|all_in", "amount": number } }`
- `{ "type": "toggle_show_all", "payload": { "show": boolean } }` (только для зрителей)

Server -> Client messages:
- `{ "type": "table_state", "payload": TableState }`
- `{ "type": "error", "code": "<string>", "message": "<string>" }`

TableState (WS):
- `table_id: string`
- `phase: string` (`preflop|flop|turn|river|finished`)
- `hand_active: boolean`
- `pot: number`
- `board: string[]`
- `players: Array<{ user_id:number, position:number, stack:number, bet:number, status:string, hole_cards?:string[] }>`
- `winners: number[]`
- `current_player_id: number|null`
- `current_bet: number|null`
- `min_bet: number|null`

### Финальное описание проекта (для защиты)

Проект — веб-приложение для игры в Texas Hold’em с лобби столов, игрой в реальном времени через WebSocket и сохранением результатов раздач в БД.

Основные возможности:
- Регистрация/логин по JWT, профиль пользователя с балансом.
- Лобби столов: создание (публичный/приватный), вход игроком (buy-in), вход зрителем.
- Игра за столом в реальном времени: действия игрока отправляются по WS, состояние стола транслируется всем подключённым.
- По завершении раздачи результаты фиксируются в Postgres: история раздач, статистика игрока.
- CI/CD: проверки `pytest + flake8 + mypy`, деплой (manual approval) на self-hosted runner.

Технологии:
- Backend: FastAPI, SQLAlchemy async, Alembic, Postgres, WebSocket.
- Frontend: React + Vite + TypeScript.
- Deploy: Nginx + PM2 (Uvicorn), GitHub Actions (self-hosted).

### Запуск проекта с нуля

#### Вариант A — Docker (рекомендуется)

Требования: Docker, Docker Compose.

1) Поднять сервисы:
   - `docker compose up --build`

2) Применить миграции:
   - `docker compose exec backend poetry run alembic -c backend/alembic.ini upgrade head`

3) Открыть:
   - Backend: `http://localhost:8000/api/health`

Frontend в Docker сейчас не поднимается отдельным сервисом. Для удобства в разработке запускай его локально (см. вариант B).

#### Вариант B — Локальная разработка (без Docker)

Требования: Python 3.12, Poetry, Node.js 18+.

1) Запустить Postgres:
   - либо через Docker: `docker compose up -d db`
   - либо свой локальный Postgres (важно знать URL)

2) Backend:
   - `poetry install`
   - `export DATABASE_URL='postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/poker'`
   - `poetry run alembic -c backend/alembic.ini upgrade head`
   - `poetry run uvicorn backend.rest.main:app --reload --host 0.0.0.0 --port 8000`

3) Frontend:
   - `npm -C frontend ci`
   - `npm -C frontend run dev`
   - открыть `http://localhost:5173`

Если фронту нужен явный адрес API/WS, можно задать:
- `VITE_API_URL` (например `http://localhost:8000/api`)
- `VITE_WS_URL` (например `ws://localhost:8000/ws`)


# Документация проекта

## Backend

### Запуск (локально)
    - из корня репозитория: `poetry install` затем `poetry run uvicorn backend.rest.main:app --reload --host 0.0.0.0 --port 8000`

-### Миграции (Alembic)
    - применить миграции: `poetry run alembic upgrade head` (или `python -m alembic upgrade head` если зависимости установлены в venv)
    - создать миграцию: `poetry run alembic revision --autogenerate -m "message"`

- ### Docker

    - uvicorn

    - poetry

    - dependecies

- ### Api (FastApi)

    - **Auth** */auth* - авторизация пользователей

        - POST */register* - регистрация (email, login, password+hash) + присванивание jwt

        - POST */login* - логин (email/login, password)

        - GET */me* - профиль текущего пользователя

    - **Lobbies** */tables* - столы, игры

        - GET *default* - список столов

        - POST */create* - создать стол с определёнными настройками (max_players: int, private: bool, buy_in: int)

        - GET */{uuid}* - информация стола по uuid

        - POST */{uuid}/join* - создание места за столом

        - POST */{uuid}/leave* - освобождение места, возврат средств игроку

        - POST */{uuid}/spectate* - сидеть в роли наблюдателя

    - **Stats** */stats* - статистика пользователей

        - GET */me/history* - прошедшие игры текущего пользователя

        - GET */{user_id}/history* - прошедшие игры пользователя по user_id

        - GET */me/stats* - статистика за все игры текущего пользователя

        - GET */{user_id}/stats* - статистика за все игры пользователя по user_id

- ### Poker Engine

    - Класс **Card** - карта

        - *Rank: str* - ранг 2-10, Валет Jack, Дама Queen, Король King, Туз Ace

        - *Suit: str* - масть Черви Hearts, Пики Spades, Бубны Diamonds, Трефы Clubs

    - Класс **Deck** - набор карт

        - *shuffle(): None* - перемешать все карты

        - *draw(): Card* - взять карту
    
    - Класс **Table** - стол, за которым идёт игра

        - *uuid: int* - айди стола

        - *max_players: int* - максимальное кол-во игроков

        - *buy_in: int* - за сколько садимся за стол

        - *private: bool* - приватный стол или можно ли присоединиться к столу из лобби

        - *players: List[int]* - список айди игроков стола

        - *spectators: List[int]* - список айди наблюдателей стола

    - Класс **PlayerState** - состояние игрока

        - *user_id: int* - айди пользоваетеля

        - *position: int* - позиция игрока за столом

        - *stack: int* - баланс фишек

        - *hole_cards: List[Card]* - выданные карты

        - *bet: int* - ставка

        - *status: Enum* - статус игрока, т.е. spectator/active/folded/all-in

        - *fold(): None* - сбросить карты

        - *check(): None* - пропуск хода

        - *call(): None* - поставить такую же ставку, как и у наибольшего игрока

        - *raise(amount): None* - повысить ставку

        - *is_first_to_play(): bool* - проверить первый ли ставил ставку для определения конца раунда

        - *is_small_blind(): bool* - small blind?

        - *is_big_blind(): bool* - big blind?

    - Класс **GameState** - состояние раздачи

        - *players: List[PlayerState]* - список игроков

        - *status: Enum* - фаза preflop/flop/turn/river/showdown

        - *board: List[Cards]* - выложенные карты

        - *pot: int* - суммарный банк

        - *min_bet: int* - минимальная ставка

        - *cur_bet: int* - текущая ставка, которую нужно уравнять ставка

        - *cur_player: PlayerState* - ход игрока

        - *raised_bet: int* - количество поднятий ставок

        - *next_player(): PlayerState* - отдать ход следующему игроку

        - *is_everyone_played(): bool* - проверить все ли походили и все ли поставили необходимую ставку

        - *is_check(): bool* - можно ли чекать

        - *is_ready_for_next_phase(): bool* - проверить готова ли игра к следующей фазе

        - возможно нужно будет хранить список ставок и действий

    - Класс **HandEvaluator** - определение руки

        - *board: List[Cards]* - карты на столе

        - *hole_cards: List[Cards]* - карты игрока
    
    - Класс определение победителя хз надо додумать

- ### Database (SqlAlchemy, Postgres)

    - **User** - пользователь, для авторизации

        - *user_id: int* - айди пользователя

        - *username: str* - имя пользователя

        - *email: str* - почта

        - *password_hash: str* - хэш пароля

        - *balance: int* - баланс

        - *created_at: datetime* - время создания

    - **PlayerStats** - статистика игрока за все игры определённого игрока

        - *hands_won: int* - выигранные игры

        - *hands_lost: int* - проигранные игры

        - *max_balance: int* - максимальный баланс за всё время

        - *max_bet: int* - максимальная ставка за всё время

        - *lost_stack* - суммарные потерянные фишки

        - *won_stack* - суммарные выигранные фишки 

    - **PlayerGame** - статистика игрока за игру

        - *id: int* - айди игрока (типо айди PlayerGame)

        - *table_id: int* - айди стола

        - *user_id: int* - айди пользователя

        - *hole_cards: List[str]* - выданные карты

        - *bet: int* - ставка

    - **FinishedGame** - законченные игры

        - *uuid: int* - айди игры

        - *Winners: List[User]* - победители

        - *Pot: int* - суммарные ставки

        - *Board: List[str]* - карты на столе в конце игры

        - *Players: List[PlayerGame]* - игроки

- ### Тесты всего всего всего

- ### Websocket

    дай бог разобраться с этим

## Frontend

Vite + React + TypeScript + Node.js

- ### Страницы:

    - **Login/Register** - регистрация/логин

    - **Lobby** - список столов

    - **Table** - стол, вокруг которого сидят игроки

    - **Profile** - профиль игрока

Впервые пользователь при входе видит страницу Login/Register

После успешной регистрации/логина пользователь видит Лобби. В лобби находятся активные столы, к которым он может присоединиться. Также может создать свой стол со своими настройками. 

Также пользователь может посмотреть на свой профиль, где будут отображаться история игр и его статистика за всё время.

Во время игры пользователь может нажимать разные кнопки будь, то поставить ставку, чекнуть, сдать карты и тп, всё по правилам покера

![](./imgs/table.png)
