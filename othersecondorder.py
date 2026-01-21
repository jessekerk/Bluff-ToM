from __future__ import annotations

from bluff import BluffBid, BluffPlayer
from firstorderplayer import FirstOrderPlayer
from zeroorderplayer import ZeroOrderPlayer

import random
from typing import Optional

# Assumes these exist in your project:
# - FULL_DECK: tuple[str, ...] or list[str]
# - BluffPlayer base class
# - BluffBid dataclass/class with .count and (optionally) .rank
# - ZeroOrderPlayer with:
#     - tom0_would_bluff(cards: tuple[str, ...], current_rank: str, proposed_bid: BluffBid) -> bool
#     - calculate_challenge_probability(cards: tuple[str, ...], player_count: int, current_rank: str, current_bid: BluffBid) -> float
# - FirstOrderPlayer with:
#     - tom1_would_bluff(my_cards: tuple[str, ...], player_count: int, current_rank: str, proposed_bid: BluffBid) -> bool

FULL_DECK = (
    "A","A","A","A",
    "K","K","K","K",
    "Q","Q","Q","Q",
    "J","J","J","J",
)

class SecondOrderPlayer(BluffPlayer):
    """
    ToM2 agent: models opponent as ToM1.
    Key fix vs your recursive version:
      - We DO NOT define "ToM1 would challenge" in terms of "best EV play" (which recurses).
      - Instead, we approximate ToM1's challenge decision from its estimated probability of winning a challenge.
    """

    def start_game(self, identifier: int, cards: tuple[str, ...]) -> None:
        self.beliefs = {}
        self.my_cards = cards
        self.player_count = 2
        self.pile_size = 0
        self.identifier = identifier

        self.strategy = True  # you can keep this if you want mode switching
        self.previous_bid: Optional[BluffBid] = None

        # Track opponent hand size explicitly (2-player game, 16-card deck -> 8 each initially)
        self.opp_hand_size = len(FULL_DECK) - len(cards)

        # Belief pool: cards opponent could still have (start = FULL_DECK minus my hand)
        deck = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
        self.opp_pool: list[str] = deck  # mutable belief pool

    # -------------------------
    # Small utilities for belief updates
    # -------------------------
    def _remove_specific(self, pool: list[str], rank: str, n: int) -> None:
        for _ in range(n):
            try:
                pool.remove(rank)
            except ValueError:
                break

    def _remove_random_from(self, pool: list[str], allowed: set[str], n: int) -> None:
        for _ in range(n):
            idxs = [i for i, c in enumerate(pool) if c in allowed]
            if not idxs:
                return
            pool.pop(random.choice(idxs))

    def _fresh_tom1_model(self) -> "FirstOrderPlayer":
        """
        Option 2 style: create a temporary ToM1 instance and initialize required state.
        This avoids AttributeError from uninitialized pile_size, etc.
        """
        fo = FirstOrderPlayer()
        fo.pile_size = self.pile_size
        fo.player_count = self.player_count
        return fo

    # -------------------------
    # Observations
    # -------------------------
    def observe_bid(
        self,
        cards: tuple[str, ...],
        player_count: int,
        challenge_amount_of_cards: int,
        current_rank: str,
        bidder_id: int,
        current_bid: Optional[BluffBid],
    ) -> None:
        self.my_cards = cards
        self.player_count = player_count

        if current_bid is None:
            return

        k = current_bid.count
        self.pile_size += k
        self.previous_bid = current_bid

        # Update opponent hand size if opponent played this bid
        if bidder_id != self.identifier:
            self.opp_hand_size = max(0, self.opp_hand_size - k)
        else:
            return  # only update opponent model when opponent is bidder

        # ToM2 belief update: assume opponent is ToM1; infer whether ToM1 would be bluffing
        fo = self._fresh_tom1_model()

        # IMPORTANT: ToM1 "my_cards" parameter is what ToM2 thinks opponent could have.
        # We approximate with a sample hand drawn from our belief pool.
        # (Because passing the entire pool as a "hand" is not a real hand.)
        assumed_opp_hand = tuple(random.sample(self.opp_pool, k=min(self.opp_hand_size, len(self.opp_pool))))

        would_bluff = fo.tom1_would_bluff(assumed_opp_hand, player_count, current_rank, current_bid)  # type: ignore

        if not would_bluff:
            # If ToM2 thinks opponent played truthfully: remove rank cards from pool
            self._remove_specific(self.opp_pool, current_rank, k)
        else:
            # If bluff: remove random non-rank cards from pool
            allowed = set("AKQJ") - {current_rank}
            self._remove_random_from(self.opp_pool, allowed, k)

    def observe_challenge(
        self,
        cards: tuple[str, ...],
        player_count: int,
        challenge_amount_of_cards: int,
        current_rank: str,
        challenger_id: int,
        success: bool,
    ) -> None:
        # After a challenge resolves, pile is cleared in your framework
        self.pile_size = 0
        self.previous_bid = None

        self.my_cards = cards
        self.player_count = player_count

        # Reset belief pool to FULL_DECK minus my current hand
        deck = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
        self.opp_pool = deck
        self.opp_hand_size = len(FULL_DECK) - len(cards)

        # Optional: switch modes if you want
        # if self.identifier == challenger_id and not success:
        #     self.strategy = not self.strategy

    # -------------------------
    # ToM2 EV models
    # -------------------------
    def calculate_ev_challenge(
        self,
        opponent_pool_snapshot: tuple[str, ...],
        current_rank: str,
        opponent_last_bid: BluffBid,
    ) -> float:
        """
        EV of challenging opponent's last bid, from ToM2's perspective.
        We model opponent as ToM1 and decide if that ToM1 would have bluffed.
        """
        fo = self._fresh_tom1_model()

        # Approximate opponent's actual hand by sampling from the pool snapshot
        pool_list = list(opponent_pool_snapshot)
        sample_n = min(self.opp_hand_size, len(pool_list))
        assumed_opp_hand = tuple(random.sample(pool_list, k=sample_n))

        if fo.tom1_would_bluff(assumed_opp_hand, self.player_count, current_rank, opponent_last_bid):  # type: ignore
            return float(self.pile_size)   # challenge succeeds -> gain pile (per your payoff convention)
        return float(-self.pile_size)      # challenge fails -> lose pile

    def predict_tom1_challenge_probability(
        self,
        current_rank: str,
        my_next_bid: BluffBid,
        sims: int = 30,
    ) -> float:
        """
        Predict (approx) probability that a ToM1 opponent challenges our bid.
        We approximate ToM1 as using ToM0's challenge probability based on *its own hand*,
        which we don't know. So we Monte Carlo sample a plausible opponent hand from opp_pool.
        """
        # If pile is empty or trivial, you can still challenge, but probability estimate works anyway.
        sims = max(1, sims)

        zo = ZeroOrderPlayer()
        challenges = 0

        pool = self.opp_pool
        sample_n = min(self.opp_hand_size, len(pool))

        if sample_n == 0:
            return 0.0

        for _ in range(sims):
            opp_hand = tuple(random.sample(pool, k=sample_n))
            p_win = zo.calculate_challenge_probability(opp_hand, self.player_count, current_rank, my_next_bid)  # type: ignore
            # ToM1 challenges if EV(challenge) >= 0  <=>  p_win >= 0.5 (given symmetric +/- pile payoff)
            if p_win >= 0.5:
                challenges += 1

        return challenges / sims

    def calculate_ev_play(
        self,
        my_cards: tuple[str, ...],
        player_count: int,
        current_rank: str,
        my_next_bid: BluffBid,
        i_will_bluff: bool,
    ) -> float:
        """
        EV of making bid my_next_bid (and playing M cards).
        Uses a non-recursive opponent challenge prediction.
        """
        M = my_next_bid.count

        p_chal = self.predict_tom1_challenge_probability(current_rank, my_next_bid, sims=30)

        if i_will_bluff:
            # If challenged, you lose pile; if not, you gain M (per your conventions)
            return p_chal * (-self.pile_size) + (1 - p_chal) * M
        else:
            # If truthful and challenged, you win pile; otherwise you still bank M
            return p_chal * (self.pile_size) + (1 - p_chal) * M

    # -------------------------
    # Action selection
    # -------------------------
    def take_turn(
        self,
        cards: tuple[str, ...],
        player_count: int,
        current_rank: str,
        current_bid: Optional[BluffBid],
    ) -> Optional[list[str]]:
        self.my_cards = cards
        self.player_count = player_count

        # Build candidate plays
        bluff_cards = [c for c in cards if c != current_rank]
        truth_cards = [c for c in cards if c == current_rank]

        choice: dict[tuple[bool, int], float] = {}

        for k in range(1, len(bluff_cards) + 1):
            bid = BluffBid(k, current_rank, 0)
            choice[(True, k)] = self.calculate_ev_play(cards, player_count, current_rank, bid, True)

        for k in range(1, len(truth_cards) + 1):
            bid = BluffBid(k, current_rank, 0)
            choice[(False, k)] = self.calculate_ev_play(cards, player_count, current_rank, bid, False)

        # If we cannot play anything (shouldn't happen), challenge if possible
        if not choice:
            self.previous_bid = None
            return None

        best_action = max(choice, key=choice.get)

        # Consider challenging current bid
        ev_chal = float("-inf")
        if current_bid is not None:
            ev_chal = self.calculate_ev_challenge(tuple(self.opp_pool), current_rank, current_bid)

        # If challenging is better than best play, challenge
        if current_bid is not None and ev_chal >= choice[best_action]:
            self.previous_bid = None
            return None

        # Otherwise play best bid
        is_bluff, k = best_action
        self.previous_bid = BluffBid(k, current_rank, 0)

        if is_bluff:
            return random.sample(bluff_cards, k)
        return random.sample(truth_cards, k)
