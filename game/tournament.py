import random
from game.battle import Battle
from game.ai import CPU_AI


class Tournament:
    def __init__(self, pokemon_list, player_pokemon, difficulty):
        self.all_pokemon = pokemon_list[:]
        self.player_pokemon = player_pokemon
        self.difficulty = difficulty
        self.ai = CPU_AI(difficulty)

        # Build bracket: 16 pokemon, 4 rounds
        random.shuffle(self.all_pokemon)
        # Make sure player is in the list
        if player_pokemon not in self.all_pokemon:
            self.all_pokemon[0] = player_pokemon

        self.rounds = []  # list of rounds, each round is list of matches [(p1,p2), ...]
        self.results = []  # list of rounds results, each is list of winners
        self.current_round = 0
        self.current_match = 0

        # Initialize round 1
        self._build_round(self.all_pokemon)

    def _build_round(self, participants):
        pairs = []
        for i in range(0, len(participants), 2):
            pairs.append((participants[i], participants[i+1]))
        self.rounds.append(pairs)
        self.results.append([None] * len(pairs))

    def get_current_match(self):
        if self.current_round >= len(self.rounds):
            return None, None
        matches = self.rounds[self.current_round]
        if self.current_match >= len(matches):
            return None, None
        return self.current_match, matches[self.current_match]

    def is_player_in_match(self, match):
        if match is None:
            return False
        return self.player_pokemon in match

    def simulate_cpu_match(self, p1, p2):
        p1.reset_battle()
        p2.reset_battle()
        ai1 = CPU_AI(self.difficulty)
        ai2 = CPU_AI(self.difficulty)
        battle = Battle(p1, p2, ai1, ai2)
        winner = battle.simulate_full()
        return winner

    def record_result(self, winner):
        self.results[self.current_round][self.current_match] = winner
        self.current_match += 1

        # Check if round complete
        matches = self.rounds[self.current_round]
        if self.current_match >= len(matches):
            # Advance to next round
            winners = self.results[self.current_round]
            if len(winners) > 1:
                # Reset for new round
                for w in winners:
                    w.reset_battle()
                self._build_round(winners)
                self.current_round += 1
                self.current_match = 0
            else:
                # Tournament over
                self.current_round += 1

    def is_finished(self):
        return (self.current_round > 0 and
                self.current_round == len(self.rounds) and
                len(self.results[-1]) == 1 and
                self.results[-1][0] is not None)

    def get_champion(self):
        if self.results and self.results[-1]:
            return self.results[-1][0]
        return None

    def player_eliminated(self):
        """Check if player was eliminated."""
        for round_results in self.results:
            for winner in round_results:
                if winner is not None and winner != self.player_pokemon:
                    # Check if player was in that match
                    round_idx = self.results.index(round_results)
                    match_idx = round_results.index(winner)
                    if round_idx < len(self.rounds):
                        match = self.rounds[round_idx][match_idx]
                        if self.player_pokemon in match:
                            return True
        return False

    def get_round_name(self):
        total_rounds = 4  # for 16 pokemon
        r = self.current_round
        names = ["Round of 16", "Quarter-Finals", "Semi-Finals", "Final"]
        if r < len(names):
            return names[r]
        return "Tournament Over"
