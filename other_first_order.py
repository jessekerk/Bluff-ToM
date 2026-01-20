from __future__ import annotations

import random
from typing import Optional

from bluff import BluffPlayer, BluffBid
from zeroorderplayer import ZeroOrderPlayer


FULL_DECK = (
    "A","A","A","A",
    "K","K","K","K",
    "Q","Q","Q","Q",
    "J","J","J","J",
)


class FirstOrderPlayer(BluffPlayer):
    """
    ToM1 player that:
    - keeps a coarse "possible opponent cards" multiset (opp_cards)
    - updates it after each observed opponent bid using the ToM0 bluff rule
    - resets state after a challenge
    - chooses action by max expected value over (challenge) + (play truth/bluff with k cards)
    """

    # -------------------------
    # Setup / bookkeeping
    # -------------------------
    def start_game(self, identifier: int, cards: tuple[str]) -> None:
        self.identifier = identifier
        self.player_count = 2  # your project assumes 2 players
        self.my_cards = cards

        self.pile_size = 0
        self.previous_bid: BluffBid | None = None

        # "Possible opponent cards" = full deck minus my hand (your approximation)
        deck = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
        self.opp_cards = tuple(deck)

        self.beliefs = {}  # placeholder for later Bayesian beliefs

    def _remove_specific(self, pool: list[str], rank: str, n: int) -> None:
        for _ in range(n):
            try:
                pool.remove(rank)
            except ValueError:
                break

    def _remove_random_not_rank(self, pool: list[str], forbidden_rank: str, n: int) -> None:
        for _ in range(n):
            idxs = [i for i, c in enumerate(pool) if c != forbidden_rank]
            if not idxs:
                return
            pool.pop(random.choice(idxs))

    # -------------------------
    # Observations
    # -------------------------
    def observe_bid(
        self,
        cards: tuple[str],
        player_count: int,
        challenge_amount_of_cards: int,
        current_rank: str,
        bidder_id: int,
        current_bid: BluffBid | None,
    ) -> None:
        # Keep my own view consistent with what engine passes me
        self.my_cards = cards
        self.player_count = player_count

        if current_bid is None:
            return

        # Your rule assumption: bid.count == number of cards placed into pile
        self.pile_size += current_bid.count
        self.previous_bid = current_bid

        # Only update opp_cards if the opponent made the bid
        if bidder_id == self.identifier:
            return

        k = current_bid.count
        opp_pool = list(self.opp_cards)

        # Predict whether ToM0 would be bluffing given opp_pool
        would_bluff = ZeroOrderPlayer().tom0_would_bluff(self.opp_cards, current_rank, current_bid)

        if not would_bluff:
            # truthful -> remove k copies of current_rank from opponent pool
            self._remove_specific(opp_pool, current_rank, k)
        else:
            # bluff -> remove k random non-current_rank cards from opponent pool
            self._remove_random_not_rank(opp_pool, current_rank, k)

        self.opp_cards = tuple(opp_pool)

    def observe_challenge(
        self,
        cards: tuple[str],
        player_count: int,
        challenge_amount_of_cards: int,
        current_rank: str,
        challenger_id: int,
        success: bool,
    ) -> None:
        # After a challenge, the pile is collected by someone => table pile is empty
        self.pile_size = 0
        self.previous_bid = None

        # Update my hand from engine
        self.my_cards = cards
        self.player_count = player_count

        # Rebuild opponent pool as "full deck minus my hand" (your coarse approximation)
        deck = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
        self.opp_cards = tuple(deck)

    # -------------------------
    # EV models
    # -------------------------
    def calculate_ev_challenge(self, opponent_cards: tuple[str], current_rank: str, opponent_last_bid: BluffBid) -> float:
        """
        EV of challenging the *opponent's* last bid.
        Your current simplification: if opponent would bluff => +pile_size else -pile_size
        """
        if ZeroOrderPlayer().tom0_would_bluff(opponent_cards, current_rank, opponent_last_bid):
            return float(self.pile_size)
        return float(-self.pile_size)

    def calculate_ev_play(
        self,
        my_cards: tuple[str],
        player_count: int,
        current_rank: str,
        my_next_bid: BluffBid,
        i_will_bluff: bool
    ) -> float:
        """
        EV of me making bid my_next_bid and playing i_will_bluff or not.
        Uses ToM0 challenge probability as opponent model.
        """
        M = my_next_bid.count
        P_challenge = ZeroOrderPlayer().calculate_challenge_probability(
            my_cards, player_count, current_rank, my_next_bid
        )

        if i_will_bluff:
            # if challenged: lose pile (pick it up) => -pile_size; if not challenged: you shed M cards
            return P_challenge * (-self.pile_size) + (1.0 - P_challenge) * M
        else:
            # if truthful and challenged: in many rules challenger loses -> you gain pile_size
            # (this matches your earlier assumption)
            return P_challenge * self.pile_size + M

    # -------------------------
    # Action selection
    # -------------------------
    def take_turn(
        self,
        cards: tuple[str],
        player_count: int,
        current_rank: str,
        current_bid: BluffBid | None
    ) -> list[str] | None:

        # Keep internal state aligned
        self.my_cards = cards
        self.player_count = player_count

        bluff_cards = [c for c in cards if c != current_rank]
        truth_cards = [c for c in cards if c == current_rank]

        n_bluff = len(bluff_cards)
        n_truth = len(truth_cards)

        choices: dict[tuple[str, bool, int] | tuple[str], float] = {}

        # Option 1: challenge (only if there is something to challenge)
        if current_bid is not None:
            choices[("CHALLENGE",)] = self.calculate_ev_challenge(self.opp_cards, current_rank, current_bid)

        # Option 2: play bluff with k cards (k must be <= number of bluff cards)
        for k in range(1, n_bluff + 1):
            bid = BluffBid(k, current_rank, 0)
            choices[("PLAY", True, k)] = self.calculate_ev_play(cards, player_count, current_rank, bid, True)

        # Option 3: play truth with k cards (k must be <= number of truth cards)
        for k in range(1, n_truth + 1):
            bid = BluffBid(k, current_rank, 0)
            choices[("PLAY", False, k)] = self.calculate_ev_play(cards, player_count, current_rank, bid, False)

        # Fallback: if we somehow have no legal plays, challenge if possible
        if not choices:
            return None

        best_action = max(choices, key=choices.get)

        if best_action == ("CHALLENGE",):
            return None

        _, is_bluff, k = best_action
        if is_bluff:
            return bluff_cards[:k]
        else:
            return truth_cards[:k]
