import pygame
import sys
import os
import random

# Ensure the directory containing this file is on sys.path
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from game.pokemon import Pokemon
from game.battle import Battle
from game.ai import CPU_AI
from game.tournament import Tournament
from game.ui import UI, AnimationManager, TYPE_COLORS
from game.assets import load_pokedex, load_sprite, select_tournament_pokemon, make_placeholder_sprite
from game import logger

# Screen
WIDTH, HEIGHT = 720, 480
FPS = 60

# Game states
STATE_DIFFICULTY = "difficulty"
STATE_POKEMON_SELECT = "pokemon_select"
STATE_BRACKET = "bracket"
STATE_BATTLE = "battle"
STATE_CPU_BATTLE = "cpu_battle"
STATE_VICTORY = "victory"
STATE_CHAMPION = "champion"


def make_pokemon_from_data(data):
    p = Pokemon(data)
    return p


def load_sprites_for_pokemon(pokemon_list):
    for p in pokemon_list:
        sprite = load_sprite(p.name)
        if sprite is None:
            logger.log(f"Sprite non trovato per {p.name}, uso placeholder", "ASSET")
            col = TYPE_COLORS.get(p.types[0], (150, 150, 150))
            sprite = make_placeholder_sprite(col)
        else:
            logger.log(f"Sprite caricato: {p.name}", "ASSET")
        p.sprite = sprite


class Game:
    def __init__(self):
        log_path = logger.init_logger()
        logger.log(f"Game starting up...")

        pygame.init()
        pygame.display.set_caption("Pokemon Tournament")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen, WIDTH, HEIGHT)
        self.state = STATE_DIFFICULTY
        self.difficulty_idx = 1  # default normal
        self.selected_pokemon_idx = 0

        # Load data
        try:
            self.pokedex = load_pokedex()
            logger.log(f"Pokedex loaded: {len(self.pokedex)} Pokemon available")
        except Exception as e:
            logger.log(f"ERROR loading pokedex: {e}", "ERROR")
            print(f"Error loading pokedex: {e}")
            print("Please make sure pokedex.json is available.")
            pygame.quit()
            sys.exit(1)

        self.tournament_pokemon_data = []
        self.tournament_pokemon = []
        self.player_pokemon = None
        self.tournament = None
        self.difficulty = "normal"

        # Battle state
        self.battle = None
        self.battle_text = []
        self.battle_phase = "choose"
        self.move_cursor = 0
        self.player_move = None
        self.anim = AnimationManager()
        self.battle_timer = 0
        self.pending_messages = []
        self.msg_display_timer = 0
        self.current_winner = None

        self.cpu_battle_msgs = []
        self.cpu_battle_timer = 0

        logger.log(f"Log file saved to: {log_path}")

    def reset_game(self):
        logger.log_section("GAME RESET - Returning to main menu")
        self.state = STATE_DIFFICULTY
        self.difficulty_idx = 1
        self.selected_pokemon_idx = 0
        self.tournament_pokemon = []
        self.player_pokemon = None
        self.tournament = None
        self.battle = None
        self.battle_text = []
        self.move_cursor = 0

    def setup_tournament(self):
        difficulties = ["easy", "normal", "hard"]
        self.difficulty = difficulties[self.difficulty_idx]
        logger.log_difficulty(self.difficulty)

        selected_data = select_tournament_pokemon(self.pokedex, 16)
        self.tournament_pokemon = [make_pokemon_from_data(d) for d in selected_data]
        load_sprites_for_pokemon(self.tournament_pokemon)
        logger.log_tournament_pokemon(self.tournament_pokemon)

    def start_tournament(self):
        self.player_pokemon = self.tournament_pokemon[self.selected_pokemon_idx]
        logger.log_player_pokemon(self.player_pokemon)
        self.tournament = Tournament(self.tournament_pokemon, self.player_pokemon, self.difficulty)
        logger.log_tournament_bracket(self.tournament)
        self.state = STATE_BRACKET

    def _get_round_name(self):
        return self.tournament.get_round_name() if self.tournament else ""

    def advance_tournament(self):
        t = self.tournament

        if t.is_finished():
            champ = t.get_champion()
            is_player = (champ == self.player_pokemon)
            logger.log_champion(champ.name, is_player)
            self.state = STATE_CHAMPION
            return

        match_idx, match = t.get_current_match()
        if match is None:
            self.state = STATE_CHAMPION
            return

        p1, p2 = match
        p1.reset_battle()
        p2.reset_battle()

        round_name = t.get_round_name()

        if t.is_player_in_match(match):
            enemy = p2 if p1 == self.player_pokemon else p1
            logger.log(f"[{round_name}] Player battle: {self.player_pokemon.name} vs {enemy.name}", "MATCH")
            cpu_ai = CPU_AI(self.difficulty)
            self.battle = Battle(self.player_pokemon, enemy, None, cpu_ai, round_name)
            self.battle_text = [f"A battle begins!", f"{self.player_pokemon.name} vs {enemy.name}!"]
            self.battle_phase = "choose"
            self.move_cursor = 0
            self.state = STATE_BATTLE
        else:
            logger.log(f"[{round_name}] CPU battle: {p1.name} vs {p2.name}", "MATCH")
            ai1 = CPU_AI(self.difficulty)
            ai2 = CPU_AI(self.difficulty)
            self.battle = Battle(p1, p2, ai1, ai2, round_name)
            self.cpu_battle_msgs = [f"CPU Battle: {p1.name} vs {p2.name}"]
            self.cpu_battle_timer = 0
            self.state = STATE_CPU_BATTLE

    def run_cpu_battle_step(self):
        if not self.battle.finished:
            msgs = self.battle.run_turn()
            self.cpu_battle_msgs.extend(msgs)
        else:
            winner = self.battle.winner
            loser = self.battle.pokemon2 if winner == self.battle.pokemon1 else self.battle.pokemon1
            logger.log_tournament_result(self.battle.round_name, winner, loser)
            self.tournament.record_result(winner)
            self.cpu_battle_msgs.append(f"{winner.name} wins!")
            self.state = STATE_BRACKET

    def handle_battle_input(self, event):
        if self.battle_phase == "choose":
            if event.key == pygame.K_UP:
                self.move_cursor = (self.move_cursor - 1) % 4
            elif event.key == pygame.K_DOWN:
                self.move_cursor = (self.move_cursor + 1) % 4
            elif event.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                self.player_move = self.move_cursor
                self.execute_battle_turn()

    def execute_battle_turn(self):
        battle = self.battle
        player = battle.pokemon1
        enemy  = battle.pokemon2

        enemy_move      = battle.ai2.choose_move(enemy, player)
        player_move_obj = player.moves[self.player_move]

        # Reset flag difesa per il nuovo turno
        battle._reset_turn_flags()

        logger.log_player_move(player_move_obj.name, player_move_obj.attack_type, player_move_obj.power)
        logger.log_cpu_move(enemy.name, enemy_move.name, enemy_move.attack_type, enemy_move.power)

        first_is_player = player.speed >= enemy.speed
        logger.log(f"  Ordine velocità: {player.name}({player.speed}) vs {enemy.name}({enemy.speed}) "
                   f"-> {'Giocatore' if first_is_player else 'CPU'} va prima", "SPEED")

        self.battle_text = []

        def do_move(attacker, move, defender, is_p1):
            msgs, dmg, mult = battle.apply_move(attacker, move, defender, is_p1)
            self.battle_text.extend(msgs)
            if dmg > 0:
                self.anim.add_shake("enemy" if is_p1 else "player")

        if first_is_player:
            do_move(player, player_move_obj, enemy, True)
            if enemy.is_alive():
                do_move(enemy, enemy_move, player, False)
        else:
            do_move(enemy, enemy_move, player, False)
            if player.is_alive():
                do_move(player, player_move_obj, enemy, True)

        battle.turn += 1

        if not player.is_alive():
            battle.finished = True
            battle.winner = enemy
        elif not enemy.is_alive():
            battle.finished = True
            battle.winner = player

        if battle.finished:
            self.battle_phase = "result"
            winner = battle.winner
            loser = enemy if winner == player else player
            logger.log_tournament_result(battle.round_name, winner, loser)
            logger.log_battle_end(winner.name, loser.name, battle.turn)
            self.tournament.record_result(winner)
            is_player_win = (winner == self.player_pokemon)
            logger.log(f"Player {'WON' if is_player_win else 'LOST'} the battle!", "PLAYER")
            self.current_winner = winner
            self.state = STATE_VICTORY
        else:
            self.battle_phase = "choose"

    def run(self):
        logger.log("Game loop started", "SYSTEM")
        while True:
            dt = self.clock.tick(FPS)
            self.anim.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    logger.log("Player closed the game window", "SYSTEM")
                    logger.close_logger()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event)

            self.draw()
            pygame.display.flip()

    def handle_key(self, event):
        if event.key == pygame.K_ESCAPE:
            logger.log("ESC pressed - resetting game", "INPUT")
            self.reset_game()
            return

        if self.state == STATE_DIFFICULTY:
            if event.key == pygame.K_UP:
                self.difficulty_idx = (self.difficulty_idx - 1) % 3
            elif event.key == pygame.K_DOWN:
                self.difficulty_idx = (self.difficulty_idx + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.setup_tournament()
                self.state = STATE_POKEMON_SELECT

        elif self.state == STATE_POKEMON_SELECT:
            n = len(self.tournament_pokemon)
            if event.key == pygame.K_LEFT:
                self.selected_pokemon_idx = (self.selected_pokemon_idx - 1) % n
            elif event.key == pygame.K_RIGHT:
                self.selected_pokemon_idx = (self.selected_pokemon_idx + 1) % n
            elif event.key == pygame.K_UP:
                self.selected_pokemon_idx = (self.selected_pokemon_idx - 4) % n
            elif event.key == pygame.K_DOWN:
                self.selected_pokemon_idx = (self.selected_pokemon_idx + 4) % n
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_tournament()

        elif self.state == STATE_BRACKET:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.advance_tournament()

        elif self.state == STATE_BATTLE:
            self.handle_battle_input(event)

        elif self.state == STATE_CPU_BATTLE:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                while not self.battle.finished:
                    self.run_cpu_battle_step()
                    if self.state == STATE_BRACKET:
                        break

        elif self.state == STATE_VICTORY:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.tournament.is_finished():
                    champ = self.tournament.get_champion()
                    is_player = (champ == self.player_pokemon)
                    logger.log_champion(champ.name, is_player)
                    self.state = STATE_CHAMPION
                else:
                    self.state = STATE_BRACKET

        elif self.state == STATE_CHAMPION:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_game()

    def draw(self):
        if self.state == STATE_DIFFICULTY:
            self.ui.draw_difficulty_screen(self.difficulty_idx)

        elif self.state == STATE_POKEMON_SELECT:
            self.ui.draw_pokemon_select(self.tournament_pokemon, self.selected_pokemon_idx)

        elif self.state == STATE_BRACKET:
            self.ui.draw_tournament_bracket(self.tournament)

        elif self.state == STATE_BATTLE:
            player_turn = (self.battle_phase == "choose")
            self.ui.draw_battle_screen(
                self.battle.pokemon1,
                self.battle.pokemon2,
                self.battle_text,
                self.move_cursor,
                player_turn,
                self.anim
            )

        elif self.state == STATE_CPU_BATTLE:
            if not self.battle.finished:
                self.run_cpu_battle_step()
            self.ui.draw_cpu_battle_screen(
                self.battle.pokemon1,
                self.battle.pokemon2,
                self.cpu_battle_msgs
            )
            if self.battle.finished and self.state != STATE_BRACKET:
                winner = self.battle.winner
                loser = self.battle.pokemon2 if winner == self.battle.pokemon1 else self.battle.pokemon1
                logger.log_tournament_result(self.battle.round_name, winner, loser)
                self.tournament.record_result(winner)
                self.state = STATE_BRACKET

        elif self.state == STATE_VICTORY:
            is_player_win = (self.current_winner == self.player_pokemon)
            self.ui.draw_victory_screen(self.current_winner, is_player_win)

        elif self.state == STATE_CHAMPION:
            champ = self.tournament.get_champion()
            is_player = (champ == self.player_pokemon)
            self.ui.draw_champion_screen(champ, is_player)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()