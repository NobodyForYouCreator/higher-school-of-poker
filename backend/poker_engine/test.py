from backend.poker_engine.table import Table
from backend.poker_engine.game_state import PlayerAction, GamePhase

def describe_state(game):
    board = " ".join(str(card) for card in game.board) or "—"
    print(f"\n=== Фаза: {game.phase.value.upper()} ===")
    print(f"Банк: {game.pot}")
    print(f"Борд: {board}")
    for player in game.players:
        cards = " ".join(str(c) for c in player.hole_cards) or "[]"
        print(
            f"Player {player.user_id} | stack={player.stack:4} | bet={player.bet:3} "
            f"| status={player.status.value:7} | cards={cards}"
        )
    acting = (
        f"ходит игрок {game.players[game.current_player_index].user_id}"
        if game.current_player_index is not None
        else "ход завершён, ждём переход фазы"
    )
    print(">>", acting)

def auto_action(table, user_id, action, amount=0):
    print(f"\nPlayer {user_id} -> {action.value}{f' {amount}' if amount else ''}")
    table.apply_action(user_id, action, amount)
    describe_state(table.game_state)

def main():
    table = Table(max_players=4)
    table.seat_player(1, 1500)
    table.seat_player(2, 1500)
    table.seat_player(3, 1500)
    table.seat_player(4, 1500)

    game = table.start_game()
    describe_state(game)



    while game.hand_active:
        action = input()
        if action == "RAISE":
            num = int(input())
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.RAISE, num)
        elif action == "BET":
            num = int(input())
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.BET, num)
        elif action == "CALL":
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.CALL)
        elif action == "CHECK":
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.CHECK)
        elif action == "FOLD":
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.FOLD)
        elif action == "ALL_IN":
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.ALL_IN)
    if not game.hand_active:
        winners = ", ".join(str(p.user_id) for p in game.winners)
        print(f"\n*** Раздача завершена. Победители: {winners}")
        if game.best_hand:
            print(f"Лучшая рука: {game.best_hand.rank.name}, "
                  f"картинки: {' '.join(str(c) for c in game.best_hand.cards)}")

    table.leave(1)
    table.leave(2)
    table.seat_player(52, 1500)
    table.seat_player(1337, 1500)

    game = table.start_game()
    describe_state(game)

    while game.hand_active:
        action = input()
        if action == "RAISE":
            num = int(input())
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.RAISE, num)
        elif action == "BET":
            num = int(input())
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.BET, num)
        elif action == "CALL":
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.CALL)
        elif action == "CHECK":
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.CHECK)
        elif action == "FOLD":
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.FOLD)
        elif action == "ALL_IN":
            auto_action(table, table.players[game.current_player_index].user_id, PlayerAction.ALL_IN)
    if not game.hand_active:
        winners = ", ".join(str(p.user_id) for p in game.winners)
        print(f"\n*** Раздача завершена. Победители: {winners}")
        if game.best_hand:
            print(f"Лучшая рука: {game.best_hand.rank.name}, "
                  f"картинки: {' '.join(str(c) for c in game.best_hand.cards)}")


if __name__ == "__main__":
    main()
