from __future__ import annotations

import random
from bluff import BluffPlayer, BluffBid
from zeroorderplayer import ZeroOrderPlayer

FULL_DECK = (
    "A","A","A","A",
    "K","K","K","K",
    "Q","Q","Q","Q",
    "J","J","J","J",
)

class FirstOrderPlayer(BluffPlayer):
    def start_game(self, identifier: int, cards: tuple[str]) -> None:
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
        
        would_bluff = ZeroOrderPlayer().tom0_would_bluff(self.opp_cards, current_rank, current_bid) # type: ignore
        
        opp_pool = list(self.opp_cards)
        
        if not would_bluff:
            self._remove_specific(opp_pool, current_rank, k) #If ToM1 knows that ToM0 played truthfully, remove those cards from his pool. 
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
            self.strategy = not self.strategy   #flip to ToM0 player
    
    
    #Predictive Theory of Mind
    def calculate_ev_challenge(self, opponent_cards: tuple[str, ...], current_rank: str, opponent_last_bid: BluffBid) -> float:
        if ZeroOrderPlayer().tom0_would_bluff(opponent_cards, current_rank, opponent_last_bid): # type: ignore
            return float(self.pile_size)
        return float(-self.pile_size)
    
    def calculate_ev_play(self, my_cards: tuple[str, ...], player_count: int, current_rank: str, my_next_bid: BluffBid, i_will_bluff: bool) -> float:
        M = my_next_bid.count
        P = ZeroOrderPlayer().calculate_challenge_probability(my_cards, player_count, current_rank, my_next_bid) # type: ignore
        
        if i_will_bluff:
            return P * (-self.pile_size) + (1 - P) * M
        else:
            return P * self.pile_size + M
        
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
        
        else:
            if current_bid is not None:    
                if ZeroOrderPlayer().calculate_challenge_probability(cards, player_count, current_rank, current_bid) >= 0.75:    #designer choice (need to explain)
                    return None     #challenge if high chance to win
            
            truth_cards = [p for p in cards if all(c == current_rank for c in p)] #PROBEER 1 KAART TE PAKKEN VOOR SIMPLICITY
            bluff_cards = [p for p in cards if all(c != current_rank for c in p)]
            
            want_to_bluff = cards.count(current_rank) < 3      #I don't know if adding 'self' here so the tom1 agent can access it will break the code       
            
            if (want_to_bluff and bluff_cards) or not truth_cards:
                return bluff_cards
            else:
                return truth_cards
