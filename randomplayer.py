from bluff import BluffPlayer
import random 

class RandomBluffPlayer(BluffPlayer):
    def take_turn(
        self,
        cards: tuple[str],
        player_count: int,
        previous_play: int,
        current_rank: str,
    ) -> list[str] | None:
        if previous_play > 0 and random.random() < 0.3:
            return None
        return [random.choice(cards)]
