"""
Le 4 mosse sono fisse per tutti i pokemon:
  0 - Attacco          (fisico:  ATK attaccante - DEF difensore,  no tipo)
  1 - Difesa           (scudo:   assorbe danno fisico per il turno)
  2 - Attacco Speciale (speciale: SP_ATK * molt_tipo - SP_DEF difensore)
  3 - Difesa Speciale  (scudo:   assorbe danno speciale per il turno)

La potenza non è un numero fisso: dipende dalle stat di chi attacca e chi difende.
move.power = 0 per le difese (nessun danno), altrimenti è la stat base per riferimento nell'UI.
"""

class Move:
    def __init__(self, label, power, move_type, attack_type="Normal"):
        self.name        = label       # "Attacco", "Difesa", "Attacco Speciale", "Difesa Speciale"
        self.power       = power       # stat di riferimento (usata solo nell'UI come indicatore)
        self.move_type   = move_type   # "physical" | "special" | "defense" | "sp_defense"
        self.attack_type = attack_type # tipo del pokemon (es. "Fire") — usato solo per Attacco Speciale

    def __repr__(self):
        return f"Move({self.name}, pwr={self.power}, {self.move_type}, {self.attack_type})"


class Pokemon:
    def __init__(self, data):
        self.id         = data["id"]
        self.name       = data["name"]["english"]
        self.types      = data["type"]
        base            = data["base"]
        self.max_hp     = base["HP"]
        self.hp         = base["HP"]
        self.attack     = base["Attack"]
        self.defense    = base["Defense"]
        self.sp_attack  = base["Sp. Attack"]
        self.sp_defense = base["Sp. Defense"]
        self.speed      = base["Speed"]
        self.sprite     = None  # caricato da assets

        self.moves = self._generate_moves()

    def _generate_moves(self):
        primary_type = self.types[0]
        return [
            # Attacco fisico: power = ATK (indicativo per l'UI)
            Move("Attacco",          self.attack,    "physical",   primary_type),
            # Difesa (scudo turno): power = 0
            Move("Difesa",           0,              "defense",    "Normal"),
            # Attacco speciale: power = SP_ATK (indicativo per l'UI)
            Move("Attacco Speciale", self.sp_attack, "special",    primary_type),
            # Difesa speciale (scudo turno): power = 0
            Move("Difesa Speciale",  0,              "sp_defense", "Normal"),
        ]

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

    def total_stats(self):
        return self.max_hp + self.attack + self.defense + self.sp_attack + self.sp_defense + self.speed

    def reset_battle(self):
        self.hp = self.max_hp

    def hp_percent(self):
        return self.hp / self.max_hp