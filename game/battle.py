import math
from game.type_chart import get_type_multiplier, get_effectiveness_text
from game import logger


def calc_damage(attacker, move, defender):
    """
    Calcolo danno:
    - Attacco fisico:   ATK_attaccante - DEF_difensore  (no moltiplicatori tipo)
    - Attacco speciale: SP_ATK_attaccante * moltiplicatore_tipo - SP_DEF_difensore
    Minimo 1 di danno se l'attacco va a segno (moltiplicatore > 0).
    """
    if move.power == 0:
        return 0, 1.0

    if move.move_type == "physical":
        # Attacco fisico: nessun moltiplicatore di tipo
        raw = attacker.attack - defender.defense
        damage = max(1, raw)
        multiplier = 1.0

    else:
        # Attacco speciale: si applica il moltiplicatore di tipo
        multiplier = get_type_multiplier(move.attack_type, defender.types)
        raw = math.floor(attacker.sp_attack * multiplier) - defender.sp_defense
        if multiplier == 0:
            damage = 0
        else:
            damage = max(1, raw)

    return damage, multiplier


class Battle:
    def __init__(self, pokemon1, pokemon2, ai1=None, ai2=None, round_name=""):
        self.pokemon1   = pokemon1
        self.pokemon2   = pokemon2
        self.ai1        = ai1
        self.ai2        = ai2
        self.log        = []
        self.turn       = 0
        self.finished   = False
        self.winner     = None
        self.last_effectiveness = ""
        self.last_damage_p1 = 0
        self.last_damage_p2 = 0
        self.round_name = round_name

        # Mosse scelte nel turno corrente (usate da apply_defense)
        self._p1_defending    = False
        self._p2_defending    = False
        self._p1_sp_defending = False
        self._p2_sp_defending = False

        logger.log_battle_start(pokemon1, pokemon2, round_name)

    def _reset_turn_flags(self):
        self._p1_defending    = False
        self._p2_defending    = False
        self._p1_sp_defending = False
        self._p2_sp_defending = False

    def apply_move(self, attacker, move, defender, is_p1_attacker):
        """
        Esegue una mossa. Gestisce:
        - Attacco fisico:   danno = ATK - DEF  (DEF può essere aumentata dalla mossa Difesa)
        - Attacco speciale: danno = SP_ATK * tipo_mult - SP_DEF
        - Difesa:           il pokemon usa la propria DEF come scudo per questo turno
                            (viene segnato il flag, gestito in apply_damage_with_shield)
        - Difesa Speciale:  idem con SP_DEF
        """
        msgs = []

        if move.move_type == "defense":
            if is_p1_attacker:
                self._p1_defending = True
            else:
                self._p2_defending = True
            msgs.append(f"{attacker.name} si mette in difesa!")
            logger.log(f"  {attacker.name} usa Difesa (DEF={attacker.defense})", "TURN")
            return msgs, 0, 1.0

        elif move.move_type == "sp_defense":
            if is_p1_attacker:
                self._p1_sp_defending = True
            else:
                self._p2_sp_defending = True
            msgs.append(f"{attacker.name} si mette in difesa speciale!")
            logger.log(f"  {attacker.name} usa Difesa Speciale (SP_DEF={attacker.sp_defense})", "TURN")
            return msgs, 0, 1.0

        else:
            # Calcola danno base
            dmg, mult = calc_damage(attacker, move, defender)

            # Applica scudo difensivo se il difensore ha usato Difesa/Difesa Speciale
            is_defender_p1 = not is_p1_attacker
            if move.move_type == "physical":
                if is_defender_p1 and self._p1_defending:
                    # danno = max(0, ATK - DEF*2)  → difesa raddoppiata per il turno
                    shielded = max(0, attacker.attack - defender.defense * 2)
                    logger.log(f"  {defender.name} in difesa! Danno ridotto da {dmg} a {shielded} "
                               f"(ATK {attacker.attack} - DEF*2 {defender.defense*2})", "SHIELD")
                    dmg = shielded
                elif not is_defender_p1 and self._p2_defending:
                    shielded = max(0, attacker.attack - defender.defense * 2)
                    logger.log(f"  {defender.name} in difesa! Danno ridotto da {dmg} a {shielded} "
                               f"(ATK {attacker.attack} - DEF*2 {defender.defense*2})", "SHIELD")
                    dmg = shielded
            elif move.move_type == "special":
                if is_defender_p1 and self._p1_sp_defending:
                    shielded = max(0, math.floor(attacker.sp_attack * mult) - defender.sp_defense * 2)
                    logger.log(f"  {defender.name} in difesa speciale! Danno ridotto da {dmg} a {shielded}", "SHIELD")
                    dmg = shielded
                elif not is_defender_p1 and self._p2_sp_defending:
                    shielded = max(0, math.floor(attacker.sp_attack * mult) - defender.sp_defense * 2)
                    logger.log(f"  {defender.name} in difesa speciale! Danno ridotto da {dmg} a {shielded}", "SHIELD")
                    dmg = shielded

            if dmg > 0:
                defender.take_damage(dmg)

            msgs.append(f"{attacker.name} usa Attacco{'  Speciale' if move.move_type == 'special' else ''}!")
            eff_text = get_effectiveness_text(mult) if move.move_type == "special" else ""
            if eff_text:
                msgs.append(eff_text)
            if dmg == 0 and mult == 0:
                msgs.append("Non ha alcun effetto!")
            elif dmg == 0:
                msgs.append(f"{defender.name} ha bloccato tutto il danno!")
            else:
                msgs.append(f"{defender.name} subisce {dmg} danni!")

            logger.log_turn(self.turn + 1, attacker.name, move.name, defender.name,
                            dmg, mult, defender.hp, defender.max_hp)

            if not defender.is_alive():
                msgs.append(f"{defender.name} è esausto!")
                logger.log_faint(defender.name)

            return msgs, dmg, mult

    def run_turn(self, player_move_idx=None):
        """Per battaglie CPU vs CPU."""
        self._reset_turn_flags()
        p1, p2 = self.pokemon1, self.pokemon2

        move1 = self.ai1.choose_move(p1, p2) if self.ai1 else p1.moves[player_move_idx or 0]
        move2 = self.ai2.choose_move(p2, p1) if self.ai2 else p2.moves[0]

        logger.log_cpu_move(p1.name, move1.name, move1.attack_type, move1.power)
        logger.log_cpu_move(p2.name, move2.name, move2.attack_type, move2.power)

        # Ordine per Speed
        if p1.speed >= p2.speed:
            first, fm, second, sm, fp1 = p1, move1, p2, move2, True
        else:
            first, fm, second, sm, fp1 = p2, move2, p1, move1, False

        all_msgs = []

        msgs, dmg, mult = self.apply_move(first, fm, second, fp1)
        all_msgs.extend(msgs)
        self.last_damage_p1 = dmg if fp1 else 0
        self.last_damage_p2 = dmg if not fp1 else 0
        self.last_effectiveness = get_effectiveness_text(mult)

        if not second.is_alive():
            self.finished = True
            self.winner   = first
            self.log.extend(all_msgs)
            logger.log_battle_end(first.name, second.name, self.turn + 1)
            return all_msgs

        msgs, dmg, mult = self.apply_move(second, sm, first, not fp1)
        all_msgs.extend(msgs)
        if fp1:
            self.last_damage_p2 = dmg
        else:
            self.last_damage_p1 = dmg

        if not first.is_alive():
            self.finished = True
            self.winner   = second
            logger.log_battle_end(second.name, first.name, self.turn + 1)

        self.turn += 1
        self.log.extend(all_msgs)
        return all_msgs

    def simulate_full(self):
        while not self.finished and self.turn < 200:
            self.run_turn()
        if not self.finished:
            self.winner   = self.pokemon1 if self.pokemon1.hp >= self.pokemon2.hp else self.pokemon2
            self.finished = True
            loser = self.pokemon2 if self.winner == self.pokemon1 else self.pokemon1
            logger.log_battle_end(self.winner.name, loser.name, self.turn)
        return self.winner