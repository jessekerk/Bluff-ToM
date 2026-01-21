from __future__ import annotations

from bluff import BluffBid,  BluffPlayer
from firstorderplayer import FirstOrderPlayer
from zeroorderplayer import ZeroOrderPlayer
import random

FULL_DECK = (
    "A","A","A","A",
    "K","K","K","K",
    "Q","Q","Q","Q",
    "J","J","J","J",
)

#second order is praktisch hetzelfde, alleen geef dan de firstorder logica door ipv the zeroorder

class SecondOrderPlayer(BluffPlayer):
    def start_game(self, identifier: int, cards: tuple[str]):
        self.beliefs = {}
        self.my_cards = cards
        self.player_count = 2
        self.pile_size = 0
        self.identifier = identifier
        self.strategy = True #Default mode is play as ToM1
        self.previous_bid: BluffBid | None = None     
        
        deck: list[str] = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
        self.opp_cards: tuple[str, ...] = tuple(deck)
    
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
    
    def observe_bid(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, bidder_id: int, current_bid: BluffBid | None) -> None:
        self.my_cards = cards
        self.player_count = player_count
        
        if current_bid is None:
            return
        
        self.pile_size += current_bid.count 
        
        self.previous_bid = current_bid   #track latest bid
        
        if bidder_id == self.identifier:
            return  #update opponent model only when opponent is bidder
        
        k = current_bid.count
        
        fo = FirstOrderPlayer()
        fo.pile_size = self.pile_size
        fo.player_count = self.player_count
        would_bluff = fo.tom1_would_bluff(self.opp_cards, player_count, current_rank, current_bid)
        
        opp_pool = list(self.opp_cards)
        
        if not would_bluff:
            self._remove_specific(opp_pool, current_rank, k) #If ToM2 knows that ToM1 played truthfully, remove those cards from his pool. 
        else:
            allowed = set('AKQJ') - {current_rank}
            self._remove_random_from(opp_pool, allowed, k)

        self.opp_cards = tuple(opp_pool)
        
    def observe_challenge(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, challenger_id: int, success: bool) -> None:
        self.pile_size = 0
        self.previous_bid = None
        
        self.my_cards = cards
        self.player_count = player_count
        
        deck: list[str] = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
        self.opp_cards = tuple(deck)
        
        if self.identifier == challenger_id and not success:
            pass
            #self.strategy = not self.strategy   #flip to ToM0 player
            
    def calculate_ev_challenge(self, opponent_cards: tuple[str, ...], current_rank: str, opponent_last_bid: BluffBid) -> float:
        fo = FirstOrderPlayer()
        fo.pile_size = self.pile_size
        fo.player_count = self.player_count
        if fo.tom1_would_bluff(opponent_cards, self.player_count, current_rank, opponent_last_bid):
            return float(self.pile_size)
        return float(-self.pile_size)

    def tom1_would_challenge(
    self,
    my_cards: tuple[str, ...],
    player_count: int,
    current_rank: str,
    current_bid: BluffBid | None,
    depth: int = 1
) -> bool:
        # Cannot challenge if there is no bid
        if current_bid is None:
            return False

        # Base case: stop recursion and use a simple proxy (ToM0-style)
        if depth <= 0:
            P = ZeroOrderPlayer().calculate_challenge_probability(
                self.opp_cards, player_count, current_rank, current_bid #type: ignore
            )
            return P >= 0.75

        # EV of challenging
        ev_chal = self.calculate_ev_challenge(
            self.opp_cards,
            current_rank,
            current_bid,
        )

        # Compute best EV among possible plays
        bluff_cards = [c for c in my_cards if c != current_rank]
        truth_cards = [c for c in my_cards if c == current_rank]

        best_play_ev = float("-inf")

        for k in range(1, len(bluff_cards) + 1):
            ev = self.calculate_ev_play(
                my_cards,
                player_count,
                current_rank,
                BluffBid(k, current_rank, 0),
                True,
                depth=depth - 1,
            )
            best_play_ev = max(best_play_ev, ev)

        for k in range(1, len(truth_cards) + 1):
            ev = self.calculate_ev_play(
                my_cards,
                player_count,
                current_rank,
                BluffBid(k, current_rank, 0),
                False,
                depth=depth - 1,
            )
            best_play_ev = max(best_play_ev, ev)

        return ev_chal >= best_play_ev



    def calculate_ev_play(
        self,
        my_cards: tuple[str, ...],
        player_count: int,
        current_rank: str,
        my_next_bid: BluffBid,
        i_will_bluff: bool,
        depth: int = 1
    ) -> float:

        M = my_next_bid.count

        # ToM2: predict whether a ToM1 opponent would challenge
        will_challenge = self.tom1_would_challenge(
            my_cards=my_cards,
            player_count=player_count,
            current_rank=current_rank,
            current_bid=my_next_bid,
            depth=depth
        )

        if i_will_bluff:
            return -self.pile_size if will_challenge else M
        else:
            return self.pile_size if will_challenge else M


    
    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid | None) -> list[str] | None:
        self.my_cards = cards
        self.player_count = player_count
        #ToM1 mode: 
        if self.strategy:
            bluff_cards = [c for c in cards if c != current_rank]
            truth_cards = [c for c in cards if c == current_rank]
            
            n_bluff = len(bluff_cards)
            n_truth = len(truth_cards)
            
            choice: dict[tuple[bool, int], float] = {}
        
            
            for k in range(1, n_bluff + 1):
                choice[(True, k)] = self.calculate_ev_play(cards, player_count, current_rank, BluffBid(k, current_rank, 0), True)
            for k in range(1, n_truth + 1):
                choice[(False, k)] = self.calculate_ev_play(cards, player_count, current_rank, BluffBid(k, current_rank, 0), False)
            
            
            best_action = max(choice, key=choice.get) # type: ignore
            
            ev_chal = 0.0
            if current_bid is not None:
                ev_chal = self.calculate_ev_challenge(self.opp_cards, current_rank, current_bid)
            
            if ev_chal >= choice[best_action]:
                self.previous_bid = None
                return None
            
            is_bluff, k = best_action
            self.previous_bid = BluffBid(k, current_rank, 0)
            
            if is_bluff:
                return random.sample(bluff_cards, k)
            else: 
                return random.sample(truth_cards, k)
    
    