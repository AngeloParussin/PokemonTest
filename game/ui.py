import pygame
import math

# GameBoy Color palette
GB_WHITE = (248, 248, 248)
GB_LIGHT = (168, 208, 136)
GB_DARK = (48, 98, 48)
GB_BLACK = (15, 56, 15)
GB_BG = (155, 188, 15)
GB_MENU_BG = (200, 220, 160)
GB_HP_GREEN = (0, 200, 0)
GB_HP_YELLOW = (220, 180, 0)
GB_HP_RED = (200, 0, 0)
GB_BORDER = (40, 80, 40)
GB_TEXT = (15, 40, 15)
GB_TITLE = (30, 30, 100)
GB_HIGHLIGHT = (255, 255, 100)
GB_SHADOW = (80, 80, 80)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 40, 40)
BLUE = (40, 80, 200)
YELLOW = (220, 180, 0)
DARK_BLUE = (20, 30, 80)

TYPE_COLORS = {
    "Normal":   (168, 168, 120),
    "Fire":     (240, 128, 48),
    "Water":    (104, 144, 240),
    "Grass":    (120, 200, 80),
    "Electric": (248, 208, 48),
    "Ice":      (152, 216, 216),
    "Fighting": (192, 48, 40),
    "Poison":   (160, 64, 160),
    "Ground":   (224, 192, 104),
    "Flying":   (168, 144, 240),
    "Psychic":  (248, 88, 136),
    "Bug":      (168, 184, 32),
    "Rock":     (184, 160, 56),
    "Ghost":    (112, 88, 152),
    "Dragon":   (112, 56, 248),
    "Dark":     (112, 88, 72),
    "Steel":    (184, 184, 208),
    "Fairy":    (238, 153, 172),
}


def get_font(size):
    return pygame.font.SysFont("Courier New", size, bold=True)


def draw_text(surface, text, x, y, color=GB_TEXT, size=14):
    font = get_font(size)
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))
    return surf.get_width()


def draw_text_centered(surface, text, cx, y, color=GB_TEXT, size=14):
    font = get_font(size)
    surf = font.render(text, True, color)
    surface.blit(surf, (cx - surf.get_width() // 2, y))


def draw_panel(surface, rect, bg=GB_WHITE, border=GB_BORDER, radius=6, border_width=3):
    pygame.draw.rect(surface, bg, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, border_width, border_radius=radius)


def draw_hp_bar(surface, x, y, w, h, hp_pct, label="HP"):
    # Background
    pygame.draw.rect(surface, (80, 80, 80), (x, y, w, h))
    # HP fill
    fill_w = max(0, int(w * hp_pct))
    if hp_pct > 0.5:
        color = GB_HP_GREEN
    elif hp_pct > 0.2:
        color = GB_HP_YELLOW
    else:
        color = GB_HP_RED
    if fill_w > 0:
        pygame.draw.rect(surface, color, (x, y, fill_w, h))
    pygame.draw.rect(surface, GB_BORDER, (x, y, w, h), 2)
    # Label
    font = get_font(10)
    lbl = font.render(label, True, GB_TEXT)
    surface.blit(lbl, (x - lbl.get_width() - 4, y))


def draw_type_badge(surface, type_name, x, y):
    color = TYPE_COLORS.get(type_name, (150, 150, 150))
    font = get_font(10)
    txt = font.render(type_name.upper(), True, WHITE)
    w = txt.get_width() + 8
    h = 14
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=3)
    surface.blit(txt, (x + 4, y + 1))
    return w + 4


class AnimationManager:
    def __init__(self):
        self.animations = []

    def add_shake(self, target_rect, duration=20):
        self.animations.append({"type": "shake", "rect": target_rect, "timer": duration, "total": duration})

    def add_flash(self, surface_fn, duration=30):
        self.animations.append({"type": "flash", "fn": surface_fn, "timer": duration, "total": duration})

    def update(self):
        for anim in self.animations[:]:
            anim["timer"] -= 1
            if anim["timer"] <= 0:
                self.animations.remove(anim)

    def get_shake_offset(self, rect_id):
        import random
        for anim in self.animations:
            if anim["type"] == "shake" and anim["rect"] == rect_id:
                progress = anim["timer"] / anim["total"]
                if progress > 0.2:
                    return (random.randint(-4, 4), random.randint(-2, 2))
        return (0, 0)

    def is_flashing(self):
        for anim in self.animations:
            if anim["type"] == "flash":
                return (anim["timer"] // 4) % 2 == 0
        return False


class UI:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.anim = AnimationManager()

    def draw_difficulty_screen(self, selected):
        self.screen.fill(DARK_BLUE)
        # Title
        draw_text_centered(self.screen, "POKEMON TOURNAMENT", self.width // 2, 40, YELLOW, 24)
        draw_text_centered(self.screen, "Select Difficulty", self.width // 2, 90, WHITE, 16)

        options = [
            ("EASY",   "CPU uses random moves & random Pokemon",   (80, 160, 80)),
            ("NORMAL", "CPU picks strongest Pokemon & best moves", (200, 160, 40)),
            ("HARD",   "CPU picks type counters & plays smart",    (200, 60, 60)),
        ]
        for i, (name, desc, color) in enumerate(options):
            y = 140 + i * 90
            rect = pygame.Rect(self.width // 2 - 220, y, 440, 70)
            bg = color if i == selected else (50, 50, 80)
            draw_panel(self.screen, rect, bg, YELLOW if i == selected else GB_BORDER, 8, 3 if i != selected else 4)
            draw_text_centered(self.screen, name, self.width // 2, y + 10, WHITE, 20)
            draw_text_centered(self.screen, desc, self.width // 2, y + 40, (200, 200, 200), 11)

        draw_text_centered(self.screen, "UP/DOWN to select  |  ENTER to confirm", self.width // 2, self.height - 40, (160, 160, 160), 12)

    def draw_pokemon_select(self, pokemon_list, selected_idx, scroll_offset=0):
        self.screen.fill(DARK_BLUE)
        draw_text_centered(self.screen, "CHOOSE YOUR POKEMON", self.width // 2, 20, YELLOW, 22)
        draw_text_centered(self.screen, "Your Pokemon will enter the tournament!", self.width // 2, 55, WHITE, 13)

        cols = 4
        rows = 4
        cell_w = 150
        cell_h = 80
        start_x = (self.width - cols * cell_w) // 2
        start_y = 80

        for i in range(min(16, len(pokemon_list))):
            row = i // cols
            col = i % cols
            x = start_x + col * cell_w
            y = start_y + row * cell_h
            rect = pygame.Rect(x + 4, y + 4, cell_w - 8, cell_h - 8)
            is_sel = (i == selected_idx)
            bg = (80, 100, 160) if is_sel else (30, 40, 70)
            border = YELLOW if is_sel else GB_BORDER
            draw_panel(self.screen, rect, bg, border, 6, 3 if not is_sel else 4)

            p = pokemon_list[i]
            if p.sprite:
                spr = pygame.transform.scale(p.sprite, (40, 40))
                self.screen.blit(spr, (x + 10, y + 10))
            else:
                col_sprite = TYPE_COLORS.get(p.types[0], (150, 150, 150))
                placeholder = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(placeholder, col_sprite, (20, 20), 18)
                self.screen.blit(placeholder, (x + 10, y + 10))

            name = p.name[:10]
            draw_text(self.screen, name, x + 56, y + 12, WHITE, 11)
            # Type badge
            tx = x + 56
            for t in p.types[:1]:
                draw_type_badge(self.screen, t, tx, y + 30)
            # Stats abbreviated
            draw_text(self.screen, f"HP:{p.max_hp}", x + 56, y + 48, (180, 220, 180), 10)

        draw_text_centered(self.screen, "Arrow keys to browse  |  ENTER to select", self.width // 2, self.height - 30, (160, 160, 160), 12)

    def draw_battle_screen(self, player_poke, enemy_poke, text_lines, move_cursor, player_turn, anim_manager=None):
        # Background
        self.screen.fill((180, 200, 140))

        # Draw battle field
        pygame.draw.ellipse(self.screen, (140, 170, 100), (350, 260, 260, 60))  # enemy platform
        pygame.draw.ellipse(self.screen, (120, 160, 80), (80, 330, 220, 50))   # player platform

        # Enemy info panel (top left)
        enemy_panel = pygame.Rect(20, 20, 280, 90)
        draw_panel(self.screen, enemy_panel, GB_WHITE, GB_BORDER, 8)
        draw_text(self.screen, enemy_poke.name, 30, 28, GB_TEXT, 14)
        tx = 30
        for t in enemy_poke.types:
            tw = draw_type_badge(self.screen, t, tx, 48)
            tx += tw
        draw_text(self.screen, f"HP: {enemy_poke.hp}/{enemy_poke.max_hp}", 30, 65, GB_TEXT, 12)
        draw_hp_bar(self.screen, 90, 70, 160, 10, enemy_poke.hp_percent())

        # Player info panel (bottom right)
        player_panel = pygame.Rect(self.width - 300, self.height - 180, 280, 90)
        draw_panel(self.screen, player_panel, GB_WHITE, GB_BORDER, 8)
        draw_text(self.screen, player_poke.name, self.width - 290, self.height - 172, GB_TEXT, 14)
        tx = self.width - 290
        for t in player_poke.types:
            tw = draw_type_badge(self.screen, t, tx, self.height - 152)
            tx += tw
        draw_text(self.screen, f"HP: {player_poke.hp}/{player_poke.max_hp}", self.width - 290, self.height - 135, GB_TEXT, 12)
        draw_hp_bar(self.screen, self.width - 230, self.height - 130, 160, 10, player_poke.hp_percent())

        # Defense boosts


        # Enemy sprite
        enemy_offset = (0, 0)
        if anim_manager:
            enemy_offset = anim_manager.get_shake_offset("enemy")
        ex, ey = 400 + enemy_offset[0], 140 + enemy_offset[1]
        if enemy_poke.sprite:
            spr = pygame.transform.scale(enemy_poke.sprite, (120, 120))
            self.screen.blit(spr, (ex, ey))
        else:
            col = TYPE_COLORS.get(enemy_poke.types[0], (200, 150, 100))
            placeholder = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(placeholder, col, (50, 50), 48)
            draw_text_centered(placeholder, enemy_poke.name[:3], 50, 40, WHITE, 14)
            self.screen.blit(placeholder, (ex + 10, ey + 10))

        # Player sprite
        player_offset = (0, 0)
        if anim_manager:
            player_offset = anim_manager.get_shake_offset("player")
        px, py = 130 + player_offset[0], 230 + player_offset[1]
        if player_poke.sprite:
            spr = pygame.transform.scale(player_poke.sprite, (120, 120))
            # Flip for back sprite feel
            spr = pygame.transform.flip(spr, True, False)
            self.screen.blit(spr, (px, py))
        else:
            col = TYPE_COLORS.get(player_poke.types[0], (100, 150, 200))
            placeholder = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(placeholder, col, (50, 50), 48)
            draw_text_centered(placeholder, player_poke.name[:3], 50, 40, WHITE, 14)
            self.screen.blit(placeholder, (px + 10, py))

        # Text box (bottom)
        text_box = pygame.Rect(10, self.height - 110, self.width - 10, 100)
        draw_panel(self.screen, text_box, GB_WHITE, GB_BORDER, 6)
        for i, line in enumerate(text_lines[-3:]):
            draw_text(self.screen, line, 20, self.height - 100 + i * 22, GB_TEXT, 13)

        # Move menu (right side of text box when player's turn)
        if player_turn:
            menu_x = self.width // 2
            menu_panel = pygame.Rect(menu_x, self.height - 110, self.width - menu_x - 10, 100)
            draw_panel(self.screen, menu_panel, GB_MENU_BG, GB_BORDER, 6)
            # I nomi delle mosse vengono presi direttamente dagli oggetti Move del pokemon
            for i, move in enumerate(player_poke.moves):
                my = self.height - 100 + i * 22
                mx = menu_x + 10
                if i == move_cursor:
                    pygame.draw.rect(self.screen, GB_HIGHLIGHT, (mx - 4, my - 1, 185, 20), border_radius=3)
                    draw_text(self.screen, f"> {move.name}", mx, my, GB_TEXT, 13)
                    # Mostra la stat rilevante come indicatore potenza
                    if move.move_type == "physical":
                        draw_text(self.screen, f"ATK:{player_poke.attack}", mx + 140, my, (60, 100, 160), 11)
                    elif move.move_type == "special":
                        draw_text(self.screen, f"SPA:{player_poke.sp_attack}", mx + 140, my, (160, 60, 160), 11)
                    elif move.move_type == "defense":
                        draw_text(self.screen, f"DEF:{player_poke.defense}", mx + 140, my, (60, 160, 100), 11)
                    elif move.move_type == "sp_defense":
                        draw_text(self.screen, f"SPD:{player_poke.sp_defense}", mx + 140, my, (60, 160, 100), 11)
                else:
                    draw_text(self.screen, f"  {move.name}", mx, my, GB_TEXT, 13)

    def draw_tournament_bracket(self, tournament, current_round_highlight=None):
        self.screen.fill(DARK_BLUE)
        draw_text_centered(self.screen, "TOURNAMENT BRACKET", self.width // 2, 15, YELLOW, 20)

        round_names = ["Round of 16", "Quarter", "Semi", "Final", "Champion"]
        rounds_data = tournament.rounds
        results_data = tournament.results

        total_rounds = len(rounds_data)
        col_w = (self.width - 40) // max(total_rounds + 1, 4)

        for r_idx, (matches, results) in enumerate(zip(rounds_data, results_data)):
            x = 20 + r_idx * col_w
            n = len(matches)
            spacing = (self.height - 80) // (n + 1)
            rname = round_names[r_idx] if r_idx < len(round_names) else f"R{r_idx+1}"
            draw_text_centered(self.screen, rname, x + col_w // 2, 45, (180, 220, 180), 11)

            for m_idx, (match, winner) in enumerate(zip(matches, results)):
                y = 65 + (m_idx + 1) * spacing - 20
                for p_i, poke in enumerate(match):
                    py = y + p_i * 22
                    is_winner = (winner == poke)
                    is_player = (poke == tournament.player_pokemon)
                    bg = (80, 140, 80) if is_winner else (40, 50, 80)
                    if is_player:
                        bg = (80, 80, 160)
                    border = YELLOW if is_player else ((100, 180, 100) if is_winner else (60, 70, 100))
                    rect = pygame.Rect(x, py, col_w - 8, 18)
                    draw_panel(self.screen, rect, bg, border, 3, 2)
                    name_short = poke.name[:10]
                    color = YELLOW if is_player else (WHITE if is_winner else (180, 180, 180))
                    draw_text(self.screen, name_short, x + 4, py + 2, color, 10)

        # Show champion if tournament over
        champ = tournament.get_champion()
        if champ:
            x = 20 + total_rounds * col_w
            draw_text_centered(self.screen, "CHAMPION", x + col_w // 2, 45, YELLOW, 12)
            is_player = (champ == tournament.player_pokemon)
            bg = (80, 80, 160) if is_player else (80, 140, 80)
            rect = pygame.Rect(x, 70, col_w - 8, 26)
            draw_panel(self.screen, rect, bg, YELLOW, 4, 3)
            draw_text_centered(self.screen, champ.name[:10], x + col_w // 2, 78, YELLOW, 12)

        round_name = tournament.get_round_name()
        draw_text_centered(self.screen, f"Current: {round_name}", self.width // 2, self.height - 35, WHITE, 13)
        draw_text_centered(self.screen, "ENTER to continue", self.width // 2, self.height - 18, (160, 160, 160), 11)

    def draw_victory_screen(self, winner, is_player_win):
        self.screen.fill(DARK_BLUE)
        if is_player_win:
            draw_text_centered(self.screen, "VICTORY!", self.width // 2, 100, YELLOW, 36)
            draw_text_centered(self.screen, f"{winner.name} won the battle!", self.width // 2, 180, WHITE, 18)
        else:
            draw_text_centered(self.screen, "DEFEATED!", self.width // 2, 100, RED, 36)
            draw_text_centered(self.screen, f"{winner.name} was eliminated...", self.width // 2, 180, (200, 180, 180), 18)
        draw_text_centered(self.screen, "ENTER to continue", self.width // 2, self.height - 60, (160, 160, 160), 14)

    def draw_champion_screen(self, champion, is_player):
        self.screen.fill(DARK_BLUE)
        t = pygame.time.get_ticks() // 500
        colors = [YELLOW, WHITE, (255, 150, 50)]
        draw_text_centered(self.screen, "TOURNAMENT CHAMPION!", self.width // 2, 80, colors[t % 3], 28)
        if is_player:
            draw_text_centered(self.screen, "YOU ARE THE CHAMPION!", self.width // 2, 140, YELLOW, 22)
        draw_text_centered(self.screen, champion.name, self.width // 2, 200, WHITE, 30)
        if champion.sprite:
            spr = pygame.transform.scale(champion.sprite, (160, 160))
            self.screen.blit(spr, (self.width // 2 - 80, 240))
        draw_text_centered(self.screen, "Press ENTER to play again or ESC to quit", self.width // 2, self.height - 50, (160, 160, 160), 13)

    def draw_waiting_screen(self, msg):
        self.screen.fill(DARK_BLUE)
        draw_text_centered(self.screen, msg, self.width // 2, self.height // 2, WHITE, 16)

    def draw_cpu_battle_screen(self, p1, p2, msgs):
        self.screen.fill((100, 120, 80))
        draw_text_centered(self.screen, "CPU vs CPU Battle", self.width // 2, 20, YELLOW, 18)
        draw_text_centered(self.screen, f"{p1.name}", self.width // 4, 60, WHITE, 16)
        draw_text_centered(self.screen, "VS", self.width // 2, 60, YELLOW, 20)
        draw_text_centered(self.screen, f"{p2.name}", 3 * self.width // 4, 60, WHITE, 16)

        draw_hp_bar(self.screen, 30, 90, 200, 14, p1.hp_percent(), p1.name[:8])
        draw_hp_bar(self.screen, self.width - 230, 90, 200, 14, p2.hp_percent(), p2.name[:8])

        if p1.sprite:
            spr = pygame.transform.scale(p1.sprite, (100, 100))
            self.screen.blit(spr, (80, 120))
        if p2.sprite:
            spr = pygame.transform.scale(p2.sprite, (100, 100))
            self.screen.blit(spr, (self.width - 180, 120))

        panel = pygame.Rect(10, self.height - 120, self.width - 20, 110)
        draw_panel(self.screen, panel, GB_WHITE, GB_BORDER, 6)
        for i, line in enumerate(msgs[-4:]):
            draw_text(self.screen, line, 20, self.height - 112 + i * 24, GB_TEXT, 13)
