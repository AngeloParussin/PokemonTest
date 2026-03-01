You are a senior Python game developer specialized in retro-style games and structured software architecture.

Your task is to create a COMPLETE, FULLY WORKING Pokémon tournament game in Python.

IMPORTANT RULES — YOU MUST FOLLOW THEM STRICTLY:

1. DO NOT invent gameplay mechanics.
2. DO NOT simplify logic.
3. DO NOT change rules.
4. FOLLOW EXACTLY the game design described in the attached .docx file.
5. If something is not specified, implement it using classic GameBoy Pokémon behavior ONLY.
6. Produce clean, modular, professional code.
7. The final result must RUN immediately after execution.

----------------------------------------------------
GAME OVERVIEW
----------------------------------------------------

Create a retro Pokémon-style tournament game with:

• Total Pokémon in tournament: 16  
• Player controls: 1 Pokémon  
• Remaining Pokémon controlled by CPU  
• Classic turn-based combat system  
• Retro GameBoy visual style

The game must include:

- Full battle logic
- GUI graphics
- Tournament progression
- AI opponents
- Type effectiveness system
- Pokémon stats handling

----------------------------------------------------
TECHNICAL REQUIREMENTS
----------------------------------------------------

Language:
Python 3

Libraries:
Use ONLY:
- pygame (graphics & input)
- json
- random
- math
- os

NO external engines.

Structure the project cleanly:

/main.py
/game/
    battle.py
    pokemon.py
    ai.py
    tournament.py
    ui.py
    assets.py

----------------------------------------------------
DATA SOURCES (MANDATORY)
----------------------------------------------------

Pokédex file:
C:\Users\Angelo\Documents\pokemon\pokedex.json

This file contains ALL Pokémon statistics.
You MUST load stats dynamically from this file.

exemple of the pokedex:
{
    "id": 1,
    "name": {
      "english": "Bulbasaur",
      "japanese": "フシギダネ",
      "chinese": "妙蛙种子",
      "french": "Bulbizarre"
    },
    "type": [
      "Grass",
      "Poison"
    ],
    "base": {
      "HP": 45,
      "Attack": 49,
      "Defense": 49,
      "Sp. Attack": 65,
      "Sp. Defense": 65,
      "Speed": 45
    }
  },

Pokémon images folder:
C:\Users\Angelo\Documents\pokemon\pokemon_images

Each Pokémon must load its sprite automatically.

DO NOT hardcode Pokémon stats.

----------------------------------------------------
POKÉMON STAT SYSTEM
----------------------------------------------------

Use stats from pokedex.json:

HP  
Attack  
Defense  
Sp. Attack  
Sp. Defense  
Speed  
Type(s)

Damage calculations must depend on these values.

----------------------------------------------------
TYPE EFFECTIVENESS
----------------------------------------------------

Use the type multiplier chart provided in the attached image.

Implement:
- 2x effectiveness
- 0.5x resistance
- 0x immunity
- 1x normal

Create a TYPE_CHART dictionary reproducing EXACTLY that table.

Special attacks must depend on Pokémon types and multipliers.

----------------------------------------------------
DIFFICULTY SYSTEM (MANDATORY)
----------------------------------------------------

Implement EXACTLY the rules defined in the .docx:

--------------------------------
EASY MODE
--------------------------------
CPU behavior:
- Selects random Pokémon from pool
- Uses completely random moves
- No strategic thinking

--------------------------------
NORMAL MODE
--------------------------------
CPU Pokémon selection:
- Compute total stat sum:
HP + Attack + Defense + Sp.Atk + Sp.Def + Speed
- Select Pokémon with highest total stats

Battle behavior:
- Chooses attack causing highest raw damage
- DOES NOT consider type effectiveness

--------------------------------
HARD MODE
--------------------------------
CPU Pokémon selection:
1. Evaluate player's Pokémon type
2. Choose Pokémon with most effective type advantage
3. If multiple candidates exist:
   - Prefer highest Speed
   - Then highest Defense / Sp.Defense

Battle behavior:
- Prefer Special Attack matching Pokémon type
- Otherwise choose highest power attack
- Must strategically counter the player

DO NOT MODIFY THESE RULES.

----------------------------------------------------
TOURNAMENT SYSTEM
----------------------------------------------------

- 16 Pokémon total
- Bracket tournament
- Single elimination
- Player progresses after victory
- CPU vs CPU battles simulated automatically

Display tournament bracket visually.

----------------------------------------------------
GRAPHICS REQUIREMENTS
----------------------------------------------------

Style:
Classic Pokémon GameBoy / GBA aesthetic.

Must include:

• Battle screen
• Pokémon sprites
• HP bars
• Text box dialogue
• Attack menu with the following options: attack,defense, special attack, special defense
• Difficulty selection screen
• Tournament bracket screen

Use pygame rendering.

No placeholder graphics logic allowed.

----------------------------------------------------
BATTLE SYSTEM
----------------------------------------------------

Turn-based combat:

Order determined by Speed stat.

Each turn:
1. Player chooses attack
2. CPU selects attack based on difficulty AI
3. Apply damage formula
4. Apply type multiplier
5. Update HP
6. Check faint condition

Include:
- Attack animation feedback
- Damage text
- Effectiveness message

----------------------------------------------------
ARCHITECTURE REQUIREMENTS
----------------------------------------------------

Create classes:

Pokemon
Move
Battle
CPU_AI
Tournament
GameUI

Code must be:
- modular
- readable
- expandable

----------------------------------------------------
OUTPUT REQUIREMENTS
----------------------------------------------------

You must output:

1. COMPLETE PROJECT CODE
2. All Python files
3. Clear folder structure
4. Instructions to run the game

Do NOT summarize.
Do NOT explain theory.
Only produce implementation.

The final result must be immediately playable.