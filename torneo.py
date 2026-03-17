# -*- coding: utf-8 -*-
# torneo.py — gestione del torneo a eliminazione diretta

import random
from pokemon  import resetta_stato, assegna_pozioni_vittoria
from battaglia import combatti

DIMENSIONE_TORNEO = 16

NOMI_ROUND = {
    16: "Round of 16",
    8:  "Quarti di Finale",
    4:  "Semifinali",
    2:  "Finale",
}


def invia(finestra, messaggio):
    if finestra is not None:
        finestra.coda_comandi.put(messaggio)


def aspetta_continua(finestra):
    if finestra is None:
        return
    while True:
        msg = finestra.coda_risposte.get()
        if msg["tipo"] == "continua": return
        if msg["tipo"] == "esci":     raise SystemExit


def mostra_tabellone(finestra, bracket, nome_round, messaggio=""):
    if finestra is None:
        return
    invia(finestra, {
        "tipo":          "tabellone",
        "bracket":       bracket,
        "round_attuale": nome_round,
        "messaggio":     messaggio,
    })
    aspetta_continua(finestra)


def chiedi_difficolta(finestra, pool):
    invia(finestra, {"tipo": "difficolta", "pool": pool})
    while True:
        msg = finestra.coda_risposte.get()
        if msg["tipo"] == "difficolta": return msg["valore"]
        if msg["tipo"] == "esci":       raise SystemExit


def chiedi_pokemon(finestra, pool):
    invia(finestra, {"tipo": "selezione", "pool": pool})
    while True:
        msg = finestra.coda_risposte.get()
        if msg["tipo"] == "pokemon": return msg["valore"]
        if msg["tipo"] == "esci":    raise SystemExit


def crea_bracket(partecipanti):
    lista = partecipanti[:]
    random.shuffle(lista)
    return lista


def bracket_completo_con_placeholder(bracket):
    # Assicura sempre 4 colonne nel tabellone (R16, QF, SF, Finale)
    # Le colonne mancanti vengono riempite con match vuoti
    b = list(bracket)
    while len(b) < 1: b.append([{"a": "", "b": "", "vincitore": None} for _ in range(8)])
    while len(b) < 2: b.append([{"a": "", "b": "", "vincitore": None} for _ in range(4)])
    while len(b) < 3: b.append([{"a": "", "b": "", "vincitore": None} for _ in range(2)])
    while len(b) < 4: b.append([{"a": "", "b": "", "vincitore": None} for _ in range(1)])
    return b


def esegui_torneo(giocatore, partecipanti, tabella_tipi, difficolta, finestra=None):
    pool = partecipanti[:]
    bracket = []

    # Mostra subito il tabellone iniziale
    if finestra is not None and len(pool) > 1:
        nome_primo_round = NOMI_ROUND.get(len(pool), f"Round di {len(pool)}")
        round_iniziale = [
            {"a": pool[i]["nome"], "b": pool[i+1]["nome"], "vincitore": None}
            for i in range(0, len(pool), 2)
        ]
        mostra_tabellone(finestra, bracket_completo_con_placeholder([round_iniziale]), nome_primo_round)

    while len(pool) > 1:
        nome_round = NOMI_ROUND.get(len(pool), f"Round di {len(pool)}")

        # Creo i match del round corrente (nessun vincitore ancora)
        round_corrente = [
            {"a": pool[i]["nome"], "b": pool[i+1]["nome"], "vincitore": None}
            for i in range(0, len(pool), 2)
        ]
        bracket.append(round_corrente)

        n_match = len(pool) // 2
        vincitori = [None] * n_match  # lista ordinata: vincitori[i] = vincitore del match i

        # Trovo quale match coinvolge il giocatore
        match_giocatore = None
        for i in range(0, len(pool), 2):
            if pool[i] is giocatore or pool[i+1] is giocatore:
                match_giocatore = (i, pool[i], pool[i+1])
                break

        # Risolvo tutti i match CPU vs CPU in silenzio
        for i in range(0, len(pool), 2):
            a = pool[i]
            b = pool[i+1]
            if a is giocatore or b is giocatore:
                continue
            resetta_stato(a)
            resetta_stato(b)
            vincitore = combatti(a, b, tabella_tipi, difficolta, finestra=None)
            assegna_pozioni_vittoria(vincitore)
            vincitori[i // 2] = vincitore
            round_corrente[i // 2]["vincitore"] = vincitore["nome"]

        # Risolvo il match del giocatore con la finestra
        if match_giocatore:
            idx, a, b = match_giocatore
            avversario = b if a is giocatore else a
            pos = idx // 2

            resetta_stato(giocatore)
            resetta_stato(avversario)

            invia(finestra, {
                "tipo":       "battaglia_inizia",
                "giocatore":  giocatore,
                "avversario": avversario,
                "round":      nome_round,
            })

            mossa_ref = [None]
            vincitore = combatti(giocatore, avversario, tabella_tipi, difficolta,
                                 giocatore=giocatore, mossa_giocatore_ref=mossa_ref,
                                 finestra=finestra)

            round_corrente[pos]["vincitore"] = vincitore["nome"]
            vincitori[pos] = vincitore

            if vincitore is giocatore:
                assegna_pozioni_vittoria(giocatore)
                msg = f"{giocatore['nome']} avanza al prossimo round!"
            else:
                assegna_pozioni_vittoria(avversario)
                msg = f"Eliminato da {avversario['nome']}..."

            invia(finestra, {"tipo": "risultato", "messaggio": msg})
            aspetta_continua(finestra)

            # Tabellone aggiornato con anteprima del prossimo round
            if len(vincitori) > 1:
                prossimo_round = [
                    {"a": vincitori[i]["nome"], "b": vincitori[i+1]["nome"], "vincitore": None}
                    for i in range(0, len(vincitori), 2)
                ]
                bracket_da_mostrare = list(bracket) + [prossimo_round]
            else:
                bracket_da_mostrare = list(bracket)

            mostra_tabellone(finestra, bracket_completo_con_placeholder(bracket_da_mostrare), nome_round, msg)

            if vincitore is not giocatore:
                return False

        pool = vincitori

    # Il giocatore ha vinto il torneo
    campione = pool[0]
    invia(finestra, {"tipo": "campione", "messaggio": campione["nome"]})
    aspetta_continua(finestra)
    return True
