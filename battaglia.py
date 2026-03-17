# -*- coding: utf-8 -*-
# battaglia.py — motore di battaglia Pokemon

import time
from danno   import applica_danno_fisico, applica_danno_speciale
from danno   import applica_pozione_normale, applica_pozione_speciale
from pokemon import e_svenuto
from ai      import scegli_mossa_cpu

TURNI_MASSIMI = 200

# Colori per i messaggi nel log
COLORE_GIOCATORE = (234, 234, 234)   # bianco
COLORE_CPU       = (176, 158, 220)   # viola chiaro
COLORE_SISTEMA   = (115,  98, 138)   # grigio viola
COLORE_HP        = ( 82, 196,  26)   # verde
COLORE_DEF       = (100, 180, 255)   # azzurro
COLORE_SPD       = (176, 106, 255)   # viola


# ---------------------------------------------------------------
# FUNZIONI PER INVIARE MESSAGGI ALLA FINESTRA
# ---------------------------------------------------------------

def manda(finestra, messaggio):
    if finestra is not None:
        finestra.coda_comandi.put(messaggio)

def log(finestra, testo, colore):
    if finestra is not None:
        finestra.coda_comandi.put({"tipo": "log", "testo": testo, "colore": colore})
    else:
        print(f"  {testo}")

def aggiorna_barre(finestra, giocatore, avversario):
    manda(finestra, {"tipo": "aggiorna", "giocatore": giocatore, "avversario": avversario})

def anima_attacco(finestra, chi, valori):
    manda(finestra, {"tipo": "anim_attacco", "chi": chi, "valori": valori})

def anima_attacco_doppio(finestra, valori_gio, valori_avv):
    manda(finestra, {"tipo": "anim_attacco_doppio", "valori_gio": valori_gio, "valori_avv": valori_avv})

def anima_cura(finestra, chi, valori, tipo_pozione="normale"):
    manda(finestra, {"tipo": "anim_cura", "chi": chi, "valori": valori, "tipo_pozione": tipo_pozione})

def anima_speciale(finestra, chi, moltiplicatore):
    manda(finestra, {"tipo": "anim_speciale", "chi": chi, "moltiplicatore": moltiplicatore})

def anima_ko(finestra, chi):
    manda(finestra, {"tipo": "anim_ko", "chi": chi})

def pausa():
    time.sleep(0.4)

def colore_efficacia(moltiplicatore):
    # Colore del log in base a quanto è efficace l'attacco speciale
    if moltiplicatore > 1:   return (255, 215,   0)  # oro
    elif moltiplicatore == 0: return ( 99, 110, 114)  # grigio
    elif moltiplicatore < 1:  return (116, 185, 255)  # azzurro
    else:                     return (200, 200, 200)  # bianco tenue


def chiedi_mossa(finestra, giocatore):
    # Chiede al giocatore quale mossa usare (aspetta il click)
    if finestra is not None:
        manda(finestra, {"tipo": "chiedi_mossa", "giocatore": giocatore})
        while True:
            r = finestra.coda_risposte.get()
            if r["tipo"] == "mossa": return r["valore"]
            if r["tipo"] == "esci":  raise SystemExit
    else:
        print(f"\n  {giocatore['nome']} HP:{giocatore['hp_attuale']:.0f}")
        print("  1)Attacco  2)Att.Spec  3)Pozione  4)Poz.Spec")
        mappa = {"1":"attacco","2":"attacco_speciale","3":"pozione_normale","4":"pozione_speciale"}
        while True:
            try:    s = input("  Scelta: ").strip()
            except: return "attacco"
            if s in mappa: return mappa[s]


# ---------------------------------------------------------------
# CALCOLA, APPLICA E DESCRIVI OGNI AZIONE
# ---------------------------------------------------------------

def esegui_attacco_fisico(attore, bersaglio):
    # Applica il danno fisico e restituisce testo, valori animazione, risultato
    r = applica_danno_fisico(attore, bersaglio)
    parti = []
    if r["danno_hp"]     > 0: parti.append(f"-{r['danno_hp']:.0f} HP")
    if r["danno_difesa"] > 0: parti.append(f"-{r['danno_difesa']:.0f} DEF")
    testo = f"{attore['nome']} attacca {bersaglio['nome']}! ({', '.join(parti) or 'nessun danno'})"
    valori_anim = []
    if r["danno_hp"]     > 0: valori_anim.append((f"-{r['danno_hp']:.0f}",      COLORE_HP))
    if r["danno_difesa"] > 0: valori_anim.append((f"-{r['danno_difesa']:.0f} DEF", COLORE_DEF))
    return r, valori_anim, testo


def esegui_attacco_speciale(attore, bersaglio, tabella_tipi):
    # Applica il danno speciale e restituisce testo, valori animazione, risultato, moltiplicatore
    r = applica_danno_speciale(attore, bersaglio, tabella_tipi)
    m = r["moltiplicatore"]
    if   m > 1:  eff = f"super efficace x{m:.1f}!"
    elif m == 0: eff = "nessun effetto"
    elif m < 1:  eff = f"poco efficace x{m:.1f}"
    else:        eff = "efficacia normale"
    parti = []
    if r["danno_hp"]    > 0: parti.append(f"-{r['danno_hp']:.0f} HP")
    if r["danno_spdef"] > 0: parti.append(f"-{r['danno_spdef']:.0f} SpD")
    testo = f"{attore['nome']} att. speciale! {eff} ({', '.join(parti) or 'nessun danno'})"
    valori_anim = []
    if r["danno_hp"]    > 0: valori_anim.append((f"-{r['danno_hp']:.0f}",      COLORE_HP))
    if r["danno_spdef"] > 0: valori_anim.append((f"-{r['danno_spdef']:.0f} SpD", COLORE_SPD))
    return r, valori_anim, testo, m


def esegui_pozione_normale(attore):
    # Applica la pozione normale e restituisce testo e valori animazione
    r = applica_pozione_normale(attore)
    parti = [f"+{r['hp_ripristinati']:.0f} HP"]
    if r["bonus_difesa"] > 0: parti.append(f"+{r['bonus_difesa']:.0f} DEF")
    testo = f"{attore['nome']} usa pozione! ({', '.join(parti)})"
    valori_anim = [(f"+{r['hp_ripristinati']:.0f} HP", COLORE_HP)]
    if r["bonus_difesa"] > 0: valori_anim.append((f"+{r['bonus_difesa']:.0f} DEF", COLORE_DEF))
    return r, valori_anim, testo


def esegui_pozione_speciale(attore):
    # Applica la pozione speciale e restituisce testo e valori animazione
    r = applica_pozione_speciale(attore)
    parti = [f"+{r['hp_ripristinati']:.0f} HP"]
    if r["bonus_spdef"] > 0: parti.append(f"+{r['bonus_spdef']:.0f} SpD")
    testo = f"{attore['nome']} usa poz. speciale! ({', '.join(parti)})"
    valori_anim = [(f"+{r['hp_ripristinati']:.0f} HP", COLORE_HP)]
    if r["bonus_spdef"] > 0: valori_anim.append((f"+{r['bonus_spdef']:.0f} SpD", COLORE_SPD))
    return r, valori_anim, testo


def applica_cura(finestra, chi_cura, mossa_cura, chi_e_lui):
    # Applica la pozione scelta e restituisce il testo (o None se non ha pozioni)
    if mossa_cura == "pozione_normale" and chi_cura["pozioni_normali"] > 0:
        _, valori, testo = esegui_pozione_normale(chi_cura)
        anima_cura(finestra, chi_e_lui, valori, "normale")
        return testo
    elif mossa_cura == "pozione_speciale" and chi_cura["pozioni_speciali"] > 0:
        _, valori, testo = esegui_pozione_speciale(chi_cura)
        anima_cura(finestra, chi_e_lui, valori, "speciale")
        return testo
    else:
        log(finestra, f"{chi_cura['nome']} non ha piu' pozioni!", COLORE_SISTEMA)
        return None


def applica_attacco(finestra, chi_attacca, bersaglio, mossa, tabella_tipi, chi_e_lui):
    # Applica l'attacco scelto e restituisce testo e colore log
    if mossa == "attacco":
        _, valori, testo = esegui_attacco_fisico(chi_attacca, bersaglio)
        anima_attacco(finestra, chi_e_lui, valori)
        return testo, COLORE_GIOCATORE  # colore verrà sovrascritto dal chiamante
    else:
        _, valori, testo, mult = esegui_attacco_speciale(chi_attacca, bersaglio, tabella_tipi)
        anima_speciale(finestra, chi_e_lui, mult)
        anima_attacco(finestra, chi_e_lui, valori)
        return testo, colore_efficacia(mult)


# ---------------------------------------------------------------
# MOTORE DI BATTAGLIA
# ---------------------------------------------------------------

def combatti(pokemon_a, pokemon_b, tabella_tipi, difficolta,
             giocatore=None, mossa_giocatore_ref=None, finestra=None):
    # Ordina per velocità: il più veloce agisce per primo
    if pokemon_a["stats"]["speed"] >= pokemon_b["stats"]["speed"]:
        primo, secondo = pokemon_a, pokemon_b
    else:
        primo, secondo = pokemon_b, pokemon_a

    primo_e_giocatore   = (giocatore is not None and primo  is giocatore)
    secondo_e_giocatore = (giocatore is not None and secondo is giocatore)

    # Riferimenti fissi per aggiornare le barre
    gio_ref = giocatore if giocatore else pokemon_a
    avv_ref = (pokemon_b if giocatore is pokemon_a else pokemon_a) if giocatore else pokemon_b

    def lato(pokemon):
        # Restituisce "giocatore" o "avversario" per le animazioni
        if giocatore is None:
            return "giocatore" if pokemon is pokemon_a else "avversario"
        return "giocatore" if pokemon is giocatore else "avversario"

    log(finestra, f"{primo['nome']} e' piu' veloce di {secondo['nome']}!", COLORE_SISTEMA)

    turno = 0

    while not e_svenuto(pokemon_a) and not e_svenuto(pokemon_b):

        if turno >= TURNI_MASSIMI:
            log(finestra, f"Limite di {TURNI_MASSIMI} turni raggiunto!", COLORE_SISTEMA)
            break

        turno += 1
        log(finestra, f"-- Turno {turno} --", COLORE_SISTEMA)

        # Raccolta mosse
        if primo_e_giocatore:
            mossa_primo = chiedi_mossa(finestra, primo)
            mossa_giocatore_corrente = mossa_primo
        elif secondo_e_giocatore:
            mossa_secondo = chiedi_mossa(finestra, secondo)
            mossa_giocatore_corrente = mossa_secondo
        else:
            mossa_giocatore_corrente = None

        if mossa_giocatore_ref is not None:
            mossa_giocatore_ref[0] = mossa_giocatore_corrente

        if not primo_e_giocatore:
            mossa_primo = scegli_mossa_cpu(primo, secondo, tabella_tipi, difficolta, mossa_giocatore_corrente)

        if not secondo_e_giocatore:
            mossa_secondo = scegli_mossa_cpu(secondo, primo, tabella_tipi, difficolta, mossa_giocatore_corrente)

        mosse_cura = ("pozione_normale", "pozione_speciale")
        primo_cura  = mossa_primo  in mosse_cura
        secondo_cura = mossa_secondo in mosse_cura

        col_primo  = COLORE_GIOCATORE if primo_e_giocatore  else COLORE_CPU
        col_second = COLORE_GIOCATORE if secondo_e_giocatore else COLORE_CPU

        # CASO 1: entrambi attaccano — azioni simultanee
        if not primo_cura and not secondo_cura:

            if mossa_primo == "attacco":
                _, v_p, t_p = esegui_attacco_fisico(primo, secondo)
                c_p = col_primo
            else:
                _, v_p, t_p, mult_p = esegui_attacco_speciale(primo, secondo, tabella_tipi)
                c_p = colore_efficacia(mult_p)
                anima_speciale(finestra, lato(primo), mult_p)

            if mossa_secondo == "attacco":
                _, v_s, t_s = esegui_attacco_fisico(secondo, primo)
                c_s = col_second
            else:
                _, v_s, t_s, mult_s = esegui_attacco_speciale(secondo, primo, tabella_tipi)
                c_s = colore_efficacia(mult_s)
                anima_speciale(finestra, lato(secondo), mult_s)

            log(finestra, t_p, c_p)
            log(finestra, t_s, c_s)

            # Animazione doppia: entrambi si lanciano verso l'avversario
            v_gio = v_p if primo_e_giocatore else v_s
            v_avv = v_s if primo_e_giocatore else v_p
            if giocatore is None:
                v_gio = v_p
                v_avv = v_s
            anima_attacco_doppio(finestra, v_gio, v_avv)
            aggiorna_barre(finestra, gio_ref, avv_ref)
            if finestra: pausa()

            # Controllo KO
            a_ko = e_svenuto(pokemon_a)
            b_ko = e_svenuto(pokemon_b)
            if a_ko and b_ko:
                log(finestra, f"Doppio KO! {secondo['nome']} si dissolve.", COLORE_SISTEMA)
                anima_ko(finestra, lato(secondo))
                if finestra: pausa()
                break
            elif a_ko:
                log(finestra, f"{pokemon_a['nome']} e' stato sconfitto!", COLORE_SISTEMA)
                anima_ko(finestra, lato(pokemon_a))
                if finestra: pausa()
                break
            elif b_ko:
                log(finestra, f"{pokemon_b['nome']} e' stato sconfitto!", COLORE_SISTEMA)
                anima_ko(finestra, lato(pokemon_b))
                if finestra: pausa()
                break

        # CASO 2: entrambi si curano — azioni simultanee
        elif primo_cura and secondo_cura:
            t_p = applica_cura(finestra, primo,  mossa_primo,  lato(primo))
            t_s = applica_cura(finestra, secondo, mossa_secondo, lato(secondo))
            if t_p: log(finestra, t_p, col_primo)
            if t_s: log(finestra, t_s, col_second)
            aggiorna_barre(finestra, gio_ref, avv_ref)
            if finestra: pausa()

        # CASO 3: uno attacca, l'altro si cura — azioni simultanee
        # La cura avviene prima: gli HP tornano su, poi l'attacco colpisce
        else:
            if primo_cura:
                chi_cura, mossa_c, chi_att, mossa_a = primo, mossa_primo, secondo, mossa_secondo
                col_cura, col_att = col_primo, col_second
            else:
                chi_cura, mossa_c, chi_att, mossa_a = secondo, mossa_secondo, primo, mossa_primo
                col_cura, col_att = col_second, col_primo

            testo_cura = applica_cura(finestra, chi_cura, mossa_c, lato(chi_cura))
            testo_att, col_att_log = applica_attacco(finestra, chi_att, chi_cura, mossa_a, tabella_tipi, lato(chi_att))

            if testo_cura: log(finestra, testo_cura, col_cura)
            log(finestra, testo_att, col_att_log)
            aggiorna_barre(finestra, gio_ref, avv_ref)
            if finestra: pausa()

            if e_svenuto(chi_cura):
                log(finestra, f"{chi_cura['nome']} e' stato sconfitto!", COLORE_SISTEMA)
                anima_ko(finestra, lato(chi_cura))
                if finestra: pausa()
                break

    # Determina il vincitore
    if   not e_svenuto(pokemon_a) and     e_svenuto(pokemon_b): vincitore = pokemon_a
    elif     e_svenuto(pokemon_a) and not e_svenuto(pokemon_b): vincitore = pokemon_b
    elif     e_svenuto(pokemon_a) and     e_svenuto(pokemon_b): vincitore = primo  # più veloce sopravvive
    else:
        vincitore = pokemon_a if pokemon_a["hp_attuale"] >= pokemon_b["hp_attuale"] else pokemon_b

    log(finestra, f"{vincitore['nome']} vince dopo {turno} turni!", COLORE_GIOCATORE)
    return vincitore
