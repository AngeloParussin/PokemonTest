# -*- coding: utf-8 -*-
# pokemon.py — funzioni sullo stato di battaglia di un Pokemon

def resetta_stato(pokemon):
    # Riporta HP, Difesa e Sp.Difesa ai valori base prima di ogni scontro
    pokemon["hp_attuale"]        = float(pokemon["stats"]["hp"])
    pokemon["difesa_attuale"]    = float(pokemon["stats"]["defense"])
    pokemon["sp_difesa_attuale"] = float(pokemon["stats"]["sp_defense"])


def assegna_pozioni_vittoria(pokemon):
    # Dopo aver vinto uno scontro, il Pokemon riceve +1 pozione per tipo
    pokemon["pozioni_normali"]  = pokemon["pozioni_normali"]  + 1
    pokemon["pozioni_speciali"] = pokemon["pozioni_speciali"] + 1


def e_svenuto(pokemon):
    # Restituisce True se il Pokemon non ha più HP
    return pokemon["hp_attuale"] <= 0
