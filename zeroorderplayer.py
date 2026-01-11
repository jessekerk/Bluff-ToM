from bluff import BluffPlayer, BluffBid, get_valid_bluff_plays

class ZeroOrderPlayer(BluffPlayer):
    def _probabilities(self, player_count: int, j: int) -> float:
        "Helper function that does math for probabilities."
        return 0.0

    def calculate_challenge_probability(
        self,
        cards: tuple[str],
        player_count: int,
        previous_play: int,
        current_rank: str,
        current_bid: BluffBid
    ) -> float:
        return 0.0
    
    def calculate_play_probability(
        self,
        cards: tuple[str],
        player_count: int,
        previous_play: int,
        current_rank: str,
        current_Bid: BluffBid
    ) -> float:
        return 0.0

    def take_turn(
        self,
        cards: tuple[str],
        player_count: int,
        previous_play: int,
        current_rank: str,
        hand: tuple[str],
        current_bid: BluffBid
    ) -> list[str] | None:
        
        valid_plays = get_valid_bluff_plays(hand, previous_play)
        
        #Calculate play probability
        best_play = None
        best_play_probability = 0.0
        
        for play_option in valid_plays:
            #maximizing algorithm using calculate_play_probability
            pass
        
        #Calculate challenge probability
        best_challenge_probability = self.calculate_challenge_probability(cards, player_count, previous_play, current_rank, current_bid)
        
        #Main choosing logic
        if best_challenge_probability >= best_play_probability:
            return None #challenge last play
        else:
            return best_play

    
    

#NOTE:
# A zero order theory of mind agent commits no theory of mind to its opponents, and treats the game as if it were a statistical "slot machine".
# So A tomo agent looks at its own hand first, then makes probabilities of which cards to play based on the rank order
# If an opponent plays more cards than there are possible in the game given the agent's own hand, always challenge. 
# If the chance that challenging is succesfull is lower than the agent playing another hand, play another hand based on the valid bids which has the highest value.
# Thus we need to make a valid bids function,  
# That is the outline for the tomo agent. 

#Now first fill in challenge probability and play probability, then fill in take_turn. 