import os
import sys
from datetime import datetime

_log_file = None
_log_path = ""


def init_logger():
    global _log_file, _log_path
    log_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    _log_path = os.path.join(log_dir, f"pokemon_log_{timestamp}.txt")
    _log_file = open(_log_path, "w", encoding="utf-8")
    _write_header()
    log(f"Log file: {_log_path}")
    return _log_path


def _write_header():
    _log_file.write("=" * 60 + "\n")
    _log_file.write("  POKEMON TOURNAMENT - GAME LOG\n")
    _log_file.write(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    _log_file.write("=" * 60 + "\n\n")
    _log_file.flush()


def log(msg, category="INFO"):
    if _log_file is None:
        return
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{timestamp}] [{category}] {msg}"
    print(line)
    _log_file.write(line + "\n")
    _log_file.flush()


def log_section(title):
    if _log_file is None:
        return
    separator = "-" * 60
    _log_file.write(f"\n{separator}\n  {title}\n{separator}\n")
    _log_file.flush()
    print(f"\n--- {title} ---")


def log_battle_start(p1, p2, round_name=""):
    log_section(f"BATTLE: {p1.name} vs {p2.name}  [{round_name}]")
    log(f"{p1.name} | HP:{p1.max_hp} ATK:{p1.attack} DEF:{p1.defense} "
        f"SPATK:{p1.sp_attack} SPDEF:{p1.sp_defense} SPD:{p1.speed} "
        f"Type:{'/'.join(p1.types)}", "BATTLE")
    log(f"{p2.name} | HP:{p2.max_hp} ATK:{p2.attack} DEF:{p2.defense} "
        f"SPATK:{p2.sp_attack} SPDEF:{p2.sp_defense} SPD:{p2.speed} "
        f"Type:{'/'.join(p2.types)}", "BATTLE")


def log_turn(turn_number, attacker_name, move_name, defender_name, damage, multiplier, defender_hp, defender_max_hp):
    effectiveness = ""
    if multiplier == 0:
        effectiveness = " [NO EFFECT]"
    elif multiplier >= 2:
        effectiveness = " [SUPER EFFECTIVE!]"
    elif multiplier <= 0.5:
        effectiveness = " [NOT VERY EFFECTIVE]"
    if damage == 0 and multiplier != 0:
        log(f"  Turn {turn_number}: {attacker_name} used {move_name} -> {defender_name} "
            f"(Stat boost, no damage){effectiveness}", "TURN")
    else:
        log(f"  Turn {turn_number}: {attacker_name} used {move_name} -> {defender_name} "
            f"dealt {damage} dmg (x{multiplier}){effectiveness} "
            f"[HP: {defender_hp}/{defender_max_hp}]", "TURN")


def log_faint(pokemon_name):
    log(f"  *** {pokemon_name} FAINTED ***", "FAINT")


def log_battle_end(winner_name, loser_name, turns):
    log(f"  RESULT: {winner_name} defeated {loser_name} in {turns} turns", "RESULT")


def log_stat_boost(pokemon_name, stat, new_level):
    log(f"  Turn: {pokemon_name} raised {stat} to +{new_level}", "BOOST")


def log_tournament_bracket(tournament):
    log_section("TOURNAMENT BRACKET")
    round_names = ["Round of 16", "Quarter-Finals", "Semi-Finals", "Final"]
    for i, pairs in enumerate(tournament.rounds):
        rname = round_names[i] if i < len(round_names) else f"Round {i+1}"
        log(f"  {rname}:", "BRACKET")
        for p1, p2 in pairs:
            log(f"    {p1.name} vs {p2.name}", "BRACKET")


def log_tournament_result(round_name, winner, loser):
    log(f"  [{round_name}] {winner.name} advances (defeated {loser.name})", "TOURNAMENT")


def log_champion(pokemon_name, is_player):
    log_section("TOURNAMENT CHAMPION")
    if is_player:
        log(f"  *** PLAYER WINS! {pokemon_name} is the Champion! ***", "CHAMPION")
    else:
        log(f"  *** CPU WINS! {pokemon_name} is the Champion! ***", "CHAMPION")


def log_difficulty(difficulty):
    log(f"Difficulty selected: {difficulty.upper()}", "SETUP")


def log_player_pokemon(pokemon):
    log(f"Player chose: {pokemon.name} "
        f"(HP:{pokemon.max_hp} ATK:{pokemon.attack} DEF:{pokemon.defense} "
        f"SPATK:{pokemon.sp_attack} SPDEF:{pokemon.sp_defense} SPD:{pokemon.speed} "
        f"Type:{'/'.join(pokemon.types)})", "SETUP")


def log_tournament_pokemon(pokemon_list):
    log_section("TOURNAMENT ROSTER")
    for i, p in enumerate(pokemon_list, 1):
        log(f"  {i:2}. {p.name:<15} Type:{'/'.join(p.types):<15} "
            f"Total:{p.total_stats()}", "ROSTER")


def log_player_move(move_name, move_type, power):
    log(f"  Player chose: {move_name} (type:{move_type}, power:{power})", "PLAYER")


def log_cpu_move(cpu_name, move_name, move_type, power):
    log(f"  CPU ({cpu_name}) chose: {move_name} (type:{move_type}, power:{power})", "CPU")


def close_logger():
    if _log_file:
        log_section("SESSION END")
        log(f"Game session ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        _log_file.close()
