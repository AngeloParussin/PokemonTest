TYPE_CHART = {
    "Normal": {
        "Rock": 0.5, "Ghost": 0, "Steel": 0.5
    },
    "Fire": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2
    },
    "Water": {
        "Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5
    },
    "Grass": {
        "Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5
    },
    "Electric": {
        "Water": 2, "Grass": 0.5, "Electric": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5
    },
    "Ice": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5
    },
    "Fighting": {
        "Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0, "Dark": 2, "Steel": 2, "Fairy": 0.5
    },
    "Poison": {
        "Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2
    },
    "Ground": {
        "Fire": 2, "Grass": 0.5, "Electric": 2, "Poison": 2, "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2
    },
    "Flying": {
        "Grass": 2, "Electric": 0.5, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5
    },
    "Psychic": {
        "Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0, "Steel": 0.5
    },
    "Bug": {
        "Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Dark": 2, "Steel": 0.5, "Fairy": 0.5
    },
    "Rock": {
        "Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Bug": 2, "Steel": 0.5
    },
    "Ghost": {
        "Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5
    },
    "Dragon": {
        "Dragon": 2, "Steel": 0.5, "Fairy": 0
    },
    "Dark": {
        "Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5, "Fairy": 0.5
    },
    "Steel": {
        "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2, "Rock": 2, "Steel": 0.5, "Fairy": 2
    },
    "Fairy": {
        "Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2, "Dark": 2, "Steel": 0.5
    },
}


def get_type_multiplier(attack_type, defender_types):
    multiplier = 1.0
    chart = TYPE_CHART.get(attack_type, {})
    for def_type in defender_types:
        multiplier *= chart.get(def_type, 1.0)
    return multiplier


def get_effectiveness_text(multiplier):
    if multiplier == 0:
        return "It had no effect!"
    elif multiplier >= 2:
        return "It's super effective!"
    elif multiplier <= 0.5:
        return "It's not very effective..."
    return ""
