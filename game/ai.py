import random
from game.type_chart import get_type_multiplier


class CPU_AI:
    def __init__(self, difficulty):
        self.difficulty = difficulty  # "easy", "normal", "hard"

    def choose_pokemon(self, pool, player_pokemon=None):
        if self.difficulty == "easy":
            return random.choice(pool)
        elif self.difficulty == "normal":
            return max(pool, key=lambda p: p.total_stats())
        else:  # hard
            if player_pokemon is None:
                return max(pool, key=lambda p: p.total_stats())
            best, best_score = None, -1
            for p in pool:
                score = sum(get_type_multiplier(t, player_pokemon.types) for t in p.types)
                if score > best_score or (
                    score == best_score and best is not None and
                    (p.speed > best.speed or
                     (p.speed == best.speed and (p.defense + p.sp_defense) > (best.defense + best.sp_defense)))
                ):
                    best_score, best = score, p
            return best if best else random.choice(pool)

    def choose_move(self, attacker, defender):
        moves = attacker.moves
        # moves[0] = Attacco fisico
        # moves[1] = Difesa
        # moves[2] = Attacco Speciale
        # moves[3] = Difesa Speciale

        if self.difficulty == "easy":
            return random.choice(moves)

        elif self.difficulty == "normal":
            # Sceglie l'attacco con più danno grezzo (senza tipo)
            atk_dmg  = max(0, attacker.attack   - defender.defense)
            spatk_dmg= max(0, attacker.sp_attack - defender.sp_defense)
            return moves[0] if atk_dmg >= spatk_dmg else moves[2]

        else:  # hard
            # Preferisce Attacco Speciale se il moltiplicatore è favorevole
            mult = get_type_multiplier(attacker.types[0], defender.types)
            spatk_dmg = max(0, int(attacker.sp_attack * mult) - defender.sp_defense)
            atk_dmg   = max(0, attacker.attack - defender.defense)

            if mult >= 2 and spatk_dmg > 0:
                return moves[2]  # Attacco Speciale super efficace
            elif atk_dmg >= spatk_dmg:
                return moves[0]  # Attacco fisico fa più danno
            else:
                return moves[2]  # Attacco Speciale fa più danno