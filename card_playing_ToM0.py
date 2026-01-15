 RANKS = "AJQK"

    def calculate_play_probability(
        self,
        cards: tuple[str],
        player_count: int,
        current_rank: str,
        play: list[str],
    ) -> float:
        """
        Returns a score ~ probability opponent won't challenge.
        ToM0: crude deck-based plausibility + small preference to shed cards truthfully.
        Assumes 2-player, 16-card game.
        """

        k = len(play)
        if k == 0:
            return -1.0

        my_count = cards.count(current_rank)
        N_i = len(cards)
        N_j = 16 - N_i

        # Plausibility that "k of current_rank" is believable to opponent
        # (same structure as your challenge truth probability)
        N_star = min(4 - my_count, N_j)

        if k > N_star:
            p_truth = 0.0
        else:
            p_truth = comb(N_star, k) / comb(N_j, k)

        # Determine if play is truthful (all cards are actually current_rank)
        truthful = all(c == current_rank for c in play)

        # Score: want high plausibility, want to shed cards, prefer truthful shedding
        score = p_truth

        # prefer getting rid of more cards, but not too aggressively
        score += 0.05 * k

        # punish bluffing slightly (ToM0 cautious)
        if not truthful:
            score -= 0.10 * k

        return score


    def choose_play(self, cards: tuple[str], current_rank: str) -> list[str]:
        # generate plays: truthful options first, otherwise bluff 1
        truthful_cards = [c for c in cards if c == current_rank]

        if truthful_cards:
            # candidate truthful plays: 1..min(4, count)
            max_k = min(4, len(truthful_cards))
            candidates = [truthful_cards[:k] for k in range(1, max_k + 1)]
        else:
            # must bluff: only 1-card bluffs (lowest risk)
            candidates = [[random.choice(cards)]]

        best = candidates[0]
        best_score = -1e9
        for play in candidates:
            s = self.calculate_play_probability(cards, 2, current_rank, play)
            if s > best_score:
                best_score = s
                best = play
        return best
