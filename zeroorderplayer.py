from bluff import BluffBid, BluffPlayer, get_valid_bluff_plays
from math import comb
    
import random
class ZeroOrderPlayer(BluffPlayer):
    def _probabilities(self, player_count: int, j: int) -> float:
        "Helper function that does math for probabilities."
        return 0.0



    def calculate_challenge_probability(
        self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> float:
        #if incoming cards + the cards in this agent's hand higher than 4, challenge NOTE: in a 3+ player game you would have to keep track of previously played 
        # cards to see if that exceeds 4 -> Tom0 agent w/ explicit memory
        
        # Defensive fix: convert rank index to rank character
        if isinstance(current_rank, int):
            current_rank = "AJQK"[current_rank]
        if current_bid is None:
            return 0.0  #dont challenge on the first round
        k = current_bid.count

        my_count = cards.count(current_rank)                 # N_i^R

        N_R = 4
        N_i = len(cards)
        N_j = 16 - N_i                                       # 2-player assumption

        N_star = min(N_R - my_count, N_j)            # maximum opponent rank cards

        # Hard impossibility
        if k > N_star:
            return 1.0

        # Hypergeometric probability
        p_truth = comb(N_star, k) / comb(N_j, k)
        return 1.0 - p_truth



    RANKS = "AJQK"

    def calculate_play_probability(
        self,
        cards: tuple[str],
        player_count: int,
        current_rank: str,
        play: list[str],
        current_bid: BluffBid
    ) -> float:
        """
        Returns a score ~ probability opponent won't challenge.
        ToM0: crude deck-based plausibility + small preference to shed cards truthfully.
        Assumes 2-player, 16-card game.
        """
        if current_bid is None:
            return 1.0  #always play on the first round
        else:
            if self.calculate_challenge_probability(cards, player_count, current_rank, current_bid) >= 0.80:
                return 0.0  #Challenge
            else:
                return 1.0  #Play
        
        
        valid_plays = get_valid_bluff_plays(cards, current_bid) #current bid is not used in this function
        # Deterministic choice to bluff whether or not (compare it against a value)
        
        if ...:
            pass
            #we will bluff
        
        if ...:
            #we will play truthfully
            if current_bid is None:
                rank_cards = [c for c in cards if c == current_rank]
                k = random.randint(1, len(rank_cards))
                return random.sample(rank_cards, k) #This plays a random amount of cards of rank R. 
        
        else: 
            #If a tom0 agent is asked to play a card of rank r which it has, it plays that card (Play one card)
            my_count = cards.count(current_rank)    #amount of cards of rank R
        
        

    def observe_challenge(self, *args): # type: ignore
        self.played_by_me = {r:0 for r in "AJQK"}
    
    
    

    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
            # Defensive fix: convert rank index to rank character
        if isinstance(current_rank, int):
            current_rank = "AJQK"[current_rank]
        
        if current_bid is not None:    
            if self.calculate_challenge_probability(cards, player_count, current_rank, current_bid) >= 0.80:    #designer choice (need to explain)
                return None     #challenge if high chance to win
    
        #Play
        #valid_plays = get_valid_bluff_plays(cards, current_bid)

        #truthful_plays = [p for p in valid_plays if all(c == current_rank for c in p)]
        #bluff_plays    = [p for p in valid_plays if not all(c == current_rank for c in p)]

        truth_cards = [p for p in cards if all(c == current_rank for c in p)] #PROBEER 1 KAART TE PAKKEN VOOR SIMPLICITY (Harmen)
        bluff_cards = [p for p in cards if all(c != current_rank for c in p)]
        
        
        want_to_bluff = cards.count(current_rank) < 3            #deterministic choice if you have less than 3 of rank r, bluff #*Describe in report
        want_to_play_truthfully = cards.count(current_rank) > 2 #deterministic choice if you have more than 2 of rank r, truth
        
        
        
        if (want_to_bluff and bluff_cards) or not truth_cards:
            return bluff_cards
        else:
            return truth_cards
   
   
    #       # if bluff is not possible fall back
    #       return random.choice(valid_plays)

    #   if want_to_play_truthfully:
    #       if truthful_plays:
    #           return random.choice(truthful_plays)
    #       # can't play truthful if you don't have the rank; fall back to bluff:
    #       if bluff_plays:
    #           return random.choice(bluff_plays)
    #       return random.choice(valid_plays)
#
     #   #Calculate play probability
     #   best_play = None
     #   best_play_probability = -1.0
     #   
     #   for play_option in valid_plays:
     #       p = self.calculate_play_probability(
     #           cards, player_count, current_rank, play_option, current_bid
     #       )
     #       if p > best_play_probability:
     #           best_play_probability = p
     #           best_play = play_option
     #   
     #   #Choose action
     #   if current_bid is not None and p_challenge >= best_play_probability:
     #       return None #challenge
     #   else:
     #       if best_play is not None:1
     #       return best_play    #play the cards w/ the highest win probability

        


#NOTE:
# A zero order theory of mind agent commits no theory of mind to its opponents, and treats the game as if it were a statistical "slot machine".
# So A tomo agent looks at its own hand first, then makes probabilities of which cards to play based on the rank order
# DONE: If an opponent plays more cards than there are possible in the game given the agent's own hand, always challenge. 
# If the chance that challenging is succesfull is lower than the agent playing another hand, play another hand based on the valid bids which has the highest value.
# DONE: Thus we need to make a valid bids function,  
# That is the outline for the tomo agent. 

#Now first fill in challenge probability and play probability, then fill in take_turn. 

#Code currently runs indefinitely because both agents just keep challenging each other. 