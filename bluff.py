from __future__ import annotations

# TODO; Implement play logic, implement 0, 1, and 2 order ToM players.
import random

CardsType = list[tuple[str, str]]

VALID_SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
VALID_VALUES = ["Jack", "Queen", "King", "Ace"]


class Card:
    def __init__(self, value: str, suit: str) -> None:
        if suit not in VALID_SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        if value not in VALID_VALUES:
            raise ValueError(f"Invalid value: {value}")
        self.suit = suit
        self.value = value

    def __str__(self):
        return f"{self.value} of {self.suit}!"

    def __repr__(self) -> str:
        return f"Card({self.value!r}, {self.suit})"


card = Card("Ace", "Spades")
print(card)


class BluffBid:
    def __init__(self, cards: CardsType):
        self.cards = cards

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BluffBid):
            return NotImplemented
        return self.cards == other.cards


class BluffPlayer:
    def start_game(self, identifier: int, player_count: int, cards: CardsType):
        """Player receives its ID, number of players, and its initial hand."""
        pass

    def take_turn(self, current_bid: BluffBid | None) -> BluffBid | None:
        """Return a new bid or None to challenge."""
        pass

    def observe_bid(self, bid: BluffBid, player: int) -> None:
        """Update beliefs given another player's bid."""
        pass

    def observe_challenge(
        self,
        bid: BluffBid,
        challenger: int,
        success: bool,
        revealed_cards: CardsType | None = None,
    ) -> None:
        """Observe the outcome of a challenge. Optionally receive revealed cards."""
        pass


class Bluff:
    """Implemnentation of bluff game"""

    CARDS_PER_PLAYER = 4  # Assume a 2-player setup

    def __init__(self):
        self._players = []

    def _build_deck(self):
        """sets up deck"""
        return [Card(v, s) for s in VALID_SUITS for v in VALID_VALUES]

    def _deal_cards(self):
        """deals cards to agents and removes them from the hand"""
        deck = self._build_deck()
        random.shuffle(deck)

        hands = []
        for _ in self._players:
            hand = deck[: self.CARDS_PER_PLAYER]
            del deck[: self.CARDS_PER_PLAYER]
            hands.append(hand)
        return hands

    def join(self, player: BluffPlayer) -> None:
        """Lets a player join the game

        Args:
            player (BluffPlayer): self explanatory
        """
        if player not in self._players:
            self._players.append(player)

    def play(self, debug: bool = False) -> list[int]:
        """_summary_

        Args:
            debug (bool, optional): _description_. Defaults to False.

        Returns:
            list[int]: _description_
        """
        score = [0 for _ in self._players]
        hands = self._deal_cards()

        # Tell each player their hand
        for pid, player in enumerate(self._players):
            player.start_game(pid, len(self._players), hands[pid])

        # Now continue with bidding logic etc.

        return score

    def repeated_games(
        self,
        number_of_games: int,
        *,
        challenge_win_score: int = 1,
        challenge_lose_score: int = 0,
        bid_win_score: int = 1,
        bid_lose_score: int = 0,
    ):
        """
        Performs a series of games
        :param number_of_games: number of games to perform
        :return: total number of wins for each player across games
        """
        total_score = 0
        return total_score

        # Minimal implementation: return the indices of players who joined.
        # This ensures the function always returns a list[int] as declared.
