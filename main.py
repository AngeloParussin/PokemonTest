"""
Pokemon Tournament Game
Retro-style Pokemon battle game using pygame.

HOW TO RUN:
1. Place this file in your /PokemonGame folder
2. Ensure pokedex.json and types.json are present
3. Optional: add pokemon_images/PokemonName.png sprites
4. Install pygame:  pip install pygame
5. Run:             python main.py
"""

import pygame
import json
import random
import os
import sys

# ═══════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════
SCREEN_W, SCREEN_H = 640, 480
FPS      = 60
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Retro palette
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
DGRAY  = (40,  40,  40)
LGRAY  = (180, 180, 180)
GREEN  = (0,   200, 0)
DGREEN = (0,   120, 0)
RED    = (220, 0,   0)
YELLOW = (240, 200, 0)
BLUE   = (0,   80,  200)
LBLUE  = (100, 160, 255)
CREAM  = (248, 248, 216)
DBLUE  = (24,  24,  112)

# ═══════════════════════════════════════════════════════
#  TERMINAL LOGGER  — prints everything that happens
# ═══════════════════════════════════════════════════════
class Log:
    @staticmethod
    def section(title):
        line = "═" * 55
        print(f"\n{line}")
        print(f"  {title}")
        print(line)

    @staticmethod
    def info(text):
        print(f"  {text}")

    @staticmethod
    def battle(text):
        print(f"  ⚔  {text}")

    @staticmethod
    def effect(text):
        print(f"  ✦  {text}")

    @staticmethod
    def hp(name, hp, max_hp):
        filled = int(20 * max(0, hp) / max(1, max_hp))
        bar    = "█" * filled + "░" * (20 - filled)
        print(f"  HP {name:<14} [{bar}] {max(0,hp):>3}/{max_hp}")

    @staticmethod
    def winner(name):
        print(f"\n  🏆  {name} WINS!\n")

    @staticmethod
    def faint(name):
        print(f"  ✖  {name} fainted!")

# ═══════════════════════════════════════════════════════
#  JSON LOADERS
# ═══════════════════════════════════════════════════════
def load_pokedex():
    path = os.path.join(BASE_DIR, "pokedex.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_types():
    path = os.path.join(BASE_DIR, "types.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ═══════════════════════════════════════════════════════
#  TYPE EFFECTIVENESS CALCULATOR
# ═══════════════════════════════════════════════════════
class TypeCalculator:
    def __init__(self, types_data):
        self.data = {}
        for entry in types_data:
            name = entry["english"]
            self.data[name] = {
                "effective":   entry.get("effective",   []),
                "ineffective": entry.get("ineffective", []),
                "no_effect":   entry.get("no_effect",   []),
            }

    def get_multiplier(self, attack_type, defender_types):
        mult = 1.0
        td   = self.data.get(attack_type)
        if not td:
            return 1.0
        for dt in defender_types:
            if dt in td["no_effect"]:
                mult *= 0.0
            elif dt in td["ineffective"]:
                mult *= 0.5
            elif dt in td["effective"]:
                mult *= 2.0
        return mult

# ═══════════════════════════════════════════════════════
#  POKEMON CLASS
# ═══════════════════════════════════════════════════════
class Pokemon:
    def __init__(self, data_entry):
        self.id         = data_entry["id"]
        self.name       = data_entry["name"]["english"]
        self.types      = data_entry["type"]
        base            = data_entry["base"]
        self.max_hp     = base["HP"]
        self.hp         = base["HP"]
        self.attack     = base["Attack"]
        self.defense    = base["Defense"]
        self.sp_attack  = base["Sp. Attack"]
        self.sp_defense = base["Sp. Defense"]
        self.speed      = base["Speed"]
        self.level      = random.randint(50, 100)

    def is_alive(self):
        return self.hp > 0

    def heal(self):
        self.hp = self.max_hp

    def __repr__(self):
        return f"{self.name}(HP:{self.hp}/{self.max_hp})"

# ═══════════════════════════════════════════════════════
#  MOVE COOLDOWN TRACKER
# ═══════════════════════════════════════════════════════
MOVES = ["attack", "defense", "special_attack", "special_defense"]

class CooldownTracker:
    def __init__(self):
        self.last_move = None
        self.count     = 0

    def can_use(self, move):
        return not (self.last_move == move and self.count >= 2)

    def register(self, move):
        if self.last_move == move:
            self.count += 1
        else:
            self.last_move = move
            self.count     = 1

    def available_moves(self):
        return [m for m in MOVES if self.can_use(m)]

# ═══════════════════════════════════════════════════════
#  CPU AI
# ═══════════════════════════════════════════════════════
class CpuAI:
    def __init__(self, difficulty, type_calc):
        self.difficulty = difficulty
        self.tc         = type_calc

    def choose_move(self, cpu, player, cooldown, player_move=None):
        """Returns (move, sp_type_index)."""
        available = cooldown.available_moves()
        if not available:
            available = MOVES[:]

        if self.difficulty == "easy":
            move   = random.choice(available)
            sp_idx = random.randint(0, len(cpu.types) - 1)
            Log.info(f"[CPU EASY] random pick: {move}  (available: {available})")
            return move, sp_idx

        if self.difficulty == "normal":
            return self._best_move(cpu, player, available, None)

        # hard: knows player move
        return self._best_move(cpu, player, available, player_move)

    def _score(self, move, cpu, player, sp_idx, counter_move=None):
        cp_hp = cpu.hp
        pl_hp = player.hp
        detail = ""  # human-readable explanation of what this move does

        if move == "attack":
            pl_hp -= cpu.attack
            detail = f"deals {cpu.attack} dmg to {player.name}"

        elif move == "defense":
            cp_hp += cpu.defense
            detail = f"heals self +{cpu.defense} HP"

        elif move == "special_attack":
            t    = cpu.types[sp_idx] if sp_idx < len(cpu.types) else cpu.types[0]
            mult = self.tc.get_multiplier(t, player.types)
            dmg  = cpu.sp_attack * mult
            pl_hp -= dmg
            detail = f"{t} SP.ATK deals {dmg:.1f} dmg to {player.name} (x{mult:.1f})"

        elif move == "special_defense":
            t    = cpu.types[sp_idx] if sp_idx < len(cpu.types) else cpu.types[0]
            mult = self.tc.get_multiplier(t, player.types)
            heal = cpu.sp_defense * mult
            cp_hp += heal
            detail = f"{t} SP.DEF heals self +{heal:.1f} HP (x{mult:.1f})"

        bonus = 0
        if counter_move:
            if counter_move in ("attack", "special_attack") and move in ("defense", "special_defense"):
                bonus += 15
                detail += f"  [counter bonus +15]"
            if counter_move in ("defense", "special_defense") and move in ("attack", "special_attack"):
                bonus += 15
                detail += f"  [counter bonus +15]"

        dmg_score  = player.hp - max(0, pl_hp)
        heal_score = (cp_hp - cpu.hp) * 0.5
        total      = dmg_score + heal_score + bonus
        return total, detail, dmg_score, heal_score, bonus

    def _best_move(self, cpu, player, available, counter_move):
        best_move = available[0]
        best_sp   = 0
        best_val  = -9999

        Log.section(f"CPU ({cpu.name}) thinking...  HP:{cpu.hp}/{cpu.max_hp}  vs  {player.name} HP:{player.hp}/{player.max_hp}")
        if counter_move:
            Log.info(f"[HARD MODE] CPU knows player chose: {counter_move}")
        Log.info(f"Available moves: {available}")
        Log.info(f"{'MOVE':<22} {'TYPE':<10} {'DMG score':>10} {'HEAL score':>11} {'BONUS':>6} {'TOTAL':>7}")
        Log.info("-" * 72)

        for move in available:
            for sp_idx in range(len(cpu.types)):
                total, detail, dmg_sc, heal_sc, bonus = self._score(move, cpu, player, sp_idx, counter_move)
                t_label = cpu.types[sp_idx] if move in ("special_attack","special_defense") and sp_idx < len(cpu.types) else "-"
                marker  = " ◄ BEST" if total > best_val else ""
                Log.info(f"  {move:<20} {t_label:<10} {dmg_sc:>10.1f} {heal_sc:>11.1f} {bonus:>6} {total:>7.1f}{marker}")
                if total > best_val:
                    best_val  = total
                    best_move = move
                    best_sp   = sp_idx

        t_chosen = cpu.types[best_sp] if best_move in ("special_attack","special_defense") and best_sp < len(cpu.types) else ""
        Log.info(f"  → CPU picks: {best_move}  {t_chosen}  (score {best_val:.1f})")
        return best_move, best_sp

# ═══════════════════════════════════════════════════════
#  BATTLE CLASS
# ═══════════════════════════════════════════════════════
class Battle:
    """
    Manages one battle between player and cpu.
    After each resolve_turn(), check is_over() to know if battle ended.
    winner() returns the winning Pokemon object.
    """
    def __init__(self, player_poke, cpu_poke, type_calc):
        self.player  = player_poke
        self.cpu     = cpu_poke
        self.tc      = type_calc
        self.p_cool  = CooldownTracker()
        self.c_cool  = CooldownTracker()
        self._over   = False
        self._winner = None
        self.turn    = 1   # turn counter: turn 1 is sequential, turn 2+ heals first

    def is_over(self):
        return self._over

    def winner(self):
        return self._winner

    def resolve_turn(self, p_move, p_sp_idx, c_move, c_sp_idx):
        """
        Apply one full turn. Returns list of (msg, tag) messages.
        Marks is_over() = True when a pokemon faints.

        Turn 1: speed-based order, sequential (first mover can KO before second acts).
        Turn 2+: healing/defense moves are applied FIRST for both pokemon simultaneously,
                 then damage is applied — so you cannot be KO'd before your heal lands.
        """
        if self._over:
            return []

        messages = []
        self.p_cool.register(p_move)
        self.c_cool.register(c_move)

        if self.turn == 1:
            # ── TURN 1: sequential, speed decides order ──────────────────
            Log.info(f"[TURN 1 — sequential, speed order]")
            player_first = self.player.speed >= self.cpu.speed
            if player_first:
                msgs = self._apply_move(self.player, p_move, p_sp_idx, self.cpu)
                messages.extend(msgs)
                Log.hp(self.cpu.name, self.cpu.hp, self.cpu.max_hp)
                if self.cpu.is_alive():
                    msgs = self._apply_move(self.cpu, c_move, c_sp_idx, self.player)
                    messages.extend(msgs)
                    Log.hp(self.player.name, self.player.hp, self.player.max_hp)
            else:
                msgs = self._apply_move(self.cpu, c_move, c_sp_idx, self.player)
                messages.extend(msgs)
                Log.hp(self.player.name, self.player.hp, self.player.max_hp)
                if self.player.is_alive():
                    msgs = self._apply_move(self.player, p_move, p_sp_idx, self.cpu)
                    messages.extend(msgs)
                    Log.hp(self.cpu.name, self.cpu.hp, self.cpu.max_hp)

        else:
            # ── TURN 2+: healing first, then damage simultaneously ───────
            Log.info(f"[TURN {self.turn} — heal first, then damage]")

            # Phase 1: apply healing/defense moves for both (no damage yet)
            p_heals = p_move in ("defense", "special_defense")
            c_heals = c_move in ("defense", "special_defense")

            if p_heals:
                msgs = self._apply_move(self.player, p_move, p_sp_idx, self.cpu)
                messages.extend(msgs)
                Log.info(f"  [HEAL PHASE] {self.player.name} HP after heal: {self.player.hp}")
            if c_heals:
                msgs = self._apply_move(self.cpu, c_move, c_sp_idx, self.player)
                messages.extend(msgs)
                Log.info(f"  [HEAL PHASE] {self.cpu.name} HP after heal: {self.cpu.hp}")

            # Phase 2: apply damage moves for both simultaneously
            p_damages = not p_heals
            c_damages = not c_heals

            if p_damages:
                msgs = self._apply_move(self.player, p_move, p_sp_idx, self.cpu)
                messages.extend(msgs)
            if c_damages:
                msgs = self._apply_move(self.cpu, c_move, c_sp_idx, self.player)
                messages.extend(msgs)

            if p_damages or c_damages:
                Log.hp(self.player.name, self.player.hp, self.player.max_hp)
                Log.hp(self.cpu.name,    self.cpu.hp,    self.cpu.max_hp)

        self.turn += 1

        # Clamp HP to minimum 0 (overheal above max is allowed)
        self.player.hp = max(0, self.player.hp)
        self.cpu.hp    = max(0, self.cpu.hp)

        # ── Check faint — this ENDS the battle ──
        if not self.cpu.is_alive() and not self.player.is_alive():
            # Both fainted simultaneously → player loses (tie goes to CPU)
            messages.append((f"Both fainted! {self.cpu.name} wins by tie-break!", None))
            Log.faint(self.player.name)
            Log.faint(self.cpu.name)
            self._over   = True
            self._winner = self.cpu
            Log.winner(self.cpu.name)

        elif not self.cpu.is_alive():
            messages.append((f"{self.cpu.name} fainted!", None))
            Log.faint(self.cpu.name)
            self._over   = True
            self._winner = self.player
            Log.winner(self.player.name)

        elif not self.player.is_alive():
            messages.append((f"{self.player.name} fainted!", None))
            Log.faint(self.player.name)
            self._over   = True
            self._winner = self.cpu
            Log.winner(self.cpu.name)

        return messages

    def _apply_move(self, attacker, move, sp_idx, defender):
        msgs = []
        name = attacker.name

        if move == "attack":
            dmg = attacker.attack
            defender.hp -= dmg
            msg = f"{name} used Attack! ({defender.name} -{dmg} HP)"
            msgs.append((msg, None))
            Log.battle(msg)

        elif move == "defense":
            gain = attacker.defense
            attacker.hp += gain
            msg  = f"{name} used Defense! (+{gain} HP)"
            msgs.append((msg, None))
            Log.battle(msg)

        elif move == "special_attack":
            t    = attacker.types[sp_idx] if sp_idx < len(attacker.types) else attacker.types[0]
            mult = self.tc.get_multiplier(t, defender.types)
            dmg  = int(attacker.sp_attack * mult)
            defender.hp -= dmg
            tag  = self._eff_tag(mult)
            msg  = f"{name} used {t} Special Attack! ({defender.name} -{dmg} HP  x{mult:.1f})"
            msgs.append((msg, tag))
            Log.battle(msg)
            if tag:
                eff_msg = self._eff_msg(tag)
                msgs.append((eff_msg, tag))
                Log.effect(eff_msg)

        elif move == "special_defense":
            t    = attacker.types[sp_idx] if sp_idx < len(attacker.types) else attacker.types[0]
            mult = self.tc.get_multiplier(t, defender.types)
            gain = int(attacker.sp_defense * mult)
            attacker.hp += gain
            msg  = f"{name} used {t} Special Defense! (+{gain} HP)"
            msgs.append((msg, None))
            Log.battle(msg)

        return msgs

    @staticmethod
    def _eff_tag(mult):
        if mult == 0:  return "no_effect"
        if mult < 1:   return "not_very"
        if mult > 1:   return "super"
        return None

    @staticmethod
    def _eff_msg(tag):
        return {"super":     "It's super effective!",
                "not_very":  "It's not very effective...",
                "no_effect": "It had no effect!"}.get(tag, "")

# ═══════════════════════════════════════════════════════
#  TOURNAMENT CLASS
# ═══════════════════════════════════════════════════════
class Tournament:
    def __init__(self, fighters):
        self.player    = fighters[0]
        self.bracket   = fighters[:]
        random.shuffle(self.bracket)
        self.round_num = 1

    def get_matches(self):
        b = self.bracket
        return [(b[i], b[i + 1]) for i in range(0, len(b), 2)]

    def advance(self, winners):
        self.bracket = winners
        self.round_num += 1

    def size(self):
        return len(self.bracket)

    def round_name(self):
        return {16: "ROUND OF 16", 8: "QUARTER FINALS",
                4:  "SEMI FINALS", 2: "FINAL"
                }.get(self.size(), f"ROUND {self.round_num}")

# ═══════════════════════════════════════════════════════
#  SPRITE LOADER
# ═══════════════════════════════════════════════════════
def load_sprite(name, flip=False):
    path = os.path.join(BASE_DIR, "pokemon_images", f"{name}.png")
    if os.path.exists(path):
        surf = pygame.image.load(path).convert_alpha()
    else:
        surf = pygame.Surface((68, 56), pygame.SRCALPHA)
        surf.fill((160, 160, 160, 180))
        # Draw a small "?" for unknown
        try:
            f = pygame.font.SysFont("Arial", 24, bold=True)
            lbl = f.render("?", True, (50, 50, 50))
            surf.blit(lbl, (24, 14))
        except:
            pass
    if flip:
        surf = pygame.transform.flip(surf, True, False)
    return surf

def get_font(size):
    for name in ["Courier New", "Courier", "monospace"]:
        try:
            return pygame.font.SysFont(name, size, bold=True)
        except:
            pass
    return pygame.font.Font(None, size)

# ═══════════════════════════════════════════════════════
#  GAME
# ═══════════════════════════════════════════════════════
class Game:
    """
    States:
      title → difficulty → pick_pool → tournament ↔ battle → game_over
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Pokemon Tournament")
        self.clock  = pygame.time.Clock()

        self.font_sm = get_font(15)
        self.font_md = get_font(20)
        self.font_lg = get_font(28)
        self.font_xl = get_font(38)

        self.pokedex   = load_pokedex()
        self.type_calc = TypeCalculator(load_types())

        self.state           = "title"
        self.difficulty      = "easy"
        self.pool            = []
        self.player_sel      = 0
        self.player_poke     = None
        self.tournament      = None
        self.cpu_ai          = None

        # Round tracking
        self.current_matches = []   # list of (p1, p2)
        self.match_index     = 0    # which match we're currently on
        self.match_winners   = {}   # {match_index: winner_pokemon}
        self.round_results   = []   # strings for display

        # Battle
        self.current_battle  = None
        self.battle_messages = []   # [(text, tag), ...]
        self.msg_index       = 0
        # battle_phase values:
        #   "messages"  — player reads dialogue, presses SPACE to advance
        #   "menu"      — player picks a move
        #   "sp_choice" — player picks special type
        self.battle_phase    = "messages"
        self.selected_menu   = 0
        self.player_move     = None
        self.player_sp_idx   = 0

        # Animations
        self.shake_player    = 0
        self.shake_cpu       = 0
        self.hp_anim_p       = 0.0
        self.hp_anim_c       = 0.0

        self.tournament_winner = None

    # ─────────────────────────────────────────
    #  MAIN LOOP
    # ─────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self._on_key(event.key)

    def _on_key(self, key):
        s = self.state

        if s == "title":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = "difficulty"

        elif s == "difficulty":
            if key == pygame.K_1:
                self.difficulty = "easy";   self._build_pool()
            elif key == pygame.K_2:
                self.difficulty = "normal"; self._build_pool()
            elif key == pygame.K_3:
                self.difficulty = "hard";   self._build_pool()

        elif s == "pick_pool":
            if key == pygame.K_UP:
                self.player_sel = max(0, self.player_sel - 1)
            elif key == pygame.K_DOWN:
                self.player_sel = min(len(self.pool) - 1, self.player_sel + 1)
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm_pick()

        elif s == "tournament":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self._begin_round()

        elif s == "battle":
            self._battle_key(key)

        elif s == "game_over":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.__init__()

    # ─────────────────────────────────────────
    #  SETUP
    # ─────────────────────────────────────────
    def _build_pool(self):
        sample    = random.sample(self.pokedex, min(50, len(self.pokedex)))
        self.pool = [Pokemon(d) for d in sample]
        self.player_sel = 0
        self.state = "pick_pool"

        Log.section("POKEMON POOL  (50 available)")
        for i, p in enumerate(self.pool):
            Log.info(f"{i+1:2}. {p.name:<16} {'/'.join(p.types):<20} "
                     f"HP:{p.max_hp}  ATK:{p.attack}  SPD:{p.speed}")

    def _confirm_pick(self):
        self.player_poke = self.pool[self.player_sel]
        self.player_poke.heal()

        Log.section(f"PLAYER CHOSE: {self.player_poke.name}")
        Log.info(f"Types:  {', '.join(self.player_poke.types)}")
        Log.info(f"HP:{self.player_poke.max_hp}  ATK:{self.player_poke.attack}  "
                 f"DEF:{self.player_poke.defense}  SP.ATK:{self.player_poke.sp_attack}  "
                 f"SP.DEF:{self.player_poke.sp_defense}  SPD:{self.player_poke.speed}")

        others = [p for i, p in enumerate(self.pool) if i != self.player_sel]

        if self.difficulty == "normal":
            pt = (self.player_poke.max_hp + self.player_poke.attack + self.player_poke.defense +
                  self.player_poke.sp_attack + self.player_poke.sp_defense + self.player_poke.speed)
            others.sort(key=lambda p: abs(
                p.max_hp + p.attack + p.defense + p.sp_attack + p.sp_defense + p.speed - pt))
            cpu_pool = others[:15]
        else:
            cpu_pool = random.sample(others, min(15, len(others)))

        for p in cpu_pool:
            p.heal()

        fighters = [self.player_poke] + cpu_pool
        self.tournament = Tournament(fighters)
        self.cpu_ai     = CpuAI(self.difficulty, self.type_calc)

        Log.section(f"TOURNAMENT BRACKET  ({self.difficulty.upper()} mode)")
        for i, (p1, p2) in enumerate(self.tournament.get_matches()):
            tag = "  ← YOU" if (p1 == self.player_poke or p2 == self.player_poke) else ""
            Log.info(f"  Match {i+1}: {p1.name} vs {p2.name}{tag}")

        self.state = "tournament"

    # ─────────────────────────────────────────
    #  TOURNAMENT FLOW
    # ─────────────────────────────────────────
    def _begin_round(self):
        self.current_matches = self.tournament.get_matches()
        self.match_index     = 0
        self.match_winners   = {}
        self.round_results   = []
        Log.section(f"{self.tournament.round_name()}  ({self.tournament.size()} pokemon)")
        self._process_next_match()

    def _process_next_match(self):
        """
        Walk forward from match_index.
        Auto-resolve CPU vs CPU matches, stop for player match.
        When all matches done → advance tournament.
        """
        while self.match_index < len(self.current_matches):
            p1, p2 = self.current_matches[self.match_index]

            if p1 == self.player_poke or p2 == self.player_poke:
                # Interactive battle
                cpu = p2 if p1 == self.player_poke else p1
                self.player_poke.heal()
                cpu.heal()
                Log.section(f"YOUR BATTLE: {self.player_poke.name} vs {cpu.name}")
                self._start_battle(self.player_poke, cpu)
                return  # ← pause here; resumes via _on_battle_over()

            else:
                # Auto-resolve CPU vs CPU
                winner = self._auto_battle(p1, p2)
                self.match_winners[self.match_index] = winner
                result = f"{p1.name} vs {p2.name}  →  {winner.name} wins"
                self.round_results.append(result)
                Log.info(f"[AUTO] {result}")
                self.match_index += 1

        # All matches done — collect winners in original bracket order
        winners = [self.match_winners[i] for i in range(len(self.current_matches))]
        self.tournament.advance(winners)

        Log.section(f"ROUND OVER  —  {len(winners)} advance")
        for w in winners:
            Log.info(f"  ✔  {w.name}")

        if len(winners) == 1:
            self.tournament_winner = winners[0]
            self.state = "game_over"
            if self.tournament_winner == self.player_poke:
                Log.section("🎉  YOU ARE THE CHAMPION!")
            else:
                Log.section(f"TOURNAMENT WINNER: {self.tournament_winner.name}")
        else:
            self.state = "tournament"

    def _auto_battle(self, p1, p2):
        """Simulate a CPU vs CPU battle without graphics. Return winner."""
        p1.heal(); p2.heal()
        cd1 = CooldownTracker()
        cd2 = CooldownTracker()
        for _ in range(300):
            av1 = cd1.available_moves()
            av2 = cd2.available_moves()
            m1  = random.choice(av1) if av1 else random.choice(MOVES)
            m2  = random.choice(av2) if av2 else random.choice(MOVES)
            sp1 = random.randint(0, len(p1.types) - 1)
            sp2 = random.randint(0, len(p2.types) - 1)
            cd1.register(m1)
            cd2.register(m2)
            self._apply_simple(p1, m1, sp1, p2)
            self._apply_simple(p2, m2, sp2, p1)
            p1.hp = max(0, min(p1.hp, p1.max_hp))
            p2.hp = max(0, min(p2.hp, p2.max_hp))
            if not p1.is_alive(): return p2
            if not p2.is_alive(): return p1
        return p1 if p1.speed >= p2.speed else p2

    def _apply_simple(self, attacker, move, sp_idx, defender):
        """Minimal move application (no messages) for auto battles."""
        if move == "attack":
            defender.hp -= attacker.attack
        elif move == "defense":
            attacker.hp += attacker.defense
        elif move == "special_attack":
            t    = attacker.types[sp_idx] if sp_idx < len(attacker.types) else attacker.types[0]
            mult = self.type_calc.get_multiplier(t, defender.types)
            defender.hp -= int(attacker.sp_attack * mult)
        elif move == "special_defense":
            t    = attacker.types[sp_idx] if sp_idx < len(attacker.types) else attacker.types[0]
            mult = self.type_calc.get_multiplier(t, defender.types)
            attacker.hp += int(attacker.sp_defense * mult)

    # ─────────────────────────────────────────
    #  BATTLE SETUP
    # ─────────────────────────────────────────
    def _start_battle(self, player_poke, cpu_poke):
        self.current_battle = Battle(player_poke, cpu_poke, self.type_calc)
        self.hp_anim_p  = float(player_poke.hp)
        self.hp_anim_c  = float(cpu_poke.hp)
        self.shake_player = 0
        self.shake_cpu    = 0

        Log.hp(player_poke.name, player_poke.hp, player_poke.max_hp)
        Log.hp(cpu_poke.name,    cpu_poke.hp,    cpu_poke.max_hp)
        first = player_poke.name if player_poke.speed >= cpu_poke.speed else cpu_poke.name
        Log.info(f"Speed: {player_poke.name}={player_poke.speed}  "
                 f"{cpu_poke.name}={cpu_poke.speed}  →  {first} goes first")

        self.battle_messages = [
            (f"A battle begins!", None),
            (f"{cpu_poke.name} appeared!", None),
        ]
        self.msg_index    = 0
        self.battle_phase = "messages"
        self.player_move  = None
        self.selected_menu= 0
        self.state        = "battle"

    # ─────────────────────────────────────────
    #  BATTLE KEY HANDLER
    # ─────────────────────────────────────────
    def _battle_key(self, key):
        phase = self.battle_phase

        # ── Reading dialogue ──────────────────
        if phase == "messages":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self.msg_index += 1
                if self.msg_index >= len(self.battle_messages):
                    # All messages read
                    if self.current_battle.is_over():
                        # Battle ended — go back to tournament flow
                        self._on_battle_over()
                    else:
                        # Show move menu
                        self.battle_phase  = "menu"
                        self.selected_menu = 0
            return

        # ── Special type selection ────────────
        if phase == "sp_choice":
            types = self.current_battle.player.types
            if key == pygame.K_1 and len(types) >= 1:
                self.player_sp_idx = 0
                self._execute_turn()
            elif key == pygame.K_2 and len(types) >= 2:
                self.player_sp_idx = 1
                self._execute_turn()
            return

        # ── Move menu ─────────────────────────
        if phase == "menu":
            if key == pygame.K_UP:
                self.selected_menu = (self.selected_menu - 1) % 4
            elif key == pygame.K_DOWN:
                self.selected_menu = (self.selected_menu + 1) % 4
            elif key in (pygame.K_1, pygame.K_KP1):
                self.selected_menu = 0
            elif key in (pygame.K_2, pygame.K_KP2):
                self.selected_menu = 1
            elif key in (pygame.K_3, pygame.K_KP3):
                self.selected_menu = 2
            elif key in (pygame.K_4, pygame.K_KP4):
                self.selected_menu = 3

            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                move = MOVES[self.selected_menu]

                # Check cooldown
                if not self.current_battle.p_cool.can_use(move):
                    warn = f"{move.replace('_',' ').title()} is on cooldown! Choose another."
                    self.battle_messages = [(warn, None)]
                    self.msg_index    = 0
                    self.battle_phase = "messages"
                    Log.info(f"[PLAYER] cooldown warning: {move}")
                    return

                self.player_move = move
                Log.info(f"[PLAYER] chose: {move}")

                # Multi-type special → ask which type
                if move in ("special_attack", "special_defense") and \
                   len(self.current_battle.player.types) > 1:
                    self.battle_phase = "sp_choice"
                else:
                    self.player_sp_idx = 0
                    self._execute_turn()

    def _execute_turn(self):
        """Ask CPU for its move and resolve the full turn."""
        battle = self.current_battle

        # Hard mode: CPU already knows player's move
        pm = self.player_move if self.difficulty == "hard" else None
        c_move, c_sp = self.cpu_ai.choose_move(
            battle.cpu, battle.player, battle.c_cool, pm)
        Log.info(f"[CPU]    chose: {c_move}")

        msgs = battle.resolve_turn(self.player_move, self.player_sp_idx, c_move, c_sp)

        self.shake_player    = 8
        self.shake_cpu       = 8
        self.battle_messages = msgs
        self.msg_index       = 0
        self.battle_phase    = "messages"
        # Note: we do NOT change state here.
        # The battle_key handler will detect is_over() after messages are read.

    def _on_battle_over(self):
        """Called when the player has read all end-of-battle messages."""
        battle = self.current_battle
        winner = battle.winner()

        if winner == battle.player:
            # Player won this match
            Log.info(f"[TOURNAMENT] {self.player_poke.name} advances")
            self.match_winners[self.match_index] = self.player_poke
            self.match_index += 1
            self._process_next_match()   # may start another battle or end round
        else:
            # Player lost
            Log.section(f"ELIMINATED — {battle.cpu.name} defeated {self.player_poke.name}")
            self.tournament_winner = battle.cpu
            self.state = "game_over"

    # ─────────────────────────────────────────
    #  UPDATE
    # ─────────────────────────────────────────
    def _update(self, dt):
        if self.shake_player > 0: self.shake_player -= 1
        if self.shake_cpu    > 0: self.shake_cpu    -= 1

        if self.current_battle:
            tp = float(self.current_battle.player.hp)
            tc = float(self.current_battle.cpu.hp)
            self.hp_anim_p += (tp - self.hp_anim_p) * 0.12
            self.hp_anim_c += (tc - self.hp_anim_c) * 0.12

    # ─────────────────────────────────────────
    #  DRAW — dispatch
    # ─────────────────────────────────────────
    def _draw(self):
        dispatch = {
            "title":      self._draw_title,
            "difficulty": self._draw_difficulty,
            "pick_pool":  self._draw_pick_pool,
            "tournament": self._draw_tournament,
            "battle":     self._draw_battle,
            "game_over":  self._draw_game_over,
        }
        dispatch.get(self.state, lambda: None)()

    # ── TITLE ─────────────────────────────────
    def _draw_title(self):
        self.screen.fill(DBLUE)
        self._tc("POKEMON TOURNAMENT",   SCREEN_H // 3,    self.font_xl, YELLOW)
        self._tc("Press ENTER to start", SCREEN_H // 2,    self.font_md, WHITE)
        self._tc("A retro tournament game", SCREEN_H*2//3, self.font_sm, LGRAY)

    # ── DIFFICULTY ────────────────────────────
    def _draw_difficulty(self):
        self.screen.fill(DGRAY)
        self._tc("CHOOSE DIFFICULTY", 70, self.font_lg, YELLOW)
        rows = [("1  EASY",   "CPU plays randomly"),
                ("2  NORMAL", "CPU plays optimally"),
                ("3  HARD",   "CPU knows your move in advance!")]
        y = 170
        for title, desc in rows:
            self._tc(title, y,      self.font_md, WHITE)
            self._tc(desc,  y + 26, self.font_sm, LGRAY)
            y += 85

    # ── PICK POOL ─────────────────────────────
    def _draw_pick_pool(self):
        self.screen.fill(CREAM)
        pygame.draw.rect(self.screen, DBLUE, (0, 0, SCREEN_W, 38))
        self._tc("CHOOSE YOUR POKEMON  —  UP/DOWN + ENTER", 8, self.font_sm, WHITE)

        item_h  = 26
        visible = (SCREEN_H - 80) // item_h
        start   = max(0, self.player_sel - visible // 2)
        end     = min(len(self.pool), start + visible)

        for i in range(start, end):
            p  = self.pool[i]
            ry = 44 + (i - start) * item_h
            bg = LBLUE if i == self.player_sel else CREAM
            fg = BLUE  if i == self.player_sel else DGRAY
            pygame.draw.rect(self.screen, bg, (8, ry, SCREEN_W - 16, item_h - 1))
            txt = f"{i+1:2}. {p.name:<15} {'/'.join(p.types):<18}  HP:{p.max_hp}  ATK:{p.attack}"
            self._t(txt, 14, ry + 4, self.font_sm, fg)

        p = self.pool[self.player_sel]
        pygame.draw.rect(self.screen, DBLUE, (0, SCREEN_H - 46, SCREEN_W, 46))
        info = f"{p.name}  |  {', '.join(p.types)}  |  Speed {p.speed}"
        self._tc(info, SCREEN_H - 34, self.font_sm, YELLOW)

    # ── TOURNAMENT ────────────────────────────
    def _draw_tournament(self):
        self.screen.fill(DGRAY)
        pygame.draw.rect(self.screen, DBLUE, (0, 0, SCREEN_W, 38))
        self._tc(f"TOURNAMENT  —  {self.tournament.round_name()}", 8, self.font_md, YELLOW)

        matches = self.tournament.get_matches()
        y = 50
        for i, (p1, p2) in enumerate(matches):
            you = (p1 == self.player_poke or p2 == self.player_poke)
            col = YELLOW if you else WHITE
            tag = "  ★ YOUR MATCH" if you else ""
            self._t(f"  {p1.name:<16} vs  {p2.name:<16}{tag}", 10, y, self.font_sm, col)
            y += 22
            if y > SCREEN_H - 80:
                break

        self._tc("Press ENTER to start your battle!", SCREEN_H - 46, self.font_md, LBLUE)

        if self.round_results:
            bx = SCREEN_W - 235
            bh = min(280, len(self.round_results) * 18 + 28)
            pygame.draw.rect(self.screen, BLACK, (bx - 4, 46, 238, bh))
            self._t("Other results:", bx, 50, self.font_sm, LGRAY)
            ry = 70
            for r in self.round_results[-12:]:
                self._t(r[:32], bx, ry, self.font_sm, LGRAY)
                ry += 18

    # ── BATTLE ────────────────────────────────
    def _draw_battle(self):
        if not self.current_battle:
            return
        player = self.current_battle.player
        cpu    = self.current_battle.cpu

        # Background
        self.screen.fill((104, 168, 88))
        pygame.draw.line(self.screen, DGREEN, (0, 275), (SCREEN_W, 275), 3)

        # Enemy info box — top left
        pygame.draw.rect(self.screen, WHITE,  (8,  8, 215, 60), border_radius=4)
        pygame.draw.rect(self.screen, BLACK,  (8,  8, 215, 60), 2, border_radius=4)
        self._t(cpu.name,          14, 12, self.font_md, BLACK)
        self._t(f"Lv{cpu.level}", 165, 12, self.font_sm, BLACK)
        self._draw_hp_bar(14, 36, 195, 13, cpu, self.hp_anim_c)

        # Enemy sprite — top right
        ex, ey = SCREEN_W - 175, 35
        if self.shake_cpu > 0:
            ex += random.randint(-4, 4)
        spr = load_sprite(cpu.name)
        spr = pygame.transform.scale(spr, (100, 84))
        self.screen.blit(spr, (ex, ey))

        # Player info box — bottom right
        pygame.draw.rect(self.screen, WHITE,  (SCREEN_W - 238, 188, 228, 74), border_radius=4)
        pygame.draw.rect(self.screen, BLACK,  (SCREEN_W - 238, 188, 228, 74), 2, border_radius=4)
        self._t(player.name,           SCREEN_W - 232, 192, self.font_md, BLACK)
        self._t(f"Lv{player.level}",   SCREEN_W - 78,  192, self.font_sm, BLACK)
        self._draw_hp_bar(SCREEN_W - 232, 218, 204, 13, player, self.hp_anim_p)
        self._t(f"HP: {max(0,int(self.hp_anim_p))}/{player.max_hp}",
                SCREEN_W - 232, 236, self.font_sm, BLACK)

        # Player sprite — bottom left (flipped)
        px, py = 55, 148
        if self.shake_player > 0:
            px += random.randint(-4, 4)
        spr_p = load_sprite(player.name, flip=True)
        spr_p = pygame.transform.scale(spr_p, (112, 95))
        self.screen.blit(spr_p, (px, py))

        # Dialogue / menu box at bottom
        pygame.draw.rect(self.screen, WHITE, (0, 283, SCREEN_W, SCREEN_H - 283))
        pygame.draw.rect(self.screen, BLACK, (0, 283, SCREEN_W, SCREEN_H - 283), 3)

        phase = self.battle_phase
        if phase == "messages":
            self._draw_messages()
        elif phase == "sp_choice":
            self._draw_sp_choice()
        elif phase == "menu":
            self._draw_move_menu()

    def _draw_hp_bar(self, x, y, w, h, poke, anim):
        pct = max(0.0, anim / max(1, poke.max_hp))
        overhealed = pct > 1.0
        if overhealed:
            col = (0, 220, 220)   # cyan = overhealed
        elif pct > 0.5:
            col = GREEN
        elif pct > 0.25:
            col = YELLOW
        else:
            col = RED
        fill_w = min(int(w * pct), w)   # visual bar capped at full width
        pygame.draw.rect(self.screen, LGRAY, (x, y, w, h))
        pygame.draw.rect(self.screen, col,   (x, y, fill_w, h))
        if overhealed:
            pygame.draw.rect(self.screen, WHITE, (x + w - 4, y, 4, h))
        pygame.draw.rect(self.screen, BLACK, (x, y, w, h), 1)

    def _draw_messages(self):
        if self.msg_index < len(self.battle_messages):
            text, tag = self.battle_messages[self.msg_index]
            col = RED if tag == "super" else (BLUE if tag == "not_very" else BLACK)
            self._wrap(text, 16, 300, SCREEN_W - 32, self.font_md, col)
        self._t("SPACE to continue", SCREEN_W - 175, SCREEN_H - 22, self.font_sm, LGRAY)

    def _draw_move_menu(self):
        self._t("What will you do?", 16, 292, self.font_md, BLACK)
        labels = [("Attack",          "attack"),
                  ("Defense",         "defense"),
                  ("Special Attack",  "special_attack"),
                  ("Special Defense", "special_defense")]
        col_x = [16, 330]
        row_y = [322, 370]
        for idx, (label, move) in enumerate(labels):
            cx     = col_x[idx % 2]
            cy     = row_y[idx // 2]
            locked = not self.current_battle.p_cool.can_use(move)
            sel    = (idx == self.selected_menu)
            bg = BLUE  if sel    else (LGRAY if locked else WHITE)
            fg = WHITE if sel    else (DGRAY if locked else BLACK)
            pygame.draw.rect(self.screen, bg,    (cx, cy, 290, 36), border_radius=4)
            pygame.draw.rect(self.screen, BLACK, (cx, cy, 290, 36), 2, border_radius=4)
            self._t(f"{idx+1}. {label}", cx + 8, cy + 8, self.font_md, fg)
            if locked:
                self._t("COOLDOWN", cx + 195, cy + 10, self.font_sm, RED)
        self._t("UP/DOWN or 1-4   ENTER=confirm", 16, SCREEN_H - 22, self.font_sm, DGRAY)

    def _draw_sp_choice(self):
        p = self.current_battle.player
        self._t("Choose type for special move:", 16, 296, self.font_md, BLACK)
        for i, t in enumerate(p.types):
            cx = 16 + i * 310
            pygame.draw.rect(self.screen, BLUE,  (cx, 335, 285, 46), border_radius=4)
            pygame.draw.rect(self.screen, BLACK, (cx, 335, 285, 46), 2, border_radius=4)
            self._t(f"{i+1}.  {t}", cx + 10, 350, self.font_md, WHITE)

    # ── GAME OVER ─────────────────────────────
    def _draw_game_over(self):
        self.screen.fill(DBLUE)
        if self.tournament_winner == self.player_poke:
            self._tc("YOU ARE THE CHAMPION!", SCREEN_H // 3,    self.font_lg, YELLOW)
            self._tc(f"{self.player_poke.name} wins the tournament!", SCREEN_H // 2, self.font_md, WHITE)
        else:
            self._tc("YOU WERE ELIMINATED!",  SCREEN_H // 3, self.font_lg, RED)
            if self.tournament_winner:
                self._tc(f"{self.tournament_winner.name} wins the tournament!",
                         SCREEN_H // 2, self.font_md, WHITE)
        self._tc("Press ENTER to play again", SCREEN_H * 2 // 3, self.font_md, LGRAY)

    # ─────────────────────────────────────────
    #  TEXT HELPERS
    # ─────────────────────────────────────────
    def _t(self, text, x, y, font, color):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def _tc(self, text, y, font, color):
        surf = font.render(str(text), True, color)
        self.screen.blit(surf, ((SCREEN_W - surf.get_width()) // 2, y))

    def _wrap(self, text, x, y, max_w, font, color):
        words = text.split()
        line  = ""
        dy    = 0
        for w in words:
            test = line + w + " "
            if font.size(test)[0] > max_w and line:
                self._t(line.strip(), x, y + dy, font, color)
                dy  += font.get_height() + 3
                line = w + " "
            else:
                line = test
        if line:
            self._t(line.strip(), x, y + dy, font, color)


# ═══════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    game = Game()
    game.run()