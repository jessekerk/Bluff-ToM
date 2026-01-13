from bluff import BluffController, BluffPlayer
from randomplayer import RandomBluffPlayer

class DebugPlayer(BluffPlayer):
    def start_game(self, identifier, cards):
        self.id = identifier

    def take_turn(self, cards, player_count, previous_play, current_rank):
        print(f"[Player {self.id}] It is my turn. Claimed rank is:", current_rank)
        # Always play 1 card so the game progresses
        return [cards[0]]

    def observe_bid(self, cards, player_count, amount, current_rank, bidder_id):
        print(
            f"[Player {self.id}] Observed bid:",
            amount, "cards of rank", current_rank,
            "by player", bidder_id
        )

    def observe_challenge(self, *args):
        pass


# Run a short game with two debug players
c = BluffController()
c.join(RandomBluffPlayer())
c.join(RandomBluffPlayer())

c.play(debug=True)
