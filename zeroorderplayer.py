from bluff import BluffBid, BluffPlayer
from math import comb

class ZeroOrderPlayer(BluffPlayer):

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


    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
        if current_bid is not None:    
            if self.calculate_challenge_probability(cards, player_count, current_rank, current_bid) >= 0.75:    #designer choice (need to explain)
                return None     #challenge if high chance to win
            
        truth_cards = [p for p in cards if all(c == current_rank for c in p)] #PROBEER 1 KAART TE PAKKEN VOOR SIMPLICITY
        bluff_cards = [p for p in cards if all(c != current_rank for c in p)]
        
        want_to_bluff = cards.count(current_rank) < 3         
        
        if (want_to_bluff and bluff_cards) or not truth_cards:
            return bluff_cards
        else:
            return truth_cards

        


#NOTE:
# A zero order theory of mind agent commits no theory of mind to its opponents, and treats the game as if it were a statistical "slot machine".
# So A tomo agent looks at its own hand first, then makes probabilities of which cards to play based on the rank order
# DONE: If an opponent plays more cards than there are possible in the game given the agent's own hand, always challenge. 
# If the chance that challenging is succesfull is lower than the agent playing another hand, play another hand based on the valid bids which has the highest value.
# DONE: Thus we need to make a valid bids function,  
# That is the outline for the tomo agent. 

#Now first fill in challenge probability and play probability, then fill in take_turn. 

#Code currently runs indefinitely because both agents just keep challenging each other. 