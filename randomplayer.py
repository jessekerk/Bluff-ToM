from bluff import BluffPlayer, BluffBid, get_valid_bluff_plays
import random 

class RandomBluffPlayer(BluffPlayer):
    def take_turn(self, cards: tuple[str], player_count: int, current_rank: str, current_bid: BluffBid) -> list[str] | None:
        if current_bid is not None and random.random() < 0.3:     #30 percent chance to challenge. 
            return None

        valid_plays = get_valid_bluff_plays(cards, current_bid)
        if not valid_plays:
            return None
        return random.choice(valid_plays)
