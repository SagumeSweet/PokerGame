from typing import Sequence


class Player(object):
    _player_dict: dict[str, set['Player']] = {}

    @classmethod
    def get_player_by_name(cls, player_name: str, game_id: str) -> 'Player':
        for player in cls._all_players(game_id):
            if player.name == player_name:
                return player
        raise ValueError("Player name is not exist")

    @classmethod
    def _all_players(cls, game_id: str) -> Sequence['Player']:
        return tuple(cls._player_dict[game_id])

    @classmethod
    def clear_all_score(cls, game_id: str) -> None:
        for player in cls._all_players(game_id):
            player.clear_score()

    @classmethod
    def clear_player(cls, game_id: str):
        cls._player_dict.pop(game_id)

    def __init__(self, player_name: str, game_id: str):
        if game_id not in Player._player_dict.keys():
            Player._player_dict[game_id] = set()
        if player_name in [player.name for player in Player._player_dict[game_id]]:
            raise ValueError("Player name is duplicated")
        else:
            Player._player_dict[game_id].add(self)
            self._name: str = player_name
            self._all_score: list[int] = [0]

    @property
    def name(self) -> str:
        return self._name

    @property
    def score(self) -> int:
        return int(self.all_score[-1])

    @property
    def all_score(self) -> tuple[int, ...]:
        return tuple(self._all_score)

    @property
    def round_number(self) -> int:
        return len(self.all_score)

    @property
    def history_score(self) -> tuple[str, ...]:
        result_list = []
        for score_index in range(self.round_number):
            this_score = self._all_score[score_index]
            if score_index == 0:
                this_round_str = f"{this_score}"
            else:
                add_score = this_score - self._all_score[score_index - 1]
                add_score_str = f"+{add_score}" if add_score > 0 else f"{add_score}"
                this_round_str = f"{this_score}({add_score_str})"
            # 输出分数格式化长度
            score_str_length = 10

            if len(this_round_str) < score_str_length:
                this_round_str = f"{" " * (score_str_length - len(this_round_str))}{this_round_str}"
            result_list.append(this_round_str)
        return tuple(result_list)

    def add_score(self, score: int) -> None:
        self._all_score.append(self.all_score[-1] + score)

    def restart(self) -> None:
        self._all_score = [self._all_score[-1]]

    def clear_score(self) -> None:
        self._all_score = [0]

    def cancel_change(self) -> None:
        if len(self._all_score) > 1:
            self._all_score.pop()
        else:
            raise OverflowError("No score to cancel")

    def __str__(self) -> str:
        return self.history_score[-1]


class Game(object):
    players_number: int = 3
    _all_games: dict[str, 'Game'] = {}

    @classmethod
    def get_game_by_id(cls, game_id: str) -> 'Game':
        if game_id in cls._all_games.keys():
            return cls._all_games[game_id]
        else:
            raise ValueError("Game id is not exist")

    @classmethod
    def del_game(cls, game_id: str) -> None:
        if game_id in cls._all_games.keys():
            Player.clear_player(game_id)
            be_del = cls._all_games.pop(game_id)
            del be_del
        else:
            raise ValueError("Game id is not exist")

    def __init__(self, game_id: str, players: Sequence[Player] | None = None):
        if game_id in Game._all_games.keys():
            raise ValueError("Game id is duplicated")
        if players is None:
            players = []
            for index in range(1, Game.players_number + 1):
                name = f"player_{index}"
                try:
                    player: Player = Player(name, game_id)
                except ValueError:
                    player: Player = Player.get_player_by_name(name, game_id)
                players.append(player)
            self._players: tuple[Player, ...] = tuple(players)
        else:
            if len(players) != Game.players_number:
                raise ValueError("Player number is not equal to 3")
            self._players: tuple[Player, ...] = tuple(players)
        Game._all_games[game_id] = self

    @property
    def round_number(self) -> int:
        return self._players[0].round_number

    @property
    def now_score(self) -> str:
        result_str = ""
        for player in self._players:
            result_str += f"{player}"
        return result_str

    @property
    def history_str(self) -> str:
        result_str: str = "\n"
        for index in range(self.round_number):
            result_str += f"Round {index + 1} "
            for player in self._players:
                result_str += f"{player.history_score[index]}"
            result_str += "\n"
        return result_str

    @property
    def history_json(self) -> dict:
        result_list: list[dict] = []
        result_dict: dict = {"keyOrder": ["round"] + [player.name for player in self._players], "data": result_list}
        for index in range(self.round_number):
            this_dict = {"round": index + 1}
            for player in self._players:
                this_dict.update({player.name: player.history_score[index]})
            result_list.append(this_dict)

        return result_dict

    @property
    def players(self) -> tuple[str, ...]:
        return tuple([player.name for player in self._players])

    @players.setter
    def players(self, new_players: Sequence[Player]):
        if len(new_players) != Game.players_number:
            raise ValueError("Player number is not equal to 3")
        self.restart()
        self._players = tuple(new_players)

    def restart(self) -> None:
        for player in self._players:
            player.restart()

    def cancel_round(self) -> None:
        for player in self._players:
            player.cancel_change()

    def _get_player_by_name(self, player_name: str) -> Player:
        for player in self._players:
            if player.name == player_name:
                return player
        raise ValueError("Player not found")

    def new_round(self, king: str, score: int) -> None:
        if score % 2 != 0:
            raise ValueError("Score must be even")
        self._get_player_by_name(king).add_score(score)
        for player in self._players:
            if player.name != king:
                player.add_score(-int(score / (Game.players_number - 1)))

    def start(self) -> None:
        while True:
            def try_to_cancel():
                if input("Cancel?(y/n): ") == "y":
                    self.cancel_round()
                    return True
                return False

            print(self.history_str)
            if try_to_cancel():
                continue
            king = input("Enter King: ")
            king_added_score: int = eval(input("input king add score: "))
            self.new_round(king, king_added_score)
            if input("Enter to continue: ") != "":
                print(self.history_str)
                break
