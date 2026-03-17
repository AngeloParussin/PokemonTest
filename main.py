# -*- coding: utf-8 -*-
# main.py — punto di ingresso del gioco

import os
import sys
import random
import argparse
import threading

# Su Windows forza UTF-8 per evitare problemi con lettere accentate
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.environ["PYTHONIOENCODING"] = "utf-8"

from dati       import carica_pokedex, carica_tipi
from torneo     import crea_bracket, esegui_torneo, chiedi_difficolta, chiedi_pokemon, DIMENSIONE_TORNEO
from finestra_tk import Finestra

DIMENSIONE_POOL = 50  # quanti Pokemon vengono mostrati nella schermata di selezione


def logica_gioco(finestra, tutti_i_pokemon, tabella_tipi):
    # Questo gira in un thread separato mentre Pygame gira nel thread principale
    try:
        while True:
            # Pokemon decorativi per la schermata difficoltà
            pool_deco = random.sample(tutti_i_pokemon, min(10, len(tutti_i_pokemon)))

            # 1. Scelta difficoltà
            difficolta = chiedi_difficolta(finestra, pool_deco)

            # 2. Pool di 50 Pokemon tra cui scegliere
            pool = random.sample(tutti_i_pokemon, min(DIMENSIONE_POOL, len(tutti_i_pokemon)))

            # 3. Il giocatore sceglie il suo Pokemon
            giocatore = chiedi_pokemon(finestra, pool)

            # 4. Scelgo i 15 avversari in base alla difficoltà
            altri = [p for p in pool if p is not giocatore]

            def stats_totali(p):
                s = p["stats"]
                return s["hp"] + s["attack"] + s["defense"] + s["sp_attack"] + s["sp_defense"] + s["speed"]

            if difficolta == "difficile":
                # I 15 più forti del pool
                avversari = sorted(altri, key=stats_totali, reverse=True)[:DIMENSIONE_TORNEO - 1]
            elif difficolta == "facile":
                # I 15 più deboli del pool
                avversari = sorted(altri, key=stats_totali, reverse=False)[:DIMENSIONE_TORNEO - 1]
            else:
                # Media: 15 casuali
                avversari = random.sample(altri, DIMENSIONE_TORNEO - 1)

            partecipanti = crea_bracket([giocatore] + avversari)

            # 5. Esegui il torneo
            esegui_torneo(giocatore, partecipanti, tabella_tipi, difficolta, finestra=finestra)

    except SystemExit:
        pass  # finestra chiusa dal giocatore
    except Exception as e:
        print(f"[ERRORE LOGICA] {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Pokemon Tournament")
    parser.add_argument("--data", default="PokemonGame", help="Cartella dati (default: PokemonGame)")
    args = parser.parse_args()

    percorso_pokedex = os.path.join(args.data, "pokedex.json")
    percorso_tipi    = os.path.join(args.data, "types.json")
    cartella_img  = os.path.join(args.data, "pokemon_images")

    if not os.path.isfile(percorso_pokedex):
        print(f"ERRORE: {percorso_pokedex} non trovato")
        sys.exit(1)
    if not os.path.isfile(percorso_tipi):
        print(f"ERRORE: {percorso_tipi} non trovato")
        sys.exit(1)

    print("Caricamento dati...")
    tutti_i_pokemon = carica_pokedex(percorso_pokedex)
    tabella_tipi    = carica_tipi(percorso_tipi)
    print(f"Caricati {len(tutti_i_pokemon)} Pokemon.")

    finestra = Finestra(cart=cartella_img, cartella_dati=args.data)

    thread_logica = threading.Thread(
        target=logica_gioco,
        args=(finestra, tutti_i_pokemon, tabella_tipi),
        daemon=True
    )

    finestra.avvia(thread_logica)
    print("Arrivederci!")


if __name__ == "__main__":
    main()
