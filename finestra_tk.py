# -*- coding: utf-8 -*-
# finestra_tk.py — grafica del Pokemon Tournament con Pygame

import pygame
import sys
import queue
import math
import os
import random


# ---------------------------------------------------------------
# COLORI — TEMA SCURO (default)
# ---------------------------------------------------------------

BG      = "#0a0e1a"
BG2     = "#111827"
BG3     = "#1a2235"
ACCENT  = "#00e5ff"
ACCENT2 = "#b06aff"
OK      = "#39ff14"
WARN    = "#ff6b35"
ERR     = "#ff2d55"
TXT     = "#e8eaf0"
TXT2    = "#7b8caa"
BORDER  = "#2a3650"
GOLD    = "#ffd700"

COL_HP  = OK
COL_DEF = ACCENT
COL_SPD = ACCENT2
COL_ATK = WARN
COL_SPA = "#ff9f43"
COL_VEL = "#48dbfb"

# Dizionari dei due temi — usati per aggiornare le variabili sopra
TEMA_SCURO = {
    "BG":"#0d0015","BG2":"#150025","BG3":"#200035",
    "ACCENT":"#c084fc","ACCENT2":"#a855f7",
    "OK":"#39ff14","WARN":"#ff6b35","ERR":"#ff2d55",
    "TXT":"#f5e8ff","TXT2":"#a78bba","BORDER":"#4a2060","GOLD":"#ffd700",
    "COL_HP":"#39ff14","COL_DEF":"#c084fc","COL_SPD":"#a855f7",
    "COL_ATK":"#ff6b35","COL_SPA":"#ff9f43","COL_VEL":"#e879f9",
    "BARRA_BG":"#200035",
    "BAR_BG":"#080010",
}

TEMA_CHIARO = {
    "BG":"#e8f4ff","BG2":"#d0e8ff","BG3":"#b8d8f8",
    "ACCENT":"#0369a1","ACCENT2":"#0ea5e9",
    "OK":"#16a34a","WARN":"#ea580c","ERR":"#dc2626",
    "TXT":"#0c1a2e","TXT2":"#2563a0","BORDER":"#5ba0d0","GOLD":"#b45309",
    "COL_HP":"#16a34a","COL_DEF":"#0369a1","COL_SPD":"#0ea5e9",
    "COL_ATK":"#ea580c","COL_SPA":"#d97706","COL_VEL":"#06b6d4",
    "BARRA_BG":"#b8d8f8",
    "BAR_BG":"#c0daf5",
}

TIPO_COL = {
    "Normal":"#9e9e9e","Fire":"#ff6b35","Water":"#0099ff","Grass":"#39ff14",
    "Electric":"#ffd700","Ice":"#48dbfb","Fighting":"#ff2d55","Poison":"#b06aff",
    "Ground":"#c8a06e","Flying":"#74b9ff","Psychic":"#fd79a8","Bug":"#a3cb38",
    "Rock":"#b8b000","Ghost":"#6c5ce7","Dragon":"#5352ed","Dark":"#636e72",
    "Steel":"#74b9ff","Fairy":"#fd79a8",
}


# ---------------------------------------------------------------
# DIMENSIONI
# ---------------------------------------------------------------

W, H = 1280, 760
BAR  = 44
TICK = 50

SPR_SEL = 36
SPR_PAN = 72
SPR_B   = 320
SPR_OFF = 0.05
SPR_CER_OFF_SEL = 0.25
SPR_CER_OFF_PAN = 0.25

GX = 50
GY = 80
AX = W - SPR_B - 50
AY = 140

LOW   = 282
LOG_N = 14

GRIGLIA_CELLA_W = 200
GRIGLIA_CELLA_H = 96
GRIGLIA_GAP     = 6
GRIGLIA_ORIG_X  = 238
GRIGLIA_ORIG_Y  = BAR + 10
GRIGLIA_COLONNE = 5
PANNELLO_L_W    = 230

BRACKET_TOP   = BAR + 35
BRACKET_H     = H - BAR - 65
BRACKET_BOX_W = 155
BRACKET_BOX_H = 56
BRACKET_GAP   = 18

FINAL_X1 = W // 2 - BRACKET_BOX_W // 2
FINAL_X2 = W // 2 + BRACKET_BOX_W // 2
SF_L_X2  = FINAL_X1 - BRACKET_GAP;  SF_L_X1 = SF_L_X2 - BRACKET_BOX_W
SF_R_X1  = FINAL_X2 + BRACKET_GAP;  SF_R_X2 = SF_R_X1 + BRACKET_BOX_W
QF_L_X2  = SF_L_X1 - BRACKET_GAP;  QF_L_X1 = QF_L_X2 - BRACKET_BOX_W
QF_R_X1  = SF_R_X2 + BRACKET_GAP;  QF_R_X2 = QF_R_X1 + BRACKET_BOX_W
R16_L_X2 = QF_L_X1 - BRACKET_GAP;  R16_L_X1 = R16_L_X2 - BRACKET_BOX_W
R16_R_X1 = QF_R_X2 + BRACKET_GAP;  R16_R_X2 = R16_R_X1 + BRACKET_BOX_W

R16_SLOT = BRACKET_H // 4
QF_SLOT  = BRACKET_H // 2
SF_Y     = BRACKET_TOP + BRACKET_H // 2 - BRACKET_BOX_H // 2


# ---------------------------------------------------------------
# FUNZIONI COLORE
# ---------------------------------------------------------------

def col(c):
    if isinstance(c, (tuple, list)):
        return (c[0], c[1], c[2])
    return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))

def ctk(c):
    if isinstance(c, tuple):
        return "#{:02x}{:02x}{:02x}".format(c[0], c[1], c[2])
    return c

converti_colore = col  # alias per compatibilita'


# ---------------------------------------------------------------
# CLASSE FINESTRA
# ---------------------------------------------------------------

class Finestra:

    def __init__(self, cart="PokemonGame/pokemon_images", cartella_dati="PokemonGame"):
        self.cartella_immagini   = cart
        self.cartella_dati       = cartella_dati
        self.cartella_wallpaper  = ""
        self.wallpaper_corrente  = None
        self.tema                = None
        self.barra_bg_colore     = "#1a2235"
        self.bar_top_colore      = "#070b14"
        self.hover_difficolta    = -1
        self.immagine_pannello   = None   # foto 230x716 nel pannello selezione
        self.cache_stile         = {}     # cache per immagini di stile (moon, ecc.)
        self.coda_comandi  = queue.Queue()
        self.coda_risposte = queue.Queue()
        self.schermata_corrente = "attesa"

        # Selezione
        self.lista_pokemon      = []
        self.hover_indice       = -1
        self.selezionato_indice = -1
        self.scroll_righe       = 0

        # Tabellone
        self.bracket_dati   = []
        self.nome_round_att = ""

        # Battaglia
        self.pokemon_giocatore  = None
        self.pokemon_avversario = None
        self.nome_round_batt    = ""
        self.e_turno_mio        = False
        self.pozioni_norm       = 1
        self.pozioni_spec       = 1
        self.messaggio_risultato = ""
        self.mostra_continua     = False
        self.log_battaglia       = []

        # Animazioni
        self.offset_x_giocatore    = 0
        self.offset_x_avversario   = 0
        self.animazione_scatto     = None
        self.animazione_scatto_avv = None
        self.animazione_ko         = None
        self.opacita_giocatore     = 255
        self.opacita_avversario    = 255
        self.numeri_fluttuanti     = []
        self.particelle_speciali   = []
        self.scia_attiva           = None
        self.onde_impatto          = []
        self.particelle_impatto    = []
        self.speed_lines           = []
        self.bolle_cura            = []   # bolle verdi/viola che salgono quando si usa una pozione
        self.shake_schermo         = None
        self.offset_shake_x        = 0
        self.offset_shake_y        = 0

        self.cache_immagini = {}
        self.hover_mossa    = -1
        self.schermo        = None
        self.in_esecuzione  = True
        # Scrollbar drag
        self.sb_dragging    = False
        self.sb_drag_y      = 0

    # -----------------------------------------------------------
    # AVVIO
    # -----------------------------------------------------------

    def avvia(self, thread_logica):
        pygame.init()
        pygame.display.set_caption("Pokemon Tournament")
        self.schermo = pygame.display.set_mode((W, H))
        self._crea_font()

        # Applica tema scuro come default — l'utente può cambiarlo dalla schermata difficoltà
        self._applica_tema("scuro")

        thread_logica.start()
        orologio = pygame.time.Clock()

        while self.in_esecuzione:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.coda_risposte.put({"tipo": "esci"})
                    self.in_esecuzione = False
                elif evento.type == pygame.MOUSEMOTION:
                    self._mouse_muove(evento.pos[0], evento.pos[1])
                    if self.sb_dragging:
                        self._scrollbar_drag(evento.pos[1])
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if not self._scrollbar_inizia_drag(evento.pos[0], evento.pos[1]):
                        self._mouse_click(evento.pos[0], evento.pos[1])
                elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                    self.sb_dragging = False
                elif evento.type == pygame.MOUSEWHEEL:
                    self._mouse_scroll(evento.y)

            self._leggi_messaggi()
            self._aggiorna_animazioni()
            self._disegna_frame()
            pygame.display.flip()
            orologio.tick(1000 // TICK)

        pygame.quit()

    def _crea_font(self):
        self.font_piccolo   = pygame.font.SysFont("consolas", 13)
        self.font_normale   = pygame.font.SysFont("consolas", 15)
        self.font_log       = pygame.font.SysFont("consolas", 16)
        self.font_nome      = pygame.font.SysFont("segoeui", 18)
        self.font_grassetto = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_titolo    = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_grande    = pygame.font.SysFont("segoeui", 38, bold=True)
        fs = "segoeuisymbol" if sys.platform=="win32" else ("applesymbols" if sys.platform=="darwin" else "dejavusans")
        self.font_simboli_s  = pygame.font.SysFont(fs, 15)
        self.font_simboli_m  = pygame.font.SysFont(fs, 20, bold=True)
        self.font_simboli_b  = pygame.font.SysFont(fs, 28, bold=True)
        self.font_simboli_xl = pygame.font.SysFont(fs, 38, bold=True)

    def _applica_tema(self, nome_tema):
        global BG, BG2, BG3, ACCENT, ACCENT2, OK, WARN, ERR, TXT, TXT2, BORDER, GOLD
        global COL_HP, COL_DEF, COL_SPD, COL_ATK, COL_SPA, COL_VEL
        self.tema = nome_tema  # salva il tema corrente
        t = TEMA_SCURO if nome_tema == "scuro" else TEMA_CHIARO
        BG=t["BG"]; BG2=t["BG2"]; BG3=t["BG3"]
        ACCENT=t["ACCENT"]; ACCENT2=t["ACCENT2"]
        OK=t["OK"]; WARN=t["WARN"]; ERR=t["ERR"]
        TXT=t["TXT"]; TXT2=t["TXT2"]; BORDER=t["BORDER"]; GOLD=t["GOLD"]
        COL_HP=t["COL_HP"]; COL_DEF=t["COL_DEF"]; COL_SPD=t["COL_SPD"]
        COL_ATK=t["COL_ATK"]; COL_SPA=t["COL_SPA"]; COL_VEL=t["COL_VEL"]
        self.barra_bg_colore = t["BARRA_BG"]
        self.bar_top_colore  = t["BAR_BG"]
        if nome_tema == "scuro":
            self.cartella_wallpaper = os.path.join(self.cartella_dati, "wallpaper_dark")
        else:
            self.cartella_wallpaper = os.path.join(self.cartella_dati, "wallpaper_light")
        # Carica immagine pannello selezione e stile (in background, non bloccante)
        self.immagine_pannello = self._carica_immagine_stile(
            f"panel_{nome_tema}.png", PANNELLO_L_W, H - BAR
        )
        self.cache_stile = {}  # svuota cache stile al cambio tema

    def _rett_tema(self):
        # Restituisce i rettangoli dei due bottoni tema (scuro a sinistra, chiaro a destra)
        lw, lh = 420, 200
        cy = H // 2
        return [
            (W//2 - lw - 20, cy - lh//2, W//2 - 20,      cy + lh//2),  # scuro
            (W//2 + 20,      cy - lh//2, W//2 + lw + 20, cy + lh//2),  # chiaro
        ]

    def _click_tema(self, x, y):
        for i, r in enumerate(self._rett_tema()):
            if self._in(x, y, r):
                self.tema = "scuro" if i == 0 else "chiaro"
                return

    def _disegna_schermata_tema(self):
        # Sfondo diviso: metà scuro, metà chiaro
        self.schermo.fill((10, 14, 26))
        metà = W // 2
        pygame.draw.rect(self.schermo, (240, 245, 252), (metà, 0, metà, H))
        # Linea divisoria
        pygame.draw.line(self.schermo, (100, 120, 150), (metà, 0), (metà, H), 2)

        # Titolo
        tit = self.font_grande.render("SCEGLI IL TEMA", True, (255, 255, 255))
        self.schermo.blit(tit, (metà - tit.get_width()//2, 80))

        rettangoli = self._rett_tema()

        # --- Bottone SCURO ---
        x1, y1, x2, y2 = rettangoli[0]
        pygame.draw.rect(self.schermo, (17, 24, 39),   pygame.Rect(x1, y1, x2-x1, y2-y1), 0, 18)
        pygame.draw.rect(self.schermo, (0, 229, 255),  pygame.Rect(x1, y1, x2-x1, y2-y1), 3, 18)
        # Icona luna
        self.schermo.blit(
            self.font_simboli_xl.render("🌙", True, (0, 229, 255)),
            (x1 + (x2-x1)//2 - 25, y1 + 30)
        )
        etichetta = self.font_titolo.render("SCURO", True, (0, 229, 255))
        self.schermo.blit(etichetta, (x1 + (x2-x1)//2 - etichetta.get_width()//2, y1 + 110))
        descr = self.font_normale.render("Interfaccia blu notte", True, (123, 140, 170))
        self.schermo.blit(descr, (x1 + (x2-x1)//2 - descr.get_width()//2, y1 + 148))

        # --- Bottone CHIARO ---
        x1, y1, x2, y2 = rettangoli[1]
        pygame.draw.rect(self.schermo, (226, 232, 240), pygame.Rect(x1, y1, x2-x1, y2-y1), 0, 18)
        pygame.draw.rect(self.schermo, (2, 132, 199),   pygame.Rect(x1, y1, x2-x1, y2-y1), 3, 18)
        # Icona sole
        self.schermo.blit(
            self.font_simboli_xl.render("☀", True, (180, 69, 0)),
            (x1 + (x2-x1)//2 - 25, y1 + 30)
        )
        etichetta = self.font_titolo.render("CHIARO", True, (2, 132, 199))
        self.schermo.blit(etichetta, (x1 + (x2-x1)//2 - etichetta.get_width()//2, y1 + 110))
        descr = self.font_normale.render("Interfaccia luminosa", True, (71, 85, 105))
        self.schermo.blit(descr, (x1 + (x2-x1)//2 - descr.get_width()//2, y1 + 148))

        # Suggerimento in basso
        hint = self.font_piccolo.render("Clicca per scegliere", True, (120, 130, 150))
        self.schermo.blit(hint, (metà - hint.get_width()//2, H - 50))
        self.font_piccolo   = pygame.font.SysFont("consolas", 13)
        self.font_normale   = pygame.font.SysFont("consolas", 15)
        self.font_log       = pygame.font.SysFont("consolas", 16)
        self.font_nome      = pygame.font.SysFont("segoeui", 18)
        self.font_grassetto = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_titolo    = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_grande    = pygame.font.SysFont("segoeui", 38, bold=True)
        fs = "segoeuisymbol" if sys.platform=="win32" else ("applesymbols" if sys.platform=="darwin" else "dejavusans")
        self.font_simboli_s  = pygame.font.SysFont(fs, 15)
        self.font_simboli_m  = pygame.font.SysFont(fs, 20, bold=True)
        self.font_simboli_b  = pygame.font.SysFont(fs, 28, bold=True)
        self.font_simboli_xl = pygame.font.SysFont(fs, 38, bold=True)

    # -----------------------------------------------------------
    # DISEGNO PRINCIPALE
    # -----------------------------------------------------------

    def _disegna_frame(self):
        self._sfondo()
        self._barra_top()
        if   self.schermata_corrente == "difficolta": self._disegna_difficolta()
        elif self.schermata_corrente == "selezione":  self._disegna_selezione()
        elif self.schermata_corrente == "tabellone":  self._disegna_tabellone()
        elif self.schermata_corrente == "battaglia":  self._disegna_battaglia()
        elif self.schermata_corrente == "campione":   self._disegna_campione()
        else:
            self._txt(W//2, H//2, "CARICAMENTO...", self.font_grande, col(ACCENT), "center")

    # -----------------------------------------------------------
    # PRIMITIVE
    # -----------------------------------------------------------

    def _txt(self, x, y, testo, font, colore, ancora="nw"):
        img = font.render(str(testo), True, colore)
        w, h = img.get_width(), img.get_height()
        if   ancora == "nw":     px, py = x,       y
        elif ancora == "w":      px, py = x,       y - h//2
        elif ancora == "e":      px, py = x - w,   y - h//2
        elif ancora == "ne":     px, py = x - w,   y
        elif ancora == "center": px, py = x - w//2, y - h//2
        elif ancora == "n":      px, py = x - w//2, y
        elif ancora == "s":      px, py = x - w//2, y - h
        elif ancora == "se":     px, py = x - w,   y - h
        else:                    px, py = x,       y
        self.schermo.blit(img, (px, py))
        return w, h

    def _rett(self, x1, y1, x2, y2, sfondo=None, bordo=None, sp=1):
        r = pygame.Rect(x1, y1, x2-x1, y2-y1)
        if sfondo: pygame.draw.rect(self.schermo, col(sfondo), r)
        if bordo:  pygame.draw.rect(self.schermo, col(bordo), r, sp)

    def _rett_r(self, x1, y1, x2, y2, raggio=12, sfondo=None, bordo=None, sp=1):
        raggio = min(raggio, (x2-x1)//2, (y2-y1)//2)
        r = pygame.Rect(x1, y1, x2-x1, y2-y1)
        if sfondo: pygame.draw.rect(self.schermo, col(sfondo), r, 0, border_radius=raggio)
        if bordo:  pygame.draw.rect(self.schermo, col(bordo),  r, sp, border_radius=raggio)

    def _linea(self, x1, y1, x2, y2, colore, sp=1):
        pygame.draw.line(self.schermo, col(colore), (x1,y1), (x2,y2), sp)

    def _cerchio(self, cx, cy, raggio, sfondo=None, bordo=None, sp=2):
        if sfondo: pygame.draw.circle(self.schermo, col(sfondo), (cx,cy), raggio)
        if bordo:  pygame.draw.circle(self.schermo, col(bordo),  (cx,cy), raggio, sp)

    def _barra(self, x, y, lw, lh, valore, massimo, c_fill):
        raggio = max(2, lh//2)
        r = pygame.Rect(x, y, lw, lh)
        pygame.draw.rect(self.schermo, col(BG3),   r, 0, border_radius=raggio)
        pygame.draw.rect(self.schermo, col(BORDER), r, 1, border_radius=raggio)
        if massimo > 0 and valore > 0:
            pieni = max(0, int(lw * min(valore, massimo) / massimo))
            if pieni > 0:
                pygame.draw.rect(self.schermo, col(c_fill),
                                 pygame.Rect(x, y, pieni, lh), 0, border_radius=raggio)

    def _overlay(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.schermo.blit(s, (0, 0))

    # -----------------------------------------------------------
    # IMMAGINI
    # -----------------------------------------------------------

    def _carica_immagine_stile(self, nome_file, larghezza, altezza):
        # Carica un'immagine dalla cartella style e la ridimensiona
        cartella = os.path.join(self.cartella_dati, "style")
        percorso = os.path.join(cartella, nome_file)
        if not os.path.isfile(percorso):
            return None
        try:
            from PIL import Image
            img = Image.open(percorso).convert("RGBA")
            img = img.resize((larghezza, altezza), Image.LANCZOS)
            return pygame.image.fromstring(img.tobytes(), (larghezza, altezza), "RGBA")
        except Exception:
            pass
        try:
            sup = pygame.image.load(percorso).convert_alpha()
            return pygame.transform.scale(sup, (larghezza, altezza))
        except Exception:
            return None

    def _carica_stile_cached(self, nome_file, larghezza, altezza):
        # Come _carica_immagine_stile ma con cache
        chiave = (nome_file, larghezza, altezza)
        if chiave not in self.cache_stile:
            self.cache_stile[chiave] = self._carica_immagine_stile(nome_file, larghezza, altezza)
        return self.cache_stile[chiave]

    def _carica_wallpaper(self):
        area_arena = (W, H - LOW - BAR)
        if not os.path.isdir(self.cartella_wallpaper):
            return None
        estensioni = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
        file_disponibili = [f for f in os.listdir(self.cartella_wallpaper) if f.lower().endswith(estensioni)]
        if not file_disponibili:
            return None
        nome_file = random.choice(file_disponibili)
        percorso  = os.path.join(self.cartella_wallpaper, nome_file)
        try:
            from PIL import Image
            img = Image.open(percorso).convert("RGBA")
            img = img.resize(area_arena, Image.LANCZOS)
            return pygame.image.fromstring(img.tobytes(), area_arena, "RGBA")
        except Exception:
            pass
        try:
            sup = pygame.image.load(percorso).convert_alpha()
            return pygame.transform.scale(sup, area_arena)
        except Exception:
            return None

    def _nomi_file(self, nome):
        # Genera tutti i possibili nomi file per un Pokemon (gestisce Mr. Mime, Type: Null, ecc.)
        n = nome.lower()
        candidati = [
            n, n.replace(" ","_"), n.replace(" ","-"), n.replace("-","_"), n.replace(" ",""),
            n.replace(".","").replace(" ","-"), n.replace(".","").replace(" ","_"),
            n.replace(".","").replace(" ",""), n.replace(":","").replace(" ","_"),
            n.replace(":","").replace(" ",""), n.replace(": ","-").replace(" ","_"),
            n.replace(".","").replace(":","").replace(" ","_"),
            n.replace(".","").replace(":","").replace(" ",""),
        ]
        visti, risultato = set(), []
        for c in candidati:
            nf = c + ".png"
            if nf not in visti:
                visti.add(nf)
                risultato.append(nf)
        return risultato

    def _carica_immagine(self, nome, dim, specchiata=False):
        chiave = (nome, dim, specchiata)
        if chiave in self.cache_immagini:
            return self.cache_immagini[chiave]
        for nf in self._nomi_file(nome):
            percorso = os.path.join(self.cartella_immagini, nf)
            if not os.path.isfile(percorso):
                continue
            try:
                from PIL import Image
                img = Image.open(percorso).convert("RGBA")
                img = img.resize((dim, dim), Image.NEAREST)
                if specchiata:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                sup = pygame.image.fromstring(img.tobytes(), (dim, dim), "RGBA")
                self.cache_immagini[chiave] = sup
                return sup
            except Exception:
                pass
            try:
                sup = pygame.image.load(percorso).convert_alpha()
                sup = pygame.transform.scale(sup, (dim, dim))
                if specchiata:
                    sup = pygame.transform.flip(sup, True, False)
                self.cache_immagini[chiave] = sup
                return sup
            except Exception:
                pass
        self.cache_immagini[chiave] = None
        return None

    def _sprite_libero(self, pokemon, cx, cy, dim):
        img = self._carica_immagine(pokemon["nome"], dim)
        if img:
            off_y = int(dim * 0.20)
            self.schermo.blit(img, (cx - dim//2, cy - dim//2 - off_y))
        else:
            tipo = pokemon["tipi"][0] if pokemon["tipi"] else "Normal"
            self._txt(cx, cy, pokemon["nome"][0].upper(), self.font_titolo,
                      col(TIPO_COL.get(tipo, TXT2)), "center")

    def _sprite_cerchio(self, pokemon, cx, cy, raggio, off_v=None):
        if off_v is None:
            off_v = SPR_CER_OFF_PAN
        tipo = pokemon["tipi"][0] if pokemon["tipi"] else "Normal"
        ct   = TIPO_COL.get(tipo, TXT2)
        self._cerchio(cx, cy, raggio, sfondo=BG3, bordo=ct, sp=2)
        dim = int(raggio * 3)
        img = self._carica_immagine(pokemon["nome"], dim)
        if img:
            sy = int(dim * off_v)
            self.schermo.blit(img, (cx - dim//2, cy - dim//2 - sy))
        else:
            self._txt(cx, cy, pokemon["nome"][0].upper(), self.font_grassetto, col(ct), "center")
        self._cerchio(cx, cy, raggio+1, bordo=ct, sp=1)

    def _ombra(self, x, y, dim):
        cx = x + dim//2
        lw = int(dim*0.5); lh = int(dim*0.08); yo = y + dim - int(dim*0.06)
        pygame.draw.ellipse(self.schermo, col("#060a10"), pygame.Rect(cx-lw//2, yo-lh, lw, lh*2))
        pygame.draw.ellipse(self.schermo, col("#0d1828"), pygame.Rect(cx-lw//3, yo-lh//2, lw*2//3, lh))

    def _sprite_battaglia(self, pokemon, cx, cy, opacita, specchiato=False):
        img = self._carica_immagine(pokemon["nome"], SPR_B, specchiata=specchiato)
        if img:
            if opacita < 255:
                s = img.copy(); s.set_alpha(opacita)
                self.schermo.blit(s, (cx - SPR_B//2, cy - SPR_B//2))
            else:
                self.schermo.blit(img, (cx - SPR_B//2, cy - SPR_B//2))
        else:
            tipo = pokemon["tipi"][0] if pokemon["tipi"] else "Normal"
            self._txt(cx, cy, pokemon["nome"][0].upper(), self.font_grande,
                      col(TIPO_COL.get(tipo, TXT2)), "center")

    # -----------------------------------------------------------
    # MESSAGGI DALLA LOGICA
    # -----------------------------------------------------------

    def _leggi_messaggi(self):
        while True:
            try:
                m = self.coda_comandi.get_nowait()
            except Exception:
                break
            tipo = m["tipo"]

            if tipo == "difficolta":
                self.schermata_corrente = "difficolta"
                self.lista_pokemon      = m.get("pool", [])
                self.log_battaglia      = []

            elif tipo == "selezione":
                self.lista_pokemon      = m["pool"]
                self.schermata_corrente = "selezione"
                self.hover_indice = self.selezionato_indice = self.scroll_righe = 0
                self.hover_indice = -1; self.selezionato_indice = -1

            elif tipo == "tabellone":
                self.bracket_dati        = m["bracket"]
                self.nome_round_att      = m.get("round_attuale", "")
                self.messaggio_risultato = m.get("messaggio", "")
                self.mostra_continua     = True
                self.schermata_corrente  = "tabellone"

            elif tipo == "battaglia_inizia":
                self.pokemon_giocatore   = m["giocatore"]
                self.pokemon_avversario  = m["avversario"]
                self.nome_round_batt     = m.get("round", "")
                self.log_battaglia       = []
                self.e_turno_mio         = False
                self.mostra_continua     = False
                self.messaggio_risultato = ""
                self.pozioni_norm = self.pokemon_giocatore["pozioni_normali"]
                self.pozioni_spec = self.pokemon_giocatore["pozioni_speciali"]
                self.offset_x_giocatore = self.offset_x_avversario = 0
                self.animazione_scatto = self.animazione_scatto_avv = self.animazione_ko = None
                self.opacita_giocatore = self.opacita_avversario = 255
                self.numeri_fluttuanti  = []
                self.particelle_speciali = []
                self.onde_impatto        = []
                self.particelle_impatto  = []
                self.speed_lines         = []
                self.bolle_cura          = []
                self.scia_attiva         = None
                self.flash_impatto       = None
                self.shake_schermo       = None
                self.offset_shake_x      = self.offset_shake_y = 0
                self._carica_immagine(self.pokemon_giocatore["nome"], SPR_B)
                self._carica_immagine(self.pokemon_avversario["nome"], SPR_B)
                # Carica il wallpaper solo se non ne abbiamo già uno per questo torneo
                if self.wallpaper_corrente is None:
                    self.wallpaper_corrente = self._carica_wallpaper()
                self.schermata_corrente = "battaglia"

            elif tipo == "aggiorna":
                self.pokemon_giocatore  = m["giocatore"]
                self.pokemon_avversario = m["avversario"]
                self.pozioni_norm = self.pokemon_giocatore["pozioni_normali"]
                self.pozioni_spec = self.pokemon_giocatore["pozioni_speciali"]

            elif tipo == "log":
                self.log_battaglia.append((m["testo"], ctk(m["colore"])))
                if len(self.log_battaglia) > 100:
                    self.log_battaglia = self.log_battaglia[-100:]

            elif tipo == "anim_attacco":
                chi    = m["chi"]
                valori = [(v[0], ctk(v[1])) for v in m["valori"]]
                self.animazione_scatto = {"chi": chi, "frame": 0, "durata": 10}
                self.shake_schermo = {"frame": 0, "durata": 8, "intensita": 5}

                # Punto di impatto = zona torace del bersaglio (più in basso del centro)
                if chi == "giocatore":
                    ix = AX + SPR_B//2; iy = AY + int(SPR_B * 0.55)
                    dir_x = 1.0
                else:
                    ix = GX + SPR_B//2; iy = GY + int(SPR_B * 0.55)
                    dir_x = -1.0

                # 3 onde d'urto concentriche che si espandono
                for k in range(3):
                    self.onde_impatto.append({
                        "chi_bersaglio": "avversario" if chi=="giocatore" else "giocatore",
                        "raggio": 0, "raggio_max": 80 + k*40,
                        "colore": (255, 220, 80),
                        "alpha": 220 - k*50,
                        "eta": k*3, "durata": 14,
                    })

                # Burst di particelle di impatto fisico
                for _ in range(20):
                    angolo = math.radians(random.uniform(-60, 60)) + (math.pi if dir_x > 0 else 0)
                    vel = random.uniform(5, 14)
                    self.particelle_impatto.append({
                        "chi_bersaglio": "avversario" if chi=="giocatore" else "giocatore",
                        "ox": float(ix), "oy": float(iy),
                        "x": float(ix), "y": float(iy),
                        "vx": math.cos(angolo) * vel,
                        "vy": math.sin(angolo) * vel - random.uniform(1, 4),
                        "eta": 0, "durata": random.randint(10, 18),
                        "raggio": random.randint(2, 6),
                        "colore": random.choice([(255,200,50),(255,140,20),(255,255,150),(255,100,30)]),
                    })

                # Speed lines: partono dall'attaccante, zona torace
                if chi == "giocatore":
                    ox = GX + SPR_B//2; oy = GY + int(SPR_B * 0.55)
                else:
                    ox = AX + SPR_B//2; oy = AY + int(SPR_B * 0.55)
                for _ in range(8):
                    offset_y = random.uniform(-SPR_B*0.2, SPR_B*0.2)
                    lunghezza = random.randint(60, 140)
                    self.speed_lines.append({
                        "x1": float(ox), "y1": float(oy + offset_y),
                        "dir_x": dir_x, "lunghezza": lunghezza,
                        "eta": 0, "durata": 8,
                    })

                px = ix; py = iy
                for i,(t,c) in enumerate(valori):
                    self.numeri_fluttuanti.append({"testo":t,"colore":c,"x":float(px),"y":float(py-i*26),"eta":0,"durata":70})

            elif tipo == "anim_attacco_doppio":
                vg = [(v[0],ctk(v[1])) for v in m["valori_gio"]]
                va = [(v[0],ctk(v[1])) for v in m["valori_avv"]]
                self.animazione_scatto     = {"chi":"giocatore",  "frame":0,"durata":10}
                self.animazione_scatto_avv = {"chi":"avversario", "frame":0,"durata":10}
                self.shake_schermo = {"frame": 0, "durata": 10, "intensita": 7}
                for chi_b, dir_x in [("avversario", 1.0), ("giocatore", -1.0)]:
                    for k in range(2):
                        self.onde_impatto.append({
                            "chi_bersaglio": chi_b,
                            "raggio":0,"raggio_max":70+k*35,
                            "colore":(255,220,80),"alpha":200-k*60,"eta":k*3,"durata":12,
                        })
                    for _ in range(12):
                        angolo = math.radians(random.uniform(-60,60)) + (math.pi if dir_x>0 else 0)
                        vel = random.uniform(4,11)
                        self.particelle_impatto.append({
                            "chi_bersaglio": chi_b,
                            "ox":0.0,"oy":0.0,"x":0.0,"y":0.0,
                            "vx":math.cos(angolo)*vel,"vy":math.sin(angolo)*vel-random.uniform(1,3),
                            "eta":0,"durata":random.randint(8,14),"raggio":random.randint(2,5),
                            "colore":random.choice([(255,200,50),(255,140,20),(255,255,150)]),
                        })
                for i,(t,c) in enumerate(vg):
                    self.numeri_fluttuanti.append({"testo":t,"colore":c,"x":float(AX+SPR_B//2),"y":float(AY+int(SPR_B*0.18)-i*26),"eta":0,"durata":70})
                for i,(t,c) in enumerate(va):
                    self.numeri_fluttuanti.append({"testo":t,"colore":c,"x":float(GX+SPR_B//2),"y":float(GY+int(SPR_B*0.18)-i*26),"eta":0,"durata":70})

            elif tipo == "anim_ko":
                chi = m["chi"]
                self.animazione_ko = {"chi":chi,"frame":0,"durata":14}
                self.animazione_scatto = self.animazione_scatto_avv = None
                self.offset_x_giocatore = self.offset_x_avversario = 0

            elif tipo == "anim_speciale":
                chi  = m["chi"]
                mult = m["moltiplicatore"]
                if   mult > 1:  cscia = (255,215,  0)
                elif mult == 0: cscia = ( 99,110,114)
                elif mult < 1:  cscia = (116,185,255)
                else:           cscia = (180,106,255)
                self.scia_attiva = {"chi":chi,"colore":cscia,"frame_rimasti":18}
                # Speed lines anche per l'attacco speciale
                dir_x = 1.0 if chi == "giocatore" else -1.0
                if chi == "giocatore":
                    ox = GX + SPR_B//2; oy = GY + int(SPR_B * 0.55)
                else:
                    ox = AX + SPR_B//2; oy = AY + int(SPR_B * 0.55)
                for _ in range(10):
                    offset_y = random.uniform(-SPR_B*0.35, SPR_B*0.35)
                    self.speed_lines.append({
                        "x1": float(ox), "y1": float(oy + offset_y),
                        "dir_x": dir_x, "lunghezza": random.randint(70, 160),
                        "eta": 0, "durata": 9,
                    })

            elif tipo == "anim_cura":
                chi    = m["chi"]
                valori = [(v[0],ctk(v[1])) for v in m["valori"]]
                px = (GX+SPR_B//2) if chi=="giocatore" else (AX+SPR_B//2)
                py = (GY+int(SPR_B*0.18)) if chi=="giocatore" else (AY+int(SPR_B*0.18))
                for i,(t,c) in enumerate(valori):
                    self.numeri_fluttuanti.append({"testo":t,"colore":c,"x":float(px),"y":float(py-i*30),"eta":0,"durata":100})

                # Bolle che salgono dal basso del Pokemon verso l'alto
                bx = (GX + SPR_B//2) if chi=="giocatore" else (AX + SPR_B//2)
                by = (GY + SPR_B - 20) if chi=="giocatore" else (AY + SPR_B - 20)
                tipo_poz = m.get("tipo_pozione", "normale")
                c_bolla = (160, 80, 255) if tipo_poz == "speciale" else (60, 220, 100)
                for _ in range(18):
                    self.bolle_cura.append({
                        "chi": chi,
                        "x": float(bx + random.uniform(-SPR_B*0.28, SPR_B*0.28)),
                        "y": float(by + random.uniform(-20, 20)),
                        "vy": random.uniform(-3.5, -1.8),
                        "vx": random.uniform(-0.8, 0.8),
                        "raggio": random.randint(4, 11),
                        "eta": random.randint(0, 8),   # sfasatura
                        "durata": random.randint(20, 35),
                        "colore": c_bolla,
                    })

            elif tipo == "chiedi_mossa":
                self.pokemon_giocatore = m["giocatore"]
                self.pozioni_norm = self.pokemon_giocatore["pozioni_normali"]
                self.pozioni_spec = self.pokemon_giocatore["pozioni_speciali"]
                self.e_turno_mio  = True

            elif tipo == "risultato":
                self.e_turno_mio = False
                self.messaggio_risultato = m["messaggio"]
                self.mostra_continua     = True

            elif tipo == "campione":
                self.messaggio_risultato = m["messaggio"]
                self.schermata_corrente  = "campione"
                self.mostra_continua     = True
                # Resetta il wallpaper: il prossimo torneo ne sceglierà uno nuovo
                self.wallpaper_corrente  = None

    # -----------------------------------------------------------
    # ANIMAZIONI
    # -----------------------------------------------------------

    def _aggiorna_animazioni(self):
        distanza = AX - GX - SPR_B // 2

        def sp(frame, durata):
            if frame >= durata: return 0
            p = frame / durata
            return int(distanza * (p/0.5)) if p < 0.5 else int(distanza * ((1-p)/0.5))

        if self.animazione_scatto is not None:
            f = self.animazione_scatto["frame"]
            d = self.animazione_scatto["durata"]
            chi = self.animazione_scatto["chi"]
            if f < d:
                s = sp(f, d)
                if chi == "giocatore":
                    self.offset_x_giocatore = s
                    if self.animazione_scatto_avv is None: self.offset_x_avversario = 0
                else:
                    self.offset_x_avversario = -s
                    if self.animazione_scatto_avv is None: self.offset_x_giocatore = 0
                self.animazione_scatto["frame"] += 1
            else:
                if chi == "giocatore": self.offset_x_giocatore  = 0
                else:                  self.offset_x_avversario = 0
                self.animazione_scatto = None

        if self.animazione_scatto_avv is not None:
            f = self.animazione_scatto_avv["frame"]
            d = self.animazione_scatto_avv["durata"]
            if f < d:
                self.offset_x_avversario = -sp(f, d)
                self.animazione_scatto_avv["frame"] += 1
            else:
                self.offset_x_avversario  = 0
                self.animazione_scatto_avv = None

        if self.animazione_ko is not None:
            f = self.animazione_ko["frame"]
            d = self.animazione_ko["durata"]
            chi = self.animazione_ko["chi"]
            if f < d:
                o = int(255 * (1 - f/d))
                if chi == "giocatore": self.opacita_giocatore  = o
                else:                  self.opacita_avversario = o
                self.animazione_ko["frame"] += 1
            else:
                if chi == "giocatore": self.opacita_giocatore  = 0
                else:                  self.opacita_avversario = 0
                self.animazione_ko = None

        self.numeri_fluttuanti = [
            {**n, "y": n["y"]-1.2, "eta": n["eta"]+1}
            for n in self.numeri_fluttuanti if n["eta"]+1 < n["durata"]
        ]

        # Onde d'urto all'impatto
        onde_vive = []
        for o in self.onde_impatto:
            o["eta"] += 1
            if o["eta"] < o["durata"]:
                if o["eta"] >= 0:  # sfasatura
                    prog = o["eta"] / o["durata"]
                    o["raggio"] = int(o["raggio_max"] * prog)
                onde_vive.append(o)
        self.onde_impatto = onde_vive

        # Particelle di impatto fisico — posizione iniziale calcolata dalla posizione del bersaglio
        pi_vive = []
        for p in self.particelle_impatto:
            if p["eta"] == 0:
                if p["chi_bersaglio"] == "giocatore":
                    p["x"] = float(GX + self.offset_x_giocatore + SPR_B//2)
                    p["y"] = float(GY + int(SPR_B * 0.55))
                else:
                    p["x"] = float(AX + self.offset_x_avversario + SPR_B//2)
                    p["y"] = float(AY + int(SPR_B * 0.55))
            p["x"] += p["vx"]; p["y"] += p["vy"]
            p["vy"] += 0.5; p["vx"] *= 0.92
            p["eta"] += 1
            if p["eta"] < p["durata"]: pi_vive.append(p)
        self.particelle_impatto = pi_vive

        # Bolle di cura
        bolle_vive = []
        for b in self.bolle_cura:
            b["eta"] += 1
            if b["eta"] > 0:
                b["x"] += b["vx"] + math.sin(b["eta"] * 0.4) * 0.6  # oscillazione laterale
                b["y"] += b["vy"]
            if b["eta"] < b["durata"]: bolle_vive.append(b)
        self.bolle_cura = bolle_vive

        # Speed lines
        sl_vive = []
        for sl in self.speed_lines:
            sl["eta"] += 1
            if sl["eta"] < sl["durata"]: sl_vive.append(sl)
        self.speed_lines = sl_vive

        # Shake schermo
        if self.shake_schermo is not None:
            f = self.shake_schermo["frame"]
            d = self.shake_schermo["durata"]
            intens = self.shake_schermo["intensita"]
            if f < d:
                # Intensità decresce nel tempo
                scala = (1 - f / d)
                self.offset_shake_x = int(random.uniform(-intens, intens) * scala)
                self.offset_shake_y = int(random.uniform(-intens, intens) * scala)
                self.shake_schermo["frame"] += 1
            else:
                self.offset_shake_x = 0
                self.offset_shake_y = 0
                self.shake_schermo  = None

        if self.scia_attiva is not None:
            chi_s = self.scia_attiva["chi"]
            cscia = self.scia_attiva["colore"]
            sx = (GX + self.offset_x_giocatore + SPR_B//2) if chi_s=="giocatore" else (AX + self.offset_x_avversario + SPR_B//2)
            sy = (GY + SPR_B//2 - int(SPR_B*SPR_OFF))      if chi_s=="giocatore" else (AY + SPR_B//2 - int(SPR_B*SPR_OFF))
            for _ in range(4):
                angolo = math.radians(random.uniform(0, 360))
                dist   = random.uniform(SPR_B*0.1, SPR_B*0.3)
                self.particelle_speciali.append({
                    "x": float(sx + math.cos(angolo)*dist),
                    "y": float(sy + math.sin(angolo)*dist*0.6),
                    "vx": random.uniform(-1.5, 1.5),
                    "vy": random.uniform(-2.5, -0.5),
                    "eta": 0, "durata": random.randint(8,16),
                    "raggio": random.randint(3,7), "colore": cscia,
                })
            self.scia_attiva["frame_rimasti"] -= 1
            if self.scia_attiva["frame_rimasti"] <= 0:
                self.scia_attiva = None

        vive = []
        for p in self.particelle_speciali:
            p["x"]  += p["vx"]; p["y"]  += p["vy"]; p["vy"] += 0.3; p["eta"] += 1
            if p["eta"] < p["durata"]: vive.append(p)
        self.particelle_speciali = vive

    # -----------------------------------------------------------
    # EVENTI MOUSE
    # -----------------------------------------------------------

    def _mouse_muove(self, x, y):
        if self.schermata_corrente == "selezione":
            self.hover_indice = self._cella(x, y)
        elif self.schermata_corrente == "difficolta":
            self.hover_difficolta = -1
            for i, r in enumerate(self._rett_diff()):
                if self._in(x, y, r):
                    self.hover_difficolta = i
                    break
        elif self.schermata_corrente == "battaglia":
            self.hover_mossa = -1
            for i, r in enumerate(self._rett_mosse()):
                if self._in(x, y, r): self.hover_mossa = i; break

    def _mouse_click(self, x, y):
        s = self.schermata_corrente

        if s == "difficolta":
            # Toggle giorno/notte
            if self._in(x, y, self._rett_toggle()):
                nuovo_tema = "chiaro" if self.tema == "scuro" else "scuro"
                self._applica_tema(nuovo_tema)
                self.wallpaper_corrente = None  # resetta il wallpaper col nuovo tema
                return
            for i, r in enumerate(self._rett_diff()):
                if self._in(x, y, r):
                    self.coda_risposte.put({"tipo":"difficolta","valore":["facile","media","difficile"][i]})
                    return

        elif s == "selezione":
            if self.selezionato_indice >= 0 and self._in(x, y, self._rett_inizia()):
                self.coda_risposte.put({"tipo":"pokemon","valore":self.lista_pokemon[self.selezionato_indice]})
                return
            idx = self._cella(x, y)
            if idx >= 0:
                self.selezionato_indice = self.hover_indice = idx

        elif s == "battaglia":
            if self.e_turno_mio:
                nomi = ["attacco","attacco_speciale","pozione_normale","pozione_speciale"]
                dis  = [False, False, self.pozioni_norm<=0, self.pozioni_spec<=0]
                for i, r in enumerate(self._rett_mosse()):
                    if not dis[i] and self._in(x, y, r):
                        self.e_turno_mio = False
                        self.coda_risposte.put({"tipo":"mossa","valore":nomi[i]})
                        return
            if self.mostra_continua and self._in(x, y, self._rett_cont()):
                self.mostra_continua = False
                self.coda_risposte.put({"tipo":"continua"})

        elif s in ("tabellone","campione"):
            if self.mostra_continua and self._in(x, y, self._rett_cont()):
                self.mostra_continua = False
                self.coda_risposte.put({"tipo":"continua"})

    def _mouse_scroll(self, dy):
        if self.schermata_corrente != "selezione": return
        dir_ = -1 if dy > 0 else 1
        max_ = max(0, math.ceil(len(self.lista_pokemon)/GRIGLIA_COLONNE) - 7)
        self.scroll_righe = max(0, min(max_, self.scroll_righe + dir_))

    # -----------------------------------------------------------
    # HIT TEST E RETTANGOLI
    # -----------------------------------------------------------

    def _in(self, px, py, r):
        return r[0] <= px <= r[2] and r[1] <= py <= r[3]

    def _rett_sb(self):
        # Restituisce (sb_x, sb_y, sb_w, sb_h) della scrollbar
        return (W - 16, GRIGLIA_ORIG_Y, 10, H - GRIGLIA_ORIG_Y - 8)

    def _scrollbar_inizia_drag(self, x, y):
        if self.schermata_corrente != "selezione": return False
        sb_x, sb_y, sb_w, sb_h = self._rett_sb()
        if not (sb_x <= x <= sb_x + sb_w and sb_y <= y <= sb_y + sb_h): return False
        self.sb_dragging = True
        self.sb_drag_y   = y
        return True

    def _scrollbar_drag(self, y):
        if not self.sb_dragging: return
        _, sb_y, _, sb_h = self._rett_sb()
        numero_righe   = math.ceil(len(self.lista_pokemon) / GRIGLIA_COLONNE)
        righe_visibili = 7
        scroll_max     = max(1, numero_righe - righe_visibili)
        rapporto       = (y - sb_y) / sb_h
        self.scroll_righe = max(0, min(scroll_max, int(rapporto * numero_righe)))

    def _rett_diff(self):
        lw, lh, gap = 420, 76, 18
        y0 = BAR + (H - BAR - lh*3 - gap*2) // 2
        cx = W // 2
        return [(cx-lw//2, y0+i*(lh+gap), cx+lw//2, y0+i*(lh+gap)+lh) for i in range(3)]

    def _cella(self, mx, my):
        if mx < GRIGLIA_ORIG_X or my < GRIGLIA_ORIG_Y: return -1
        c = (mx - GRIGLIA_ORIG_X) // (GRIGLIA_CELLA_W + GRIGLIA_GAP)
        r = (my - GRIGLIA_ORIG_Y) // (GRIGLIA_CELLA_H + GRIGLIA_GAP)
        if not (0 <= c < GRIGLIA_COLONNE): return -1
        if mx > GRIGLIA_ORIG_X + c*(GRIGLIA_CELLA_W+GRIGLIA_GAP) + GRIGLIA_CELLA_W: return -1
        if my > GRIGLIA_ORIG_Y + r*(GRIGLIA_CELLA_H+GRIGLIA_GAP) + GRIGLIA_CELLA_H: return -1
        idx = (self.scroll_righe + r) * GRIGLIA_COLONNE + c
        return idx if 0 <= idx < len(self.lista_pokemon) else -1

    def _rett_inizia(self):   return (W-230, 4, W-10, BAR-4)
    def _rett_cont(self):
        lw, lh = 260, 48
        x1 = W//2 - lw//2
        return (x1, H-76, x1+lw, H-76+lh)

    def _rett_mosse(self):
        lw_log = int(W*0.72); xi = lw_log+6; lw = W-xi-8
        lh = (LOW-16)//4 - 6
        return [(xi, H-LOW+8+i*(lh+6), xi+lw, H-LOW+8+i*(lh+6)+lh) for i in range(4)]

    # -----------------------------------------------------------
    # ELEMENTI COMUNI
    # -----------------------------------------------------------

    def _sfondo(self):
        self.schermo.fill(col(BG))
        if self.schermata_corrente != "battaglia":
            # Colore linee griglia adattato al tema (viola per scuro, azzurro per chiaro)
            if self.tema == "scuro":
                c_griglia = (30, 10, 50)
            else:
                c_griglia = (180, 210, 235)
            for x in range(0, W, 80): self._linea(x, 0, x, H, c_griglia)
            for y in range(0, H, 80): self._linea(0, y, W, y, c_griglia)

    def _barra_top(self):
        # Barra solida colore tema, bordo inferiore doppio pixel-art
        self._rett(0, 0, W, BAR, sfondo=self.bar_top_colore)
        self._linea(0, BAR,   W, BAR,   ACCENT, 3)
        self._linea(0, BAR-2, W, BAR-2, ACCENT2, 1)
        # Titolo POKEMON TOURNAMENT — shadow 2px, monospace + bold
        for dx, dy in [(2,2),(3,3)]:
            self._txt(18+dx, BAR//2+dy, "POKEMON TOURNAMENT", self.font_grassetto, (0,0,0), "w")
        self._txt(18, BAR//2, "POKEMON TOURNAMENT", self.font_grassetto, col(ACCENT), "w")
        # Pixel accent squares ai bordi del titolo
        pygame.draw.rect(self.schermo, col(ACCENT2), pygame.Rect(14, BAR//2-8, 4, 4))
        pygame.draw.rect(self.schermo, col(ACCENT2), pygame.Rect(14, BAR//2+4, 4, 4))
        s = self.schermata_corrente
        sub = {"difficolta":"SELEZIONA DIFFICOLTA'","selezione":"SCEGLI IL TUO POKEMON",
               "tabellone":self.nome_round_att.upper(),"battaglia":self.nome_round_batt.upper(),
               "campione":"CAMPIONE!"}.get(s,"")
        if sub:
            for dx, dy in [(2,2)]:
                self._txt(W-16+dx, BAR//2+dy, sub, self.font_normale, (0,0,0), "e")
            self._txt(W-16, BAR//2, sub, self.font_nome, col(TXT2), "e")

    def _btn_continua(self):
        x1,y1,x2,y2 = self._rett_cont()
        self._rett_r(x1,y1,x2,y2,raggio=12,sfondo=BG2,bordo=ACCENT2,sp=2)
        self._txt((x1+x2)//2,(y1+y2)//2,"▶  CONTINUA",self.font_simboli_m,col(ACCENT2),"center")

    # -----------------------------------------------------------
    # SCHERMATA: DIFFICOLTA'
    # -----------------------------------------------------------

    def _rett_toggle(self):
        tw, th = 160, 60
        return (W//2 - tw//2, H - 110, W//2 + tw//2, H - 110 + th)

    def _disegna_toggle(self):
        x1, y1, x2, y2 = self._rett_toggle()
        lw = x2 - x1; lh = y2 - y1
        raggio = lh // 2
        e_scuro = (self.tema == "scuro")

        # Sfondo del toggle
        if e_scuro:
            sfondo_c = (15, 20, 45)   # notte: blu scuro
        else:
            sfondo_c = (100, 180, 240) # giorno: azzurro cielo

        pygame.draw.rect(self.schermo, sfondo_c, pygame.Rect(x1, y1, lw, lh), 0, border_radius=raggio)

        # Dettagli di sfondo
        if e_scuro:
            # Stelline nella parte sinistra
            for sx, sy in [(x1+18,y1+12),(x1+40,y1+30),(x1+28,y1+42),(x1+55,y1+18),(x1+70,y1+38)]:
                pygame.draw.circle(self.schermo, (255,255,255), (sx,sy), 2)
        else:
            # Nuvoletta nella parte destra
            for cx_, cy_, cr in [(x2-65,y1+30,10),(x2-50,y1+24,13),(x2-35,y1+28,10)]:
                pygame.draw.circle(self.schermo, (255,255,255), (cx_,cy_), cr)

        # Thumb: notte → luna a DESTRA, giorno → sole a SINISTRA
        thumb_r = raggio - 5
        if e_scuro:
            tx = x2 - raggio   # destra = notte/luna
            # Luna grigia con crateri
            pygame.draw.circle(self.schermo, (210,210,210), (tx, y1+lh//2), thumb_r)
            pygame.draw.circle(self.schermo, (170,170,170), (tx+6, y1+lh//2-6), 5)
            pygame.draw.circle(self.schermo, (170,170,170), (tx-4, y1+lh//2+5), 3)
        else:
            tx = x1 + raggio   # sinistra = giorno/sole
            # Sole giallo
            pygame.draw.circle(self.schermo, (255,210,50), (tx, y1+lh//2), thumb_r)
            for ang in range(0, 360, 45):
                rad = math.radians(ang)
                rx1 = tx + int(math.cos(rad) * (thumb_r+3))
                ry1 = y1+lh//2 + int(math.sin(rad) * (thumb_r+3))
                rx2 = tx + int(math.cos(rad) * (thumb_r+8))
                ry2 = y1+lh//2 + int(math.sin(rad) * (thumb_r+8))
                pygame.draw.line(self.schermo, (255,190,20), (rx1,ry1), (rx2,ry2), 2)

        # Bordo
        bordo_c = (50,70,120) if e_scuro else (50,130,190)
        pygame.draw.rect(self.schermo, bordo_c, pygame.Rect(x1,y1,lw,lh), 2, border_radius=raggio)

        # Etichetta sotto
        label = "NOTTE" if e_scuro else "GIORNO"
        self._txt(W//2, y2+8, label, self.font_piccolo, col(TXT2), "n")

    def _disegna_difficolta(self):
        # Elementi ambientali in base al tema
        if self.tema == "scuro":
            # Stelle fisse in posizioni casuali ma deterministiche (seed fisso)
            rng = random.Random(42)
            for _ in range(60):
                sx = rng.randint(0, W)
                sy = rng.randint(BAR + 10, H - 140)
                sr = rng.randint(1, 3)
                bright = rng.randint(160, 255)
                pygame.draw.circle(self.schermo, (bright, bright, bright), (sx, sy), sr)

            # Moon.png in alto a destra
            moon = self._carica_stile_cached("moon.png", 110, 110)
            if moon:
                self.schermo.blit(moon, (W - 270, BAR + 20))
            else:
                pygame.draw.circle(self.schermo, (220, 220, 180), (W - 145, BAR + 75), 55)
                pygame.draw.circle(self.schermo, col(BG), (W - 125, BAR + 60), 42)

        ys = [170,320,460,590,700]
        psx = [(65,ys[0]),(215,ys[1]),(60,ys[2]),(210,ys[3]),(70,ys[4])]
        pdx = [(W-65,ys[0]),(W-215,ys[1]),(W-60,ys[2]),(W-210,ys[3]),(W-70,ys[4])]
        for i, p in enumerate(self.lista_pokemon[:5]):  self._sprite_libero(p, psx[i][0], psx[i][1], 270)
        for i, p in enumerate(self.lista_pokemon[5:10]): self._sprite_libero(p, pdx[i][0], pdx[i][1], 270)

        # Titolo con bordo pixel-art (ombra spostata di 3px)
        titolo = "SCEGLI LA DIFFICOLTA'"
        self._txt(W//2 + 3, BAR + 39, titolo, self.font_titolo, (0, 0, 0), "n")  # ombra
        self._txt(W//2,     BAR + 36, titolo, self.font_titolo, col(ACCENT), "n")

        nomi  = ["FACILE","MEDIA","DIFFICILE"]
        descr = ["CPU a caso","CPU sceglie meglio","CPU conosce la tua mossa"]
        clist = [OK, WARN, ERR]

        for i, (x1,y1,x2,y2) in enumerate(self._rett_diff()):
            c = clist[i]; cy = (y1+y2)//2
            hover = (i == self.hover_difficolta)
            # Ombra pixel-art
            pygame.draw.rect(self.schermo, (0,0,0), pygame.Rect(x1+4, y1+4, x2-x1, y2-y1), 0, 8)
            # Sfondo: si riempie col colore del bordo se hover
            sfondo_btn = c if hover else BG3
            self._rett_r(x1, y1, x2, y2, raggio=8, sfondo=sfondo_btn, bordo=c, sp=2)
            # Angolini pixel-art
            for qx, qy in [(x1,y1),(x2-6,y1),(x1,y2-6),(x2-6,y2-6)]:
                pygame.draw.rect(self.schermo, col(c), pygame.Rect(qx, qy, 6, 6))
            testo_c = BG if hover else TXT2
            nome_c  = BG if hover else c
            self._txt(x1+22, cy-10, nomi[i],  self.font_grassetto, col(nome_c), "w")
            self._txt(x1+22, cy+12, descr[i], self.font_normale,   col(testo_c),"w")
            self._txt(x2-20, cy,    "›",      self.font_simboli_b, col(nome_c), "e")

        self._disegna_toggle()

    # -----------------------------------------------------------
    # SCHERMATA: SELEZIONE
    # -----------------------------------------------------------

    def _disegna_selezione(self):
        self._rett(0, BAR, PANNELLO_L_W, H, sfondo=BG2, bordo=BORDER)

        # Immagine di sfondo nel pannello (panel_scuro.png o panel_chiaro.png dalla cartella style)
        if self.immagine_pannello is not None:
            self.schermo.blit(self.immagine_pannello, (0, BAR))

        self._linea(PANNELLO_L_W, BAR, PANNELLO_L_W, H, ACCENT)

        if 0 <= self.selezionato_indice < len(self.lista_pokemon):
            self._pannello_stats(self.lista_pokemon[self.selezionato_indice])
        else:
            self._txt(PANNELLO_L_W//2, H//2-20, "CLICCA UN", self.font_grassetto, col(TXT2), "center")
            self._txt(PANNELLO_L_W//2, H//2+5,  "POKEMON",   self.font_grassetto, col(TXT2), "center")

        x1,y1,x2,y2 = self._rett_inizia()
        attivo = self.selezionato_indice >= 0
        if attivo:
            # Ombra pixel-art + bottone monocolore ACCENT
            pygame.draw.rect(self.schermo, (0,0,0), pygame.Rect(x1+3, y1+3, x2-x1, y2-y1), 0, 4)
            pygame.draw.rect(self.schermo, col(ACCENT), pygame.Rect(x1, y1, x2-x1, y2-y1), 0, 4)
            # Angolini neri pixel-art
            for qx, qy in [(x1,y1),(x2-4,y1),(x1,y2-4),(x2-4,y2-4)]:
                pygame.draw.rect(self.schermo, (0,0,0), pygame.Rect(qx, qy, 4, 4))
            self._txt((x1+x2)//2+1,(y1+y2)//2+1,"INIZIA BATTAGLIA",self.font_simboli_s,(0,0,0),"center")
            self._txt((x1+x2)//2,  (y1+y2)//2,  "INIZIA BATTAGLIA",self.font_simboli_s,col(BG),"center")
        else:
            pygame.draw.rect(self.schermo, col(BG3), pygame.Rect(x1, y1, x2-x1, y2-y1), 0, 4)
            pygame.draw.rect(self.schermo, col(BORDER), pygame.Rect(x1, y1, x2-x1, y2-y1), 2, 4)
            self._txt((x1+x2)//2,(y1+y2)//2,"SCEGLI UN POKEMON",self.font_simboli_s,col(TXT2),"center")

        self._griglia()
        self._scrollbar()

    def _scrollbar(self):
        numero_righe   = math.ceil(len(self.lista_pokemon) / GRIGLIA_COLONNE)
        righe_visibili = 7
        if numero_righe <= righe_visibili:
            return
        sb_x, sb_y, sb_w, sb_h = self._rett_sb()
        # Sfondo pixel-art — angoli quadrati, bordo doppio
        pygame.draw.rect(self.schermo, col(BG3), pygame.Rect(sb_x, sb_y, sb_w, sb_h))
        pygame.draw.rect(self.schermo, col(BORDER), pygame.Rect(sb_x, sb_y, sb_w, sb_h), 1)
        pygame.draw.rect(self.schermo, col(ACCENT2), pygame.Rect(sb_x-1, sb_y-1, sb_w+2, sb_h+2), 1)
        # Thumb — colore accent pieno, angoli quadrati
        proporzione = righe_visibili / numero_righe
        thumb_h = max(20, int(sb_h * proporzione))
        scroll_max = numero_righe - righe_visibili
        thumb_y = sb_y + int((sb_h - thumb_h) * (self.scroll_righe / max(1, scroll_max)))
        pygame.draw.rect(self.schermo, col(ACCENT), pygame.Rect(sb_x, thumb_y, sb_w, thumb_h))
        # Lineette decorative sul thumb
        for dy in range(thumb_h // 4, thumb_h, thumb_h // 4):
            pygame.draw.rect(self.schermo, col(ACCENT2),
                             pygame.Rect(sb_x+2, thumb_y+dy, sb_w-4, 1))

    def _griglia(self):
        for riga in range(8):
            for colonna in range(GRIGLIA_COLONNE):
                idx = (self.scroll_righe + riga) * GRIGLIA_COLONNE + colonna
                if idx >= len(self.lista_pokemon): break
                px = GRIGLIA_ORIG_X + colonna * (GRIGLIA_CELLA_W + GRIGLIA_GAP)
                py = GRIGLIA_ORIG_Y + riga    * (GRIGLIA_CELLA_H + GRIGLIA_GAP)
                if py + GRIGLIA_CELLA_H > H: break
                self._cella_pokemon(self.lista_pokemon[idx], px, py,
                                    idx==self.hover_indice, idx==self.selezionato_indice)

    def _cella_pokemon(self, pokemon, x, y, hover, selezionato):
        tipo = pokemon["tipi"][0] if pokemon["tipi"] else "Normal"
        if selezionato:
            self._rett_r(x,y,x+GRIGLIA_CELLA_W,y+GRIGLIA_CELLA_H,raggio=14,sfondo="#1e3a28",bordo=OK,sp=2)
            cn = OK
        elif hover:
            self._rett_r(x,y,x+GRIGLIA_CELLA_W,y+GRIGLIA_CELLA_H,raggio=14,sfondo="#162030",bordo=ACCENT,sp=2)
            cn = ACCENT
        else:
            self._rett_r(x,y,x+GRIGLIA_CELLA_W,y+GRIGLIA_CELLA_H,raggio=14,sfondo=BG3,bordo=BORDER,sp=1)
            cn = TXT

        self._rett(x+2, y+8, x+5, y+GRIGLIA_CELLA_H-8, sfondo=TIPO_COL.get(tipo,TXT2))

        raggio = SPR_SEL
        cxs = x + 10 + raggio; cys = y + GRIGLIA_CELLA_H // 2
        self._sprite_cerchio(pokemon, cxs, cys, raggio, SPR_CER_OFF_SEL)

        tx = cxs + raggio + 8; ty = y + 6
        self._txt(tx, ty, pokemon["nome"][:14], self.font_normale, col(cn))

        xt = tx; yt = ty + 21; xm = x + GRIGLIA_CELLA_W - 6
        for t in pokemon["tipi"]:
            tw, th = self.font_piccolo.size(t)
            lbw = tw + 8; lbh = th + 4
            if xt + lbw > xm: break
            self._rett_r(xt, yt, xt+lbw, yt+lbh, raggio=4, sfondo=TIPO_COL.get(t,TXT2))
            self._txt(xt+lbw//2, yt+lbh//2, t, self.font_piccolo, col(TXT), "center")
            xt += lbw + 3

        lb = GRIGLIA_CELLA_W - (tx-x) - 8; yb = ty + 46
        self._barra(tx, yb,   lb, 5, pokemon["stats"]["hp"],     250, COL_HP);  yb += 8
        self._barra(tx, yb,   lb, 5, pokemon["stats"]["attack"],  200, COL_ATK); yb += 8
        self._barra(tx, yb,   lb, 5, pokemon["stats"]["speed"],   200, COL_VEL)

    def _pannello_stats(self, pokemon):
        cx = PANNELLO_L_W // 2; cy = BAR + 20 + SPR_PAN
        self._sprite_cerchio(pokemon, cx, cy, SPR_PAN, SPR_CER_OFF_PAN)
        y = cy + SPR_PAN + 12
        self._txt(cx, y, pokemon["nome"], self.font_grassetto, col(TXT), "center")
        y += 22
        xb = 10
        for tipo in pokemon["tipi"]:
            lbw = len(tipo)*7+14
            self._rett_r(xb, y, xb+lbw, y+17, raggio=6, sfondo=TIPO_COL.get(tipo,TXT2))
            self._txt(xb+lbw//2, y+8, tipo, self.font_piccolo, col(TXT), "center")
            xb += lbw + 5
        y += 28
        self._linea(10, y, PANNELLO_L_W-10, y, BORDER)
        y += 8
        lb = PANNELLO_L_W - 24
        for nome, valore, massimo, cb in [
            ("HP",pokemon["stats"]["hp"],250,COL_HP),("ATK",pokemon["stats"]["attack"],200,COL_ATK),
            ("DEF",pokemon["stats"]["defense"],250,COL_DEF),("SpA",pokemon["stats"]["sp_attack"],194,COL_SPA),
            ("SpD",pokemon["stats"]["sp_defense"],250,COL_SPD),("VEL",pokemon["stats"]["speed"],200,COL_VEL),
        ]:
            self._txt(12, y+3, nome, self.font_piccolo, col(TXT2), "w")
            self._txt(PANNELLO_L_W-12, y+3, str(valore), self.font_piccolo, col(TXT), "e")
            y += 15
            self._barra(12, y, lb, 8, valore, massimo, cb)
            y += 12

    # -----------------------------------------------------------
    # SCHERMATA: TABELLONE
    # -----------------------------------------------------------

    def _disegna_tabellone(self):
        vuoto = lambda n: [{"a":"","b":"","vincitore":None} for _ in range(n)]
        r16 = self.bracket_dati[0] if len(self.bracket_dati)>=1 else vuoto(8)
        rqf = self.bracket_dati[1] if len(self.bracket_dati)>=2 else vuoto(4)
        rsf = self.bracket_dati[2] if len(self.bracket_dati)>=3 else vuoto(2)
        rf  = self.bracket_dati[3] if len(self.bracket_dati)>=4 else vuoto(1)
        while len(r16)<8: r16.append({"a":"","b":"","vincitore":None})
        while len(rqf)<4: rqf.append({"a":"","b":"","vincitore":None})
        while len(rsf)<2: rsf.append({"a":"","b":"","vincitore":None})
        while len(rf) <1: rf.append( {"a":"","b":"","vincitore":None})

        yi = BRACKET_TOP - 22
        for testo, xc, c in [
            ("ROUND OF 16",(R16_L_X1+R16_L_X2)//2,ACCENT),("QUARTI",(QF_L_X1+QF_L_X2)//2,ACCENT),
            ("SEMIFINALI",(SF_L_X1+SF_L_X2)//2,ACCENT),("FINALE",W//2,GOLD),
            ("SEMIFINALI",(SF_R_X1+SF_R_X2)//2,ACCENT),("QUARTI",(QF_R_X1+QF_R_X2)//2,ACCENT),
            ("ROUND OF 16",(R16_R_X1+R16_R_X2)//2,ACCENT),
        ]: self._txt(xc, yi, testo, self.font_piccolo, col(c), "n")

        for i in range(4):
            ym = BRACKET_TOP + i*R16_SLOT + (R16_SLOT-BRACKET_BOX_H)//2
            self._box_match(r16[i],   R16_L_X1, ym)
            self._linea(R16_L_X2, ym+BRACKET_BOX_H//2, (R16_L_X2+QF_L_X1)//2, ym+BRACKET_BOX_H//2, BORDER)
            self._box_match(r16[i+4], R16_R_X1, ym)
            self._linea(R16_R_X1, ym+BRACKET_BOX_H//2, (R16_R_X1+QF_R_X2)//2, ym+BRACKET_BOX_H//2, BORDER)

        for i in range(2):
            ym = BRACKET_TOP + i*QF_SLOT + (QF_SLOT-BRACKET_BOX_H)//2
            cy = ym + BRACKET_BOX_H//2
            ya = BRACKET_TOP + (i*2+0)*R16_SLOT + R16_SLOT//2
            yb_ = BRACKET_TOP + (i*2+1)*R16_SLOT + R16_SLOT//2
            xrl = (R16_L_X2+QF_L_X1)//2; xrr = (R16_R_X1+QF_R_X2)//2
            self._box_match(rqf[i],   QF_L_X1, ym)
            self._linea(QF_L_X2,cy,(QF_L_X2+SF_L_X1)//2,cy,BORDER)
            self._linea(xrl,ya,xrl,yb_,BORDER); self._linea(xrl,cy,QF_L_X1,cy,BORDER)
            self._box_match(rqf[i+2], QF_R_X1, ym)
            self._linea(QF_R_X1,cy,(QF_R_X1+SF_R_X2)//2,cy,BORDER)
            self._linea(xrr,ya,xrr,yb_,BORDER); self._linea(QF_R_X2,cy,xrr,cy,BORDER)

        cyl = cyr = SF_Y + BRACKET_BOX_H//2
        self._box_match(rsf[0], SF_L_X1, SF_Y)
        self._linea(SF_L_X2,cyl,(SF_L_X2+FINAL_X1)//2,cyl,BORDER)
        xrl2=(QF_L_X2+SF_L_X1)//2
        self._linea(xrl2,BRACKET_TOP+0*QF_SLOT+QF_SLOT//2,xrl2,BRACKET_TOP+1*QF_SLOT+QF_SLOT//2,BORDER)
        self._linea(xrl2,cyl,SF_L_X1,cyl,BORDER)

        self._box_match(rsf[1], SF_R_X1, SF_Y)
        self._linea(SF_R_X1,cyr,(SF_R_X1+FINAL_X2)//2,cyr,BORDER)
        xrr2=(QF_R_X1+SF_R_X2)//2
        self._linea(xrr2,BRACKET_TOP+0*QF_SLOT+QF_SLOT//2,xrr2,BRACKET_TOP+1*QF_SLOT+QF_SLOT//2,BORDER)
        self._linea(SF_R_X2,cyr,xrr2,cyr,BORDER)

        self._box_match(rf[0], FINAL_X1, SF_Y)
        cf = SF_Y + BRACKET_BOX_H//2
        self._linea((SF_L_X2+FINAL_X1)//2,cf,FINAL_X1,cf,BORDER)
        self._linea(FINAL_X2,cf,(SF_R_X1+FINAL_X2)//2,cf,BORDER)

        if self.mostra_continua:
            if self.messaggio_risultato:
                self._txt(W//2, H-110, self.messaggio_risultato, self.font_grassetto, col(ACCENT), "center")
            self._btn_continua()

    def _box_match(self, match, x, y):
        na = match.get("a","?"); nb = match.get("b","?"); vc = match.get("vincitore")
        self._rett_r(x,y,x+BRACKET_BOX_W,y+BRACKET_BOX_H,raggio=8,sfondo=BG2,
                     bordo=(OK if vc else BORDER),sp=1)
        meta = BRACKET_BOX_H // 2
        ca, pra = (OK,"▶ ") if vc==na else ((TXT2,"  ") if vc else (TXT,"  "))
        self._txt(x+8, y+meta//2, pra+na[:16], self.font_simboli_s, col(ca), "w")
        self._linea(x+3, y+meta, x+BRACKET_BOX_W-3, y+meta, BORDER)
        cb, prb = (OK,"▶ ") if vc==nb else ((TXT2,"  ") if vc else (TXT,"  "))
        self._txt(x+8, y+meta+meta//2, prb+nb[:16], self.font_simboli_s, col(cb), "w")

    # -----------------------------------------------------------
    # SCHERMATA: BATTAGLIA
    # -----------------------------------------------------------

    def _disegna_battaglia(self):
        if self.pokemon_giocatore is None or self.pokemon_avversario is None:
            return

        # Sfondo arena: wallpaper se disponibile, altrimenti gradiente scuro
        if self.wallpaper_corrente is not None:
            self.schermo.blit(self.wallpaper_corrente, (0, BAR))
        else:
            # Gradiente di fallback
            alt = H - LOW - BAR
            for i in range(8):
                p = i/8
                r_ = int(0x0a+(0x14-0x0a)*p); g_ = int(0x0e+(0x1c-0x0e)*p); b_ = int(0x1a+(0x35-0x1a)*p)
                yi_ = BAR+int(i*alt/8); yf_ = BAR+int((i+1)*alt/8)
                pygame.draw.rect(self.schermo, (r_,g_,b_), (0,yi_,W,yf_-yi_))

        self._linea(0, H-LOW, W, H-LOW, ACCENT, 2)
        self._barre_pokemon(self.pokemon_giocatore,  14,    BAR+8, 300, True)
        self._barre_pokemon(self.pokemon_avversario, W-314, BAR+8, 300, False)

        # Applico lo shake a entrambi gli sprite
        sx = self.offset_shake_x
        sy = self.offset_shake_y

        # Speed lines durante lo scatto (disegnate PRIMA degli sprite)
        for sl in self.speed_lines:
            prog = sl["eta"] / sl["durata"]
            alpha = int(200 * (1 - prog))
            lx1 = int(sl["x1"])
            ly1 = int(sl["y1"])
            lx2 = int(sl["x1"] + sl["dir_x"] * sl["lunghezza"] * prog * 1.5)
            ly2 = ly1
            if alpha > 20:
                spessore = max(1, int(3 * (1 - prog)))
                pygame.draw.line(self.schermo, (220, 220, 255), (lx1, ly1), (lx2, ly2), spessore)

        cxg = GX + self.offset_x_giocatore + SPR_B//2 + sx
        cyg = GY + SPR_B//2 - int(SPR_B*SPR_OFF) + sy
        if self.opacita_giocatore > 0:
            self._sprite_battaglia(self.pokemon_giocatore, cxg, cyg, self.opacita_giocatore, specchiato=True)

        cxa = AX + self.offset_x_avversario + SPR_B//2 + sx
        cya = AY + SPR_B//2 - int(SPR_B*SPR_OFF) + sy
        if self.opacita_avversario > 0:
            self._sprite_battaglia(self.pokemon_avversario, cxa, cya, self.opacita_avversario)

        # Onde d'urto espandenti — centrate sulla posizione CORRENTE del bersaglio
        for o in self.onde_impatto:
            if o["raggio"] > 0:
                prog = o["eta"] / o["durata"]
                alpha = int(o["alpha"] * (1 - prog))
                if alpha > 10:
                    # Posizione corrente del bersaglio (zona torace, include shake)
                    if o["chi_bersaglio"] == "giocatore":
                        cx_t = cxg; cy_t = cyg + int(SPR_B * 0.1)
                    else:
                        cx_t = cxa; cy_t = cya + int(SPR_B * 0.1)
                    spessore = max(1, int(4 * (1 - prog)))
                    r, g, b = o["colore"]
                    r2 = min(255, r + int((255-r)*prog*0.5))
                    g2 = min(255, g + int((255-g)*prog*0.5))
                    b2 = min(255, b + int((255-b)*prog*0.5))
                    pygame.draw.circle(self.schermo, (r2, g2, b2),
                                       (int(cx_t), int(cy_t)), o["raggio"], spessore)

        # Particelle scia attacco speciale
        for p in self.particelle_speciali:
            prog = p["eta"]/p["durata"]; ra = max(1,int(p["raggio"]*(1-prog*0.6)))
            if prog < 0.92:
                pygame.draw.circle(self.schermo, p["colore"], (int(p["x"]),int(p["y"])), ra)
                if ra >= 3: pygame.draw.circle(self.schermo,(255,255,255),(int(p["x"]),int(p["y"])),max(1,ra//3))

        # Particelle di impatto fisico
        for p in self.particelle_impatto:
            prog = p["eta"] / p["durata"]
            ra = max(1, int(p["raggio"] * (1 - prog)))
            r, g, b = p["colore"]
            r2 = min(255, r + int((255-r)*prog*0.6))
            g2 = min(255, g + int((255-g)*prog*0.6))
            b2 = min(255, b + int((255-b)*prog*0.6))
            pygame.draw.circle(self.schermo, (r2, g2, b2), (int(p["x"]), int(p["y"])), ra)

        # Bolle di cura: cerchi semitrasparenti che salgono
        for b in self.bolle_cura:
            if b["eta"] <= 0: continue
            prog = b["eta"] / b["durata"]
            alpha = int(200 * (1 - prog))
            if alpha < 10: continue
            r, g, bv = b["colore"]
            # Cerchio esterno colorato
            pygame.draw.circle(self.schermo, (r, g, bv), (int(b["x"]), int(b["y"])), b["raggio"], 2)
            # Riflesso bianco piccolo in alto a sinistra della bolla
            rx = int(b["x"] - b["raggio"] * 0.3)
            ry = int(b["y"] - b["raggio"] * 0.3)
            rr = max(1, b["raggio"] // 4)
            pygame.draw.circle(self.schermo, (255, 255, 255), (rx, ry), rr)

        # Zona bassa
        lw_log = int(W*0.72)
        self._rett(0,H-LOW,lw_log,H,sfondo=BG2); self._rett(lw_log,H-LOW,W,H,sfondo=BG)
        self._linea(lw_log,H-LOW,lw_log,H,BORDER)
        self._rett_r(8,H-LOW+8,lw_log-8,H-8,raggio=10,sfondo=BG3,bordo=BORDER)

        messaggi = self.log_battaglia[-LOG_N:]
        y_log = H-LOW+14; alt_r = (H-16-y_log)//LOG_N
        for i,(testo,cm) in enumerate(messaggi):
            self._txt(16, y_log+i*alt_r, testo[:88], self.font_log, col(cm) if cm else col(TXT))

        nomi_btn  = ["ATTACCO","ATT. SPECIALE","POZIONE","POZ. SPECIALE"]
        col_btn   = [COL_ATK,COL_SPA,COL_HP,COL_SPD]
        det_btn   = ["ATK:"+str(self.pokemon_giocatore["stats"]["attack"]),
                     "SpA:"+str(self.pokemon_giocatore["stats"]["sp_attack"]),
                     "x"+str(self.pozioni_norm), "x"+str(self.pozioni_spec)]
        dis       = [False,False,self.pozioni_norm<=0,self.pozioni_spec<=0]

        for i,(x1,y1,x2,y2) in enumerate(self._rett_mosse()):
            cm = col_btn[i]; eh = (self.hover_mossa==i and self.e_turno_mio and not dis[i])
            if dis[i]:          csf,cbr,ct,cd = BG3,BORDER,TXT2,TXT2
            elif eh:            csf,cbr,ct,cd = cm,cm,BG,BG
            elif self.e_turno_mio: csf,cbr,ct,cd = BG2,cm,cm,TXT2
            else:               csf,cbr,ct,cd = BG3,BORDER,TXT2,TXT2
            self._rett_r(x1,y1,x2,y2,raggio=8,sfondo=csf,bordo=cbr,sp=2)
            cy_ = (y1+y2)//2
            self._txt(x1+10, cy_-8, nomi_btn[i], self.font_normale, col(ct), "w")
            self._txt(x1+10, cy_+8, det_btn[i],  self.font_piccolo, col(cd), "w")

        for n in self.numeri_fluttuanti:
            prog = n["eta"]/n["durata"]; cs = n["colore"]
            try:
                rv=int(cs[1:3],16); gv=int(cs[3:5],16); bv=int(cs[5:7],16)
                cf_=(max(0,min(255,int(rv*(1-prog)+0x0a*prog))),max(0,min(255,int(gv*(1-prog)+0x0e*prog))),max(0,min(255,int(bv*(1-prog)+0x1a*prog))))
            except Exception:
                cf_ = col(cs)
            self._txt(int(n["x"]),int(n["y"]),n["testo"],self.font_titolo,cf_,"center")

        if self.mostra_continua and self.animazione_ko is None:
            self._overlay()
            if self.messaggio_risultato:
                self._txt(W//2,H//2-60,self.messaggio_risultato,self.font_grassetto,col(ACCENT),"center")
            self._btn_continua()

    def _barre_pokemon(self, pokemon, x, y0, lw, e_giocatore):
        c_nome = ACCENT if e_giocatore else ACCENT2
        self._txt(x, y0, pokemon["nome"], self.font_grassetto, col(c_nome))
        y = y0 + 36
        for nome, valore, massimo, cb in [
            ("HP", pokemon["hp_attuale"],       pokemon["stats"]["hp"],         COL_HP),
            ("DEF",pokemon["difesa_attuale"],    pokemon["stats"]["defense"],    COL_DEF),
            ("SpD",pokemon["sp_difesa_attuale"], pokemon["stats"]["sp_defense"], COL_SPD),
        ]:
            self._txt(x, y+1, nome, self.font_piccolo, col(TXT2))
            xb = x+34; lwb = lw-80
            r_ = pygame.Rect(xb, y, lwb, 10)
            pygame.draw.rect(self.schermo, col(self.barra_bg_colore), r_, 0, border_radius=5)
            pygame.draw.rect(self.schermo, col(BORDER), r_, 1, border_radius=5)
            if massimo > 0:
                pieni = max(0, int(lwb * min(valore,massimo)/massimo))
                if pieni > 0:
                    pygame.draw.rect(self.schermo,col(cb),pygame.Rect(xb,y,pieni,10),0,border_radius=5)
            self._txt(x+lw, y+1, f"{int(valore)}/{massimo}", self.font_piccolo, col(TXT), "ne")
            y += 16

    # -----------------------------------------------------------
    # SCHERMATA: CAMPIONE
    # -----------------------------------------------------------

    def _disegna_campione(self):
        for i in range(12):
            a = i*30*math.pi/180
            self._linea(W//2, H//2-60, W//2+int(math.cos(a)*500), H//2-60+int(math.sin(a)*500), "#302800")
        self._txt(W//2, H//2-100, "◈  CAMPIONE DEL TORNEO  ◈", self.font_simboli_xl, col(GOLD), "center")
        self._txt(W//2, H//2-50,  self.messaggio_risultato,    self.font_titolo,    col(ACCENT),"center")
        if self.mostra_continua:
            x1,y1,x2,y2 = self._rett_cont()
            self._rett_r(x1,y1,x2,y2,raggio=12,sfondo=BG2,bordo=ACCENT2,sp=2)
            self._txt((x1+x2)//2,(y1+y2)//2,"▶  GIOCA ANCORA",self.font_simboli_m,col(ACCENT2),"center")
