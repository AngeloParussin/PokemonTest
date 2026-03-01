import os
import json
import random
import pygame

POKEDEX_PATH = r"C:\Users\Angelo\Documents\pokemon\pokedex.json"
IMAGES_PATH  = r"C:\Users\Angelo\Documents\pokemon\pokemon_images"

# Fallback se eseguito da un percorso diverso
if not os.path.exists(POKEDEX_PATH):
    POKEDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pokedex.json")
if not os.path.exists(IMAGES_PATH):
    IMAGES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pokemon_images")


def load_pokedex():
    with open(POKEDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sprite(pokemon_name, size=(96, 96)):
    """
    Carica il sprite cercando per NOME del pokemon (es. "Charizard.png").
    Prova varianti: nome esatto, lowercase, uppercase, con spazi→underscore, ecc.
    """
    if not os.path.exists(IMAGES_PATH):
        return None

    # Varianti del nome da provare
    name_variants = [
        pokemon_name,                          # Charizard
        pokemon_name.lower(),                  # charizard
        pokemon_name.upper(),                  # CHARIZARD
        pokemon_name.replace(" ", "_"),        # Mr_Mime
        pokemon_name.replace(" ", "-"),        # Mr-Mime
        pokemon_name.replace(" ", ""),         # MrMime
        pokemon_name.replace(".", ""),         # rimuove punti (Mr. Mime → Mr Mime)
        pokemon_name.replace("'", ""),         # rimuove apostrofi (Farfetch'd)
        pokemon_name.replace(".", "").replace(" ", "_"),
        pokemon_name.replace(".", "").replace(" ", ""),
    ]

    extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp"]

    for variant in name_variants:
        for ext in extensions:
            path = os.path.join(IMAGES_PATH, variant + ext)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, size)
                    return img
                except Exception:
                    pass

    # Ricerca fuzzy: scansiona la cartella e trova il file più simile
    try:
        files = os.listdir(IMAGES_PATH)
        name_lower = pokemon_name.lower().replace(" ", "").replace(".", "").replace("'", "")
        for f in files:
            f_lower = f.lower()
            f_stem  = os.path.splitext(f_lower)[0].replace(" ", "").replace(".", "").replace("'", "").replace("_", "").replace("-", "")
            if f_stem == name_lower:
                try:
                    img = pygame.image.load(os.path.join(IMAGES_PATH, f)).convert_alpha()
                    img = pygame.transform.scale(img, size)
                    return img
                except Exception:
                    pass
    except Exception:
        pass

    return None


def select_tournament_pokemon(pokedex_data, count=16):
    """Seleziona 16 pokemon diversi dal pokedex."""
    pool = [p for p in pokedex_data if 1 <= p["id"] <= 151]
    if len(pool) < count:
        pool = pokedex_data[:200]
    return random.sample(pool, min(count, len(pool)))


def make_placeholder_sprite(color, size=(96, 96)):
    """Sprite placeholder colorato se l'immagine non è disponibile."""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(surf, color, (0, 0, size[0], size[1]))
    # Aggiunge un punto più chiaro per dare profondità
    light = tuple(min(255, c + 60) for c in color)
    pygame.draw.ellipse(surf, light, (size[0]//4, size[1]//6, size[0]//3, size[1]//3))
    return surf