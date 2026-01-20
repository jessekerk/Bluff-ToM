from bluff import BluffBid, BluffController, BluffPlayer
from firstorderplayer import FirstOrderPlayer

#second order is praktisch hetzelfde, alleen geef dan de firstorder logica door ipv the zeroorder

class SecondOrderPlayer(BluffPlayer):
    def start_game(self, identifier: int, cards: tuple[str]):
        return super().start_game(identifier, cards)
    
    def observe_bid(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, bidder_id: int) -> None:
        return super().observe_bid(cards, player_count, challenge_amount_of_cards, current_rank, bidder_id)
    
    def observe_challenge(self, cards: tuple[str], player_count: int, challenge_amount_of_cards: int, current_rank: str, challenger_id: int, success: bool) -> None:
        return super().observe_challenge(cards, player_count, challenge_amount_of_cards, current_rank, challenger_id, success)
    
    def calculate_ev_challenge(self, cards: tuple[str], player_count: int, current_rank: str, bid: BluffBid):
        pass
        
    def calculate_ev_play(self, cards: tuple[str], player_count: int, current_rank: str, bid: BluffBid):
        pass    
    
    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
        return super().take_turn(cards, player_count, current_rank, current_bid)
    
    