import itertools
import random


class BluffBid:
    """
    Represents a single bluff claim in the game:
    a player claims that `count` cards of rank `rank`
    were just played.
    """

    def __init__(self, count: int, rank: str, player_id: int):
        self.count = count
        self.rank = rank
        self.player_id = player_id

    def __str__(self) -> str:
        return f"{self.count} x {self.rank} (by player {self.player_id})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, BluffBid):
            return False
        return (
            self.count == other.count
            and self.rank == other.rank
            and self.player_id == other.player_id
        )


class BluffPlayer:
    def start_game(self, identifier: int, cards: tuple[str]):
        pass

    def take_turn(
        self,
        cards: tuple[str],
        player_count: int,
        previous_play: int,
        current_rank: str,
    ) -> list[str] | None:
        return None

    def observe_bid(
        self,
        cards: tuple[str],
        player_count: int,
        challenge_amount_of_cards: int,
        current_rank: str,
        bidder_id: int,
    ) -> None:
        pass

    def observe_challenge(
        self,
        cards: tuple[str],
        player_count: int,
        challenge_amount_of_cards: int,
        current_rank: str,
        challenger_id: int,
        success: bool,
    ) -> None:
        pass


class BluffController:
    RANKS = "AJQK"

    def __init__(self):
        self._players = []

    def join(self, player: BluffPlayer) -> None:
        if player not in self._players:
            self._players.append(player)

    def _shuffle_and_divide(self) -> tuple[list[list[str]], list[str]]:
        deck = [card for card in self.RANKS for _ in range(4)]
        random.shuffle(deck)
        hands = [[] for _ in self._players]
        number_of_cards_per_player = len(deck) // len(self._players)
        for player in range(len(self._players)):
            hands[player] = deck[:number_of_cards_per_player]
            deck = deck[number_of_cards_per_player:]
        return hands, deck

    def play(self, *, debug=False) -> int:
        hands, pile = self._shuffle_and_divide()
        for i, player in enumerate(self._players):
            player.start_game(i, tuple(hands[i]))  # Start game signal
        current_rank = 0
        current_player = 0
        winner = None
        last_action = []
        while (
            winner is None
        ):  # Changed from while not winner because 0 equals not winner and would throw bug.
            if debug:
                for player in range(len(self._players)):
                    print("Player", player, "has hand", sorted(hands[player]))
                print("Pile currently has", pile)
                print("Current rank is", self.RANKS[current_rank])
            if len(hands[current_player]) == 0:
                winner = current_player
                break
            current_action = self._players[current_player].take_turn(
                tuple(hands[current_player]),
                len(self._players),
                len(last_action),
                self.RANKS[current_rank],
            )
            if current_action is None or len(current_action) == 0:
                if len(last_action) == 0:
                    # Player has performed an illegal action, next player wins the game
                    if debug:
                        print(
                            "Player", current_player, "performed an illegal challenge."
                        )
                    winner = (current_player + 1) % len(self._players)
                    break
                last_action_was_a_bluff = False
                for card in last_action:
                    if card != self.RANKS[current_rank]:
                        last_action_was_a_bluff = True
                if not last_action_was_a_bluff:
                    if debug:
                        print(
                            "Player",
                            current_player,
                            "challenged unsuccessfully and takes the entire pile.",
                        )
                    hands[current_player].extend(pile)
                    pile = []
                else:
                    challenged_player = (len(self._players) + current_player - 1) % len(
                        self._players
                    )
                    if debug:
                        print(
                            "Player",
                            current_player,
                            "challenged successfully; player",
                            challenged_player,
                            "takes the entire pile.",
                        )
                    hands[challenged_player].extend(pile)
                    pile = []
                # Next round: next player, next rank
                current_player = (current_player + 1) % len(
                    self._players
                )  # chatgpt says there is a bug here
                current_rank = (current_rank + 1) % len(self.RANKS)
                last_action = []
                for player in range(len(self._players)):
                    self._players[player].observe_challenge(
                        hands[player],
                        len(self._players),
                        len(last_action),
                        current_rank,
                        current_player,
                        last_action_was_a_bluff,
                    )  # till here
            else:
                for card in current_action:
                    if card in hands[current_player]:
                        hands[current_player].remove(card)
                        pile.append(card)
                    else:
                        if debug:
                            print(
                                "Player",
                                current_player,
                                "cheated and takes the entire pile.",
                            )
                        hands[current_player].extend(pile)
                        pile = []
                        current_action = []
                        break
                if debug:
                    print(
                        "Player",
                        current_player,
                        "plays",
                        current_action,
                        "onto the pile.",
                    )
                last_action = current_action
                for player in range(
                    len(self._players)
                ):  # Chatgpt says theres an error from here
                    self._players[player].observe_bid(
                        hands[player],
                        len(self._players),
                        len(last_action),
                        current_rank,
                        current_player,
                    )  # Till here
                current_player = (current_player + 1) % len(self._players)
        if debug:
            print("Player", current_player, "wins the game.")
        return current_player

    def repeated_games(
        self,
        number_of_games: int,
        *,
        win_score: int = 1,
    ) -> list[int]:
        total_score = [0 for _ in range(len(self._players))]
        for _ in range(number_of_games):
            winner = self.play()  # your play() returns an int
            total_score[winner] += win_score
        return total_score


def get_valid_bluff_plays(hand: tuple[str], previous_play: int) -> list[list[str]]:
    """
    Returns all legal card plays (not challenges) from this hand.
    Does NOT include the challenge action.
    """
    if len(hand) == 0:
        return []
    valid = []
    # You may play between 1 and 4 cards, as it is illogical to play more than 4 cards as there are only 4 cards of each rank
    # IMPORTANT: This is an assumption, I should mention this in the report.
    max_play = 4
    for k in range(1, max_play + 1):
        for combo in itertools.combinations(hand, k):
            valid.append(list(combo))
    return valid
