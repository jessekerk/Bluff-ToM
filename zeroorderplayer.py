from bluff import BluffBid, BluffPlayer
from math import comb

class ZeroOrderPlayer(BluffPlayer):
    def tom0_would_bluff(
        self,
        cards: tuple[str],
        current_rank: str,
        bid: BluffBid
    ) -> bool:
        """
        Returns True iff, given these cards, a ToM0 agent would be bluffing
        when making this bid.
        """
        # how many rank-r cards ToM0 has
        r_count = cards.count(current_rank)

        # ToM0 wants to bluff iff r_count < 3
        want_to_bluff = r_count < 3

        # If bid claims more rank-r cards than ToM0 could truthfully play,
        # then it must be a bluff
        if bid.count > r_count: #Should he not challenge here? 
            return True

        # Otherwise, follow ToM0 policy
        return want_to_bluff


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
        N_agent = len(cards)
        N_opp = 16 - N_agent                                    # 2-player assumption

        N_star = min(N_R - my_count, N_opp)            # maximum opponent rank cards

        # Hard impossibility
        if k > N_star:
            return 1.0

        # Hypergeometric probability
        p_truth = comb(N_star, k) / comb(N_opp, k)
        return 1.0 - p_truth


    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
        if current_bid is not None:    
            if self.calculate_challenge_probability(cards, player_count, current_rank, current_bid) >= 0.75:    #designer choice (need to explain)
                return None     #challenge if high chance to win
            
        truth_cards = [p for p in cards if all(c == current_rank for c in p)] #PROBEER 1 KAART TE PAKKEN VOOR SIMPLICITY
        bluff_cards = [p for p in cards if all(c != current_rank for c in p)]
        
        want_to_bluff = cards.count(current_rank) < 3      #I don't know if adding 'self' here so the tom1 agent can access it will break the code       
        
        if (want_to_bluff and bluff_cards) or not truth_cards:
            return bluff_cards[:1]
        else:
            return truth_cards[:1]

        
