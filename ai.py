# -*- coding: utf-8 -*-
# ai.py — intelligenza artificiale della CPU

import random
from danno import calcola_danno_fisico, calcola_danno_speciale

SOGLIA_CURA = 0.35  # percentuale HP sotto cui la CPU media si cura


def attacco_migliore(cpu, avversario, tabella_tipi):
    # Restituisce l'attacco (fisico o speciale) che fa più danno
    danno_fisico   = calcola_danno_fisico(cpu, avversario)["danno_totale"]
    danno_speciale = calcola_danno_speciale(cpu, avversario, tabella_tipi)["danno_totale"]
    if danno_speciale >= danno_fisico:
        return "attacco_speciale"
    return "attacco"


def danno_subito_dagli_hp(cpu, avversario, tabella_tipi):
    # Stima il danno massimo agli HP che la CPU subirebbe dal prossimo attacco avversario
    danno_fis = calcola_danno_fisico(avversario, cpu)["danno_hp"]
    danno_spe = calcola_danno_speciale(avversario, cpu, tabella_tipi)["danno_hp"]
    return max(danno_fis, danno_spe)


# ---------------------------------------------------------------
# FACILE: sceglie a caso
# ---------------------------------------------------------------

def mossa_cpu_facile(cpu, avversario, tabella_tipi):
    scelte = ["attacco", "attacco_speciale"]
    if cpu["pozioni_normali"]  > 0: scelte.append("pozione_normale")
    if cpu["pozioni_speciali"] > 0: scelte.append("pozione_speciale")
    return random.choice(scelte)


# ---------------------------------------------------------------
# MEDIA: ragiona su danno e cura
# ---------------------------------------------------------------

def mossa_cpu_media(cpu, avversario, tabella_tipi):
    danno_mio    = max(calcola_danno_fisico(cpu, avversario)["danno_totale"],
                       calcola_danno_speciale(cpu, avversario, tabella_tipi)["danno_totale"])
    danno_subito = danno_subito_dagli_hp(cpu, avversario, tabella_tipi)
    piu_veloce   = cpu["stats"]["speed"] >= avversario["stats"]["speed"]

    # Posso ucciderlo: attacca sempre
    if danno_mio >= avversario["hp_attuale"]:
        return attacco_migliore(cpu, avversario, tabella_tipi)

    # L'avversario mi uccide prima che io possa fare qualcosa: attacca
    if danno_subito >= cpu["hp_attuale"]:
        return attacco_migliore(cpu, avversario, tabella_tipi)

    # HP bassi ma sopravviverò al prossimo colpo: mi curo
    percentuale_hp = cpu["hp_attuale"] / cpu["stats"]["hp"]
    if percentuale_hp < SOGLIA_CURA:
        if cpu["pozioni_normali"]  > 0: return "pozione_normale"
        if cpu["pozioni_speciali"] > 0: return "pozione_speciale"

    return attacco_migliore(cpu, avversario, tabella_tipi)


# ---------------------------------------------------------------
# DIFFICILE: conosce la mossa del giocatore e sceglie la risposta migliore
# ---------------------------------------------------------------

def mossa_cpu_difficile(cpu, avversario, tabella_tipi, mossa_giocatore=None):
    piu_veloce     = cpu["stats"]["speed"] >= avversario["stats"]["speed"]
    giocatore_cura = mossa_giocatore in ("pozione_normale", "pozione_speciale")

    # Se il giocatore si cura, non mi attacca: danno subito = 0 (turno gratuito)
    if giocatore_cura:
        danno_dal_giocatore = 0.0
    else:
        danno_dal_giocatore = danno_subito_dagli_hp(cpu, avversario, tabella_tipi)

    def punteggio(mossa):
        # Pozioni esaurite: non usabili
        if mossa == "pozione_normale"  and cpu["pozioni_normali"]  <= 0: return -99999
        if mossa == "pozione_speciale" and cpu["pozioni_speciali"] <= 0: return -99999

        if mossa == "attacco":
            danno = calcola_danno_fisico(cpu, avversario)["danno_totale"]
            # Se sono più veloce e uccido, il giocatore non attacca più
            danno_subito = 0.0 if (piu_veloce and danno >= avversario["hp_attuale"]) else danno_dal_giocatore
            return danno - danno_subito

        if mossa == "attacco_speciale":
            danno = calcola_danno_speciale(cpu, avversario, tabella_tipi)["danno_totale"]
            danno_subito = 0.0 if (piu_veloce and danno >= avversario["hp_attuale"]) else danno_dal_giocatore
            return danno - danno_subito

        if mossa == "pozione_normale" or mossa == "pozione_speciale":
            hp_curati = cpu["stats"]["hp"]  # cura al 100%
            hp_dopo_cura = min(cpu["hp_attuale"] + hp_curati, cpu["stats"]["hp"])
            # Se il giocatore mi uccide comunque dopo la cura, è inutile
            if danno_dal_giocatore >= hp_dopo_cura:
                return -99998
            return hp_curati - danno_dal_giocatore

        return 0.0

    mosse = ["attacco", "attacco_speciale", "pozione_normale", "pozione_speciale"]
    return max(mosse, key=punteggio)


# ---------------------------------------------------------------
# FUNZIONE PRINCIPALE
# ---------------------------------------------------------------

def scegli_mossa_cpu(cpu, avversario, tabella_tipi, difficolta, mossa_giocatore=None):
    if difficolta == "facile":
        return mossa_cpu_facile(cpu, avversario, tabella_tipi)
    elif difficolta == "media":
        return mossa_cpu_media(cpu, avversario, tabella_tipi)
    else:  # difficile
        return mossa_cpu_difficile(cpu, avversario, tabella_tipi, mossa_giocatore)
