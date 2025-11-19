# Backend

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

# Frontend

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

![](./imgs/table.svg)