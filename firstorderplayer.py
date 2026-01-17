from bluff import BluffPlayer, BluffBid
from zeroorderplayer import ZeroOrderPlayer

class FirstOrderPlayer(BluffPlayer):
    #Interpretative Theory of Mind
    def start_game(self, identifier: int, cards: tuple[str]) -> None:
        self.my_cards = cards
        self.player_count = 2
        
        self.beliefs = {}   #Set that represents ToM1 agent's initial beliefs
        
        #Multinomial prior over opponent hand
        # for ... in ... 

        
        #difficult math here that updates initial beliefs, based on perhaps pile size 
        
        self.previous_bid = None
        self.epsilon = 0.05
                

    def tom0_decision(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
        if current_bid is not None:    
            if ZeroOrderPlayer().calculate_challenge_probability(cards, player_count, current_rank, current_bid) >= 0.75:    #designer choice (need to explain)
                return None     #challenge if high chance to win
            
        truth_cards = [p for p in cards if all(c == current_rank for c in p)] #PROBEER 1 KAART TE PAKKEN VOOR SIMPLICITY
        bluff_cards = [p for p in cards if all(c != current_rank for c in p)]
        
        want_to_bluff = cards.count(current_rank) < 3         
        
        if (want_to_bluff and bluff_cards) or not truth_cards:
            return bluff_cards
        else:
            return truth_cards

        

    def observe_bid(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, bidder_id: int, current_bid: BluffBid, bid: BluffBid) -> None:
        if current_bid is None:
            current_bid = bid
            return
        
        new_beliefs = {}
        beta = 0.0
        
        valid_plays = ...
        n = len(valid_plays) + 1  #+1 for challenge       # type: ignore
    
    def observe_challenge(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, challenger_id: int, success: bool) -> None:
        pass
    
    
    #Predictive Theory of Mind
    def calculate_ev_challenge(self, bid: BluffBid):
        pass
    
    def calculate_ev_play(self, bid: BluffBid):
        pass
    
    #Final decision
    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
        return super().take_turn(cards, player_count, current_rank, current_bid)
    
    
#NOTE: Copy code / style from assignment 2 
# Add the functionality of a tom1 player acting like a tomo player when random play is detected for extra points. 
# A ToM0 player wants to bluff only if he has fewer than 2 cards of the asked rank; use this information along with the pile checkign for a first order agent
# Then the implementation should be rather straightforward. 


# TODO: Make ToM1 agent act like ToM0 if suspicion of opponent being random... 