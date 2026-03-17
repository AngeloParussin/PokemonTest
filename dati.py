# -*- coding: utf-8 -*-
# dati.py — legge i file JSON e crea le liste di Pokemon e tipi

import json


def carica_pokedex(percorso_file):
    # Legge pokedex.json e restituisce una lista di dizionari Pokemon
    with open(percorso_file, "r", encoding="utf-8") as f:
        dati_raw = json.load(f)

    lista_pokemon = []

    for voce in dati_raw:
        # Leggo il nome (può essere {"english": "Bulbasaur"} oppure "Bulbasaur")
        nome_raw = voce.get("name", "Sconosciuto")
        if isinstance(nome_raw, dict):
            nome = nome_raw.get("english", nome_raw.get("japanese", "Sconosciuto"))
        else:
            nome = str(nome_raw)

        # Leggo i tipi (può essere ["Grass", "Poison"] oppure "Grass")
        tipi_raw = voce.get("type") or voce.get("types") or ["Normal"]
        if isinstance(tipi_raw, str):
            tipi_raw = [tipi_raw]
        tipi = [t.capitalize() for t in tipi_raw]

        # Leggo le statistiche base
        stats_raw = voce.get("base", voce)
        stats = {
            "hp":         int(stats_raw.get("HP",          stats_raw.get("hp",          45))),
            "attack":     int(stats_raw.get("Attack",      stats_raw.get("attack",      50))),
            "defense":    int(stats_raw.get("Defense",     stats_raw.get("defense",     50))),
            "sp_attack":  int(stats_raw.get("Sp. Attack",  stats_raw.get("sp_attack",   50))),
            "sp_defense": int(stats_raw.get("Sp. Defense", stats_raw.get("sp_defense",  50))),
            "speed":      int(stats_raw.get("Speed",       stats_raw.get("speed",       50))),
        }

        pokemon = {
            "nome":              nome,
            "tipi":              tipi,
            "stats":             stats,
            "hp_attuale":        float(stats["hp"]),
            "difesa_attuale":    float(stats["defense"]),
            "sp_difesa_attuale": float(stats["sp_defense"]),
            "pozioni_normali":   1,
            "pozioni_speciali":  1,
        }
        lista_pokemon.append(pokemon)

    return lista_pokemon


def carica_tipi(percorso_file):
    # Legge types.json e restituisce un dizionario: tabella[attaccante][difensore] = moltiplicatore
    with open(percorso_file, "r", encoding="utf-8") as f:
        dati_raw = json.load(f)

    tabella = {}

    for voce in dati_raw:
        tipo_attaccante = voce.get("english", "").capitalize()
        if not tipo_attaccante:
            continue

        matchup = {}
        for t in voce.get("effective",   []): matchup[t.capitalize()] = 2.0
        for t in voce.get("ineffective", []): matchup[t.capitalize()] = 0.5
        for t in voce.get("no_effect",   []): matchup[t.capitalize()] = 0.0

        tabella[tipo_attaccante] = matchup

    return tabella
