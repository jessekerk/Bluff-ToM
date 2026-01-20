from __future__ import annotations

from bluff import BluffPlayer, BluffBid
from zeroorderplayer import ZeroOrderPlayer

FULL_DECK = (
    "A","A","A","A",
    "K","K","K","K",
    "Q","Q","Q","Q",
    "J","J","J","J",
)



class FirstOrderPlayer(BluffPlayer):
    #Interpretative Theory of Mind
    def start_game(self, identifier: int, cards: tuple[str]) -> None:
        self.beliefs = {}   #Set that represents ToM1 agent's initial beliefs
        self.my_cards = cards
        self.player_count = 2
        self.pile_size = 0  #change this later
        
        deck: list[str] = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
            
        self.opp_cards = tuple(deck)
        
        
        #This should calculate the # of cards in the opp hand, at the start of every round. This could get updated and calculated from 16 - len(pile) - len(self.my_cards)             
        
        #Multinomial prior over opponent hand
        # for ... in ... 


        #difficult math here that updates initial beliefs, based on perhaps pile size 
        
        self.previous_bid = None
        self.epsilon = 0.05
    


        

    def observe_bid(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, bidder_id: int, current_bid: BluffBid):   #type: ignore
        self.pile_size +=  current_bid.count    #pile size increases by the # of cards played 
        
        if self.previous_bid is None:
            self.previous_bid = current_bid     #bid I just added, don't know if it should still be there
            return
        
        new_beliefs = {}
        beta = 0.0
        
    
    def observe_challenge(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, challenger_id: int, success: bool) -> None:
        self.pile_size = 0  #pile gets picked up by loser of this challenge. 
        
    
    
    #Predictive Theory of Mind
    def calculate_ev_challenge(self, cards: tuple[str], current_rank: str, bid: BluffBid) -> float:
        if ZeroOrderPlayer().tom0_would_bluff(cards, current_rank, bid): 
            return 0.0

    
    def calculate_ev_play(self, cards: tuple[str], player_count: int, current_rank: str, bid: BluffBid) -> float:
        
                
    #Final decision
    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
