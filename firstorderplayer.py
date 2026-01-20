from __future__ import annotations

from bluff import BluffPlayer, BluffBid
from zeroorderplayer import ZeroOrderPlayer

import random


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
        self.pile_size = 0 
        self.identifier = identifier #so we know we're the challenger later
        self.strategy = True    #to play as tom1 agent
        
        
        deck: list[str] = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
            
        self.opp_cards: tuple[str, ...] = tuple(deck) #Update dit door het aantal kaarten wat hij heeft gebluft willekeurig weg te nemen.    #dit moet nog gefixt worden.
        self.previous_bid = None 
        
    def _remove_specific(self, pool: list[str], rank: str, n: int) -> None:
        """Remove up to n copies of rank from pool (in-place)."""
        for _ in range(n):
            try:
                pool.remove(rank)
            except ValueError:
                break

    def _remove_random_from(self, pool: list[str], allowed: set[str], n: int) -> None:
        """Remove n random cards from pool where card in allowed (in-place)."""
        for _ in range(n):
            idxs = [i for i, c in enumerate(pool) if c in allowed]
            if not idxs:
                return
            i = random.choice(idxs)
            pool.pop(i)

    def observe_bid( 
        self,
        cards: tuple[str],
        player_count: int,
        challenge_amount_of_cards: int,
        current_rank: str,
        bidder_id: int,
        current_bid: BluffBid | None,
    ) -> None:  
        """
        Observe that someone made a bid.

        - Always store the latest bid so future decisions can use it.
        - Only update pile_size if we actually have a bid object.
        (This assumes your rules mean: bid.count == number of cards added to the pile.)
        """
        if current_bid is None:
            # No bid to record (e.g., start of round / before first move)
            return

        # If in your rules the bid count equals the number of cards placed into the pile:
        self.pile_size += current_bid.count

        # Track the most recent bid
        #self.previous_bid = current_bid

        
    
    def observe_challenge(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, challenger_id: int, success: bool) -> None:
        self.pile_size = 0  #pile gets picked up by loser of this challenge. 
        #Update self.opp_cards naar alle kaarten behalve cards
        self.previous_bid = None
        self.my_cards = cards
        self.player_count = player_count
        # Update opponent "possible cards" as all cards not in your (updated) hand.
        deck: list[str] = list(FULL_DECK)
        for c in cards:
            deck.remove(c)
        self.opp_cards = deck    #Once again give the opponents the cards if they are not in your hand. 
        
        if self.identifier == challenger_id and not success:
           self.strategy = not self.strategy
           
            #verander strategie
        
        #als mijn challenge niet succesvol was, verander de strategie en vice versa. 

        
    
    #Predictive Theory of Mind
    def calculate_ev_challenge(self, opponent_cards: tuple[str], current_rank: str, my_previou_bid: BluffBid) -> float:
        if ZeroOrderPlayer().tom0_would_bluff(opponent_cards, current_rank, my_previou_bid):   #if tomo would bluff, assign a high value to challenging the play. 
            return self.pile_size  #EV_challenge = pile_size if challenging is succesful to the ToM1 agent, because ToM0 picks up the pile
        return -self.pile_size  #If ToM0 has truthed, assign a low value for challenging. 



    def calculate_ev_play(self, cards: tuple[str], player_count: int, current_rank: str, my_next_bid: BluffBid, i_will_bluff: bool) -> float:
        M = my_next_bid.count   #Amount of cards tom1 wants to play #I dont know if this bid is the incoming bid or the outgoing bid. 
        #The information below presupposes ToM1 does not want to bluff. 
        P = ZeroOrderPlayer().calculate_challenge_probability(cards, player_count, current_rank, my_next_bid)
        
        if i_will_bluff:
            return P * (-self.pile_size) + (1-P) * M    #Either ev_chal is equal to - the cards you must pick up if fail, or it is equal to the cards you lose from your hand. 
        else:
           return P * self.pile_size + M

    #Final decision
    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
        #If playing as Tom1 agent
        #if self.strategy is True:   
            print("playing as tom1")
            bluff_cards = [p for p in cards if p != current_rank]
            truth_cards = [p for p in cards if p == current_rank]
            number_bluff_cards = len(bluff_cards)
            number_truth_cards = len(truth_cards)
            
            choice = {}
            for bid_number in range(1, number_bluff_cards + 1):
                choice[(True, bid_number)] = self.calculate_ev_play(self.opp_cards, player_count, current_rank, BluffBid(bid_number, current_rank, 0), True) 
            for bid_number in range(1, number_truth_cards + 1):
                choice[(False, bid_number)] = self.calculate_ev_play(self.opp_cards, player_count, current_rank, BluffBid(bid_number, current_rank, 0), False) 

            
            best_action = max(choice, key=choice.get)
            
            ev_chal = self.calculate_ev_challenge(self.opp_cards, current_rank, self.previous_bid)
            
            if ev_chal >= choice[best_action]:
                self.previous_bid = None 
                return None
            else:
                self.previous_bid = BluffBid(best_action[1], current_rank, 0)
                if best_action[0]:  #bluff
                    return random.sample(bluff_cards, best_action[1])
                else:
                    return random.sample(truth_cards, best_action[1])
        
        #If playing as ToM0 agent
        #if self.strategy is not True:
        #    if current_bid is not None:    
        #        if ZeroOrderPlayer().calculate_challenge_probability(cards, player_count, current_rank, current_bid) >= 0.75:    #designer choice (need to explain)
        #            return None     #challenge if high chance to win
        #        
        #    truth_cards = [p for p in cards if all(c == current_rank for c in p)] #PROBEER 1 KAART TE PAKKEN VOOR SIMPLICITY
        #    bluff_cards = [p for p in cards if all(c != current_rank for c in p)]
        #    
        #    want_to_bluff = cards.count(current_rank) < 3      #I don't know if adding 'self' here so the tom1 agent can access it will break the code       
        #    
        #    if (want_to_bluff and bluff_cards) or not truth_cards:
        #        return bluff_cards
        #    else:
        #        return truth_cards


        

#Om de tom1 naar een tom0 te zetten, wanneer de tom1 zeker weet dat de opponent gaat bluffen, maar er is niet gebluft, is zijn opponent een randomplayer
#In andere woorden, wanneer de tom1's challenge onsuccesvol is


# TODO: Make ToM1 agent act like ToM0 if suspicion of opponent being random... 
#To do that.. 
#If challenging results in a failure as a ToM1 agent, change strat. 
#Use the private functions to update beliefs of opponent's hand. 