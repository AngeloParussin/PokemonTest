# -*- coding: utf-8 -*-
# danno.py — calcola e applica danni e cure in battaglia

# ---------------------------------------------------------------
# MOLTIPLICATORE DI TIPO
# ---------------------------------------------------------------

def calcola_moltiplicatore(tipi_attaccante, tipi_difensore, tabella_tipi):
    # Usa solo il tipo primario dell'attaccante
    tipo_mossa = tipi_attaccante[0] if tipi_attaccante else "Normal"

    mult = 1.0
    for tipo_difensore in tipi_difensore:
        riga = tabella_tipi.get(tipo_mossa, {})
        mult = mult * riga.get(tipo_difensore, 1.0)

    # Limita ai valori ufficiali: 0, 0.5, 1.0, 2.0
    if mult == 0.0:
        return 0.0
    elif mult < 1.0:
        return 0.5
    elif mult > 1.0:
        return 2.0
    else:
        return 1.0


# ---------------------------------------------------------------
# CALCOLO DANNI (solo matematica, non cambiano lo stato)
# ---------------------------------------------------------------

def calcola_danno_fisico(attaccante, difensore):
    # Il danno è uguale all'ATK dell'attaccante
    # Colpisce prima la difesa, l'eccesso va agli HP
    danno = float(attaccante["stats"]["attack"])
    assorbito = min(difensore["difesa_attuale"], danno)
    danno_hp = danno - assorbito
    return {
        "danno_difesa":   assorbito,
        "danno_hp":       danno_hp,
        "danno_totale":   danno,
        "moltiplicatore": 1.0,
    }


def calcola_danno_speciale(attaccante, difensore, tabella_tipi):
    # Il danno è SpATK moltiplicato per l'efficacia del tipo
    # Colpisce prima la sp.difesa, l'eccesso va agli HP
    mult = calcola_moltiplicatore(attaccante["tipi"], difensore["tipi"], tabella_tipi)
    danno = float(attaccante["stats"]["sp_attack"]) * mult
    assorbito = min(difensore["sp_difesa_attuale"], danno)
    danno_hp = danno - assorbito
    return {
        "danno_spdef":    assorbito,
        "danno_hp":       danno_hp,
        "danno_totale":   danno,
        "moltiplicatore": mult,
    }


# ---------------------------------------------------------------
# CALCOLO CURE (solo matematica, non cambiano lo stato)
# ---------------------------------------------------------------

def calcola_pozione_normale(pokemon):
    # Ripristina il 100% degli HP. Se gli HP sono già pieni, l'eccesso va in difesa.
    hp_max = pokemon["stats"]["hp"]
    hp_mancanti = hp_max - pokemon["hp_attuale"]
    hp_curati = min(hp_max, hp_mancanti)
    eccesso = hp_max - hp_curati  # va in difesa
    return {"hp_ripristinati": hp_curati, "bonus_difesa": eccesso}


def calcola_pozione_speciale(pokemon):
    # Ripristina il 100% degli HP. Se gli HP sono già pieni, l'eccesso va in sp.difesa.
    hp_max = pokemon["stats"]["hp"]
    hp_mancanti = hp_max - pokemon["hp_attuale"]
    hp_curati = min(hp_max, hp_mancanti)
    eccesso = hp_max - hp_curati  # va in sp.difesa
    return {"hp_ripristinati": hp_curati, "bonus_spdef": eccesso}


# ---------------------------------------------------------------
# APPLICAZIONE (modificano davvero lo stato del Pokemon)
# ---------------------------------------------------------------

def applica_danno_fisico(attaccante, difensore):
    r = calcola_danno_fisico(attaccante, difensore)
    difensore["difesa_attuale"] = max(0.0, difensore["difesa_attuale"] - r["danno_difesa"])
    difensore["hp_attuale"]     = max(0.0, difensore["hp_attuale"]     - r["danno_hp"])
    return r


def applica_danno_speciale(attaccante, difensore, tabella_tipi):
    r = calcola_danno_speciale(attaccante, difensore, tabella_tipi)
    difensore["sp_difesa_attuale"] = max(0.0, difensore["sp_difesa_attuale"] - r["danno_spdef"])
    difensore["hp_attuale"]        = max(0.0, difensore["hp_attuale"]        - r["danno_hp"])
    return r


def applica_pozione_normale(pokemon):
    if pokemon["pozioni_normali"] <= 0:
        raise ValueError(f"{pokemon['nome']} non ha pozioni normali!")
    r = calcola_pozione_normale(pokemon)
    pokemon["hp_attuale"]      = pokemon["hp_attuale"]      + r["hp_ripristinati"]
    pokemon["difesa_attuale"]  = pokemon["difesa_attuale"]  + r["bonus_difesa"]
    pokemon["pozioni_normali"] = pokemon["pozioni_normali"] - 1
    return r


def applica_pozione_speciale(pokemon):
    if pokemon["pozioni_speciali"] <= 0:
        raise ValueError(f"{pokemon['nome']} non ha pozioni speciali!")
    r = calcola_pozione_speciale(pokemon)
    pokemon["hp_attuale"]         = pokemon["hp_attuale"]         + r["hp_ripristinati"]
    pokemon["sp_difesa_attuale"]  = pokemon["sp_difesa_attuale"]  + r["bonus_spdef"]
    pokemon["pozioni_speciali"]   = pokemon["pozioni_speciali"]   - 1
    return r
