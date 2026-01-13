from bluff import BluffBid, BluffPlayer, get_valid_bluff_plays
from math import comb

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
        k = current_bid.count

        
        my_count = cards.count(current_rank)                 # N_i^R
        my_played = self.played_by_me[current_rank]          # P_i^R

        N_R = 4
        N_i = len(cards)
        N_j = 16 - N_i                                       # 2-player assumption

        N_star = N_R - my_count - my_played                  # maximum opponent rank cards

        # Hard impossibility
        if k > N_star:
            return 1.0

        # Hypergeometric probability
        p_truth = comb(N_star, k) / comb(N_j, k)
        return 1.0 - p_truth


    def calculate_play_probability(
        self, cards: tuple[str], player_count: int, current_rank: str, play) -> float:  #fill in play typehint later
        return 0.0

    def observe_challenge(self, *args):
        self.played_by_me = {r:0 for r in "AJQK"}
    
    
    

    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
            # Defensive fix: convert rank index → rank character
        if isinstance(current_rank, int):
            current_rank = "AJQK"[current_rank]
            
        #Calculate challenge probability
        if current_bid is not None: #Cant challenge on the first turn
            p_challenge = self.calculate_challenge_probability(cards, player_count, current_rank, current_bid)
        else:
            p_challenge = 0.0 
    
        valid_plays = get_valid_bluff_plays(cards, current_bid)
         
        #Calculate play probability
        best_play = None
        best_play_probability = -1.0
        
        for play_option in valid_plays:
            p = self.calculate_play_probability(
                cards, player_count, current_rank, play_option
            )
            if p > best_play_probability:
                best_play_probability = p
                best_play = play_option
        
        #Choose action
        if current_bid is not None and p_challenge >= best_play_probability:
            return None #challenge
        else:
            if best_play is not None:
                for c in best_play:
                    self.played_by_me[c] += 1
            return best_play    #play the cards w/ the highest win probability

        


#NOTE:
# A zero order theory of mind agent commits no theory of mind to its opponents, and treats the game as if it were a statistical "slot machine".
# So A tomo agent looks at its own hand first, then makes probabilities of which cards to play based on the rank order
# DONE: If an opponent plays more cards than there are possible in the game given the agent's own hand, always challenge. 
# If the chance that challenging is succesfull is lower than the agent playing another hand, play another hand based on the valid bids which has the highest value.
# DONE: Thus we need to make a valid bids function,  
# That is the outline for the tomo agent. 

#Now first fill in challenge probability and play probability, then fill in take_turn. 