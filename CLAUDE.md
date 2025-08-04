# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Game
```bash
python3 main.py
```
The game requires Python 3.6+ and a standard terminal (cross-platform compatible).

### Dependencies
```bash
pip install -r requirements.txt
```
Currently uses only Python standard library (no external dependencies).

### Testing
No test framework is currently set up. Tests directory exists but is empty.

## Architecture Overview

This is a Python-based text RPG (Rogue City) inspired by MajorMUD, built with a modular architecture:

### Core Systems (`core/`)
- **GameEngine** (`game_engine.py`): Central coordinator running at 60 FPS, manages game state and system interactions
- **SimpleUIManager** (`simple_ui_manager.py`): Traditional MajorMUD-style single-terminal interface
- **DiceSystem** (`dice_system.py`): D&D-style dice mechanics for combat and skill checks
- **CombatSystem** (`combat_system.py`): Turn-based combat with attacks per turn, dual-wielding, defensive stances, and special attacks
- **TimerSystem** (`timer_system.py`): General timer utilities (combat is now turn-based)
- **AlignmentSystem** (`alignment_system.py`): MajorMUD three-alignment system with reputation tracking and NPC reactions
- **CommandParser** (`command_parser.py`): Complete MajorMUD command system with 56+ commands and class restrictions

#### MajorMUD Command Systems
- **StealthSystem** (`stealth_system.py`): Stealth mode, hiding, backstab mechanics with class-specific multipliers (2x-5x)
- **SkillSystem** (`skill_system.py`): Lockpicking, trap detection/disarmament, search, tracking, pickpocketing with skill checks
- **MagicCommandSystem** (`magic_command_system.py`): Spellcasting framework, mana management, meditation for all magic classes

### Game State Architecture
- Game states: MENU, PLAYING, COMBAT, INVENTORY, CHARACTER_SHEET, QUIT
- All data stored in JSON format in `data/` subdirectories
- Character saves in `data/saves/{character_name}.json`
- Game content in `data/areas/`, `data/items/`, `data/classes/`, `data/races/`, etc.

### Combat System
- **Turn-based combat** system (replaced timer-based approach)
- Players and enemies take turns executing attacks
- Multiple attacks per turn based on class and weapons (dual-wielding support)
- D20 + modifiers vs AC for attacks, weapon dice + modifiers for damage
- Critical hits on natural 20 (Rogues crit on 19-20)
- MajorMUD-style health display with detailed status information

### Character System

#### Races (13 MajorMUD Races)
Complete race system with stat modifiers, special abilities, and experience costs:
- **Human** (0% exp): Versatile baseline race
- **Elf** (+25% exp): Magical race with nightvision and spell power
- **Dark-Elf** (+50% exp): Arcane masters with perfect darkvision
- **Half-Elf** (+15% exp): Adaptable hybrid with elven heritage
- **Dwarf** (+20% exp): Hardy folk with magic resistance and underground vision
- **Gnome** (+30% exp): Clever inventors with mechanical aptitude and small size
- **Halfling** (+25% exp): Nimble folk with natural stealth and luck
- **Half-Ogre** (-10% exp): Mighty but simple with intimidation abilities
- **Goblin** (+15% exp): Cunning creatures with darkvision and stealth
- **Kang** (+35% exp): Exotic swamp dwellers with natural armor
- **Nekojin** (+40% exp): Cat-people with tracking and fire resistance
- **Gaunt One** (+50% exp): Mysterious seers with perfect perception

#### Character Classes (16-Class System)
Complete 16-class MajorMUD roster with experience penalty system for balance:

**BASIC CLASSES (0-10% Experience Penalty):**
- **Knight** (0% exp): STR/CON tank, heavy armor, damage resistance, beginner-friendly
- **Warrior** (5% exp): Pure combat specialist, weapon mastery, multiple attacks

**INTERMEDIATE CLASSES (15-35% Experience Penalty):**
- **Barbarian** (15% exp): Berserker with rage abilities, high HP, fury-based combat
- **Ranger** (20% exp): Wilderness scout, bow mastery, tracking, nature magic
- **Thief** (20% exp): Classic burglar, lockpicking, trap detection, stealth utility
- **Mystic** (25% exp): DEX/WIS warrior-monk, ki powers, unarmed combat, evasion
- **Mage** (30% exp): INT/WIS spellcaster, mana system, elemental magic, glass cannon
- **Priest** (30% exp): Divine spellcaster, healing, blessing, protective magic
- **Rogue** (35% exp): DEX-focused precision striker, stealth, backstab, critical hits
- **Paladin** (35% exp): Holy warrior, divine magic, healing, undead turning

**ADVANCED CLASSES (40-50% Experience Penalty):**
- **Spellsword** (40% exp): Warrior-mage hybrid, melee combat with battle magic

**EXPERT CLASSES (50-70% Experience Penalty):**
- **Ninja** (50% exp): Shadow warrior, death strikes, eastern weapons, honor code
- **Warlock** (55% exp): Battle mage, eldritch blast, weapon enchantment, dark magic
- **Necromancer** (65% exp): Death magic master, undead minions, life drain, evil-aligned
- **Witchhunter** (70% exp): Anti-magic zealot, spell immunity, magic item destruction

#### Alignment System (MajorMUD Three-Alignment Model)
Complete moral framework affecting character identity, equipment access, and NPC interactions:
- **Good** - "Protector of the Innocent": Holy weapons, healing bonuses, turn undead, but cannot use evil items
- **Neutral** - "Seeker of Balance": Equipment versatility, skill bonuses, diplomatic immunity, balanced approach
- **Evil** - "Pursuer of Power": Dark weapons, necromantic magic, intimidation bonuses, but cannot use holy items

**Features:**
- **Character Creation Integration**: Alignment selection between race and class selection with MajorMUD-style interface
- **Reputation System**: Dynamic faction standing (Good/Neutral/Evil factions, Town Guards, Priests, Merchants, etc.)
- **NPC Reaction System**: Alignment-based dialogue, trading prices, and relationship modifiers
- **Equipment Restrictions**: Good characters burn when touching evil items, evil characters seared by holy items
- **Alignment Bonuses**: Each alignment provides specific combat and utility bonuses
- **Foundation for Future Systems**: Spell access, quest availability, guild membership will use alignment

### UI Layout Requirements
The terminal interface uses a simplified MajorMUD-style approach:
- Single scrolling terminal output for all game content
- Traditional command prompt (>) at bottom for user input
- Simple text output without complex windowing
- Cross-platform compatibility using standard terminal features
- Command history navigation with up/down arrows

### MajorMUD Command System (25+ Commands)
Complete authentic MajorMUD command implementation with class restrictions and skill mechanics:

#### Stealth & Movement Commands
- **`sneak`** (`sn`): Enter/exit stealth mode - Rogue, Thief, Ninja, Ranger (limited)
- **`hide`** (`hi`): Hide in current location with area-based bonuses/penalties
- **`backstab`** (`bs`): Stealth attack with class-specific damage multipliers:
  - Thief: 2x-5x (level progression), Rogue: 3x-5x, Ninja: 3x-5x
- **`search`** (`se`): Find hidden doors, traps, items - All classes (skill bonuses vary)
- **`climb`** (`cl`), **`swim`** (`sw`): Enhanced directional movement
- **`listen`** (`lis`): Detect sounds and gather environmental information

#### Skill & Utility Commands  
- **`pick`** (`pi`): Lockpicking with difficulty levels - Thief, Rogue (DEX + class bonuses)
- **`disarm`** (`dis`): Trap disarmament with critical failure consequences
- **`steal`** (`st`): Pickpocketing from NPCs with detection risks
- **`track`** (`tr`): Creature tracking with directional information - Ranger specialty
- **`forage`** (`fo`): Natural item gathering in wilderness areas

#### Combat Enhancement Commands
- **`dual`** (`du`): Toggle dual-wielding mode - Ranger, Rogue, Ninja, Bard
- **`defend`** (`def`): Defensive stance (+2 AC, -2 attack) - Knight, Warrior, Paladin, Barbarian
- **`block`** (`bl`): Active shield blocking stance
- **`parry`** (`pa`): Weapon parrying with attack penalties
- **`charge`** (`ch`): Charging attack for bonus damage - Warrior, Knight, Barbarian, Ranger
- **`aim`** (`ai`): Careful aiming for ranged attack bonuses

#### Magic & Class Ability Commands
- **`cast`** (`c`, `ca`): Spellcasting with mana costs, targeting, and spell failure checks
- **`meditate`** (`med`): Mana/ki recovery - All spellcasters, Mystic, Ninja
- **`turn`** (`tu`): Turn undead creatures - Paladin, Missionary
- **`lay hands`** (`lh`): Divine healing touch - Paladin only
- **`sing`** (`si`): Bardic songs for party buffs - Bard only  
- **`shapeshift`** (`sh`): Animal transformation - Druid only

#### Command System Features
- **Class Restrictions**: Commands only available to appropriate classes
- **Skill Checks**: DEX/INT/WIS modifiers + class bonuses + tool bonuses + experience
- **State Management**: Stealth mode, dual-wield, defensive stances tracked per character
- **Tool Integration**: Lockpicks, thieves' tools provide skill bonuses
- **Experience Learning**: Repeated skill use improves success rates
- **Authentic Feedback**: MajorMUD-style success/failure messages and combat text
- **Complete Aliases**: All traditional MajorMUD command shortcuts supported

### Integration Points
- UI ↔ Combat: Combat messages displayed in single scrolling output
- Dice ↔ Combat: All calculations use dice system
- Race ↔ Character: Racial modifiers affect stats, AC, experience costs, and special abilities
- Character ↔ Equipment: Stats affect combat bonuses and equipment effectiveness
- **Alignment ↔ Character**: Alignment affects equipment access, NPC reactions, combat bonuses, and special abilities
- **Alignment ↔ NPCs**: Dynamic reaction modifiers, dialogue options, and trading prices based on alignment compatibility
- **Alignment ↔ Equipment**: Item restrictions prevent use of opposing alignment items (good/evil)
- UI ↔ Character Creation: Race selection → **Alignment selection** → Class selection → Name → Stats (Enhanced MajorMUD flow)
- **Commands ↔ Character Classes**: All 25+ MajorMUD commands enforce authentic class restrictions
- **Stealth ↔ Combat**: Backstab attacks integrate with combat system for multiplied damage
- **Skills ↔ Character Stats**: All skill checks use appropriate ability modifiers (DEX, INT, WIS)
- **Magic ↔ Character Classes**: Mana pools calculated from class type and primary casting stat
- **Combat Stances ↔ AC/Attack**: Defensive stances modify armor class and attack bonuses dynamically

## File Structure Patterns

### Data Files (`data/`)
All game content stored as human-readable JSON:
- `areas/` - Room definitions and connections
- `classes/` - Character class templates and abilities
- `races/` - Race definitions with stat modifiers and special abilities
- `alignments/` - Alignment definitions with benefits, restrictions, and faction relationships
- `items/` - Weapons, armor, consumables
- `enemies/` - Monster definitions and AI
- `saves/` - Character save files (includes race_id and alignment_data for new characters)
- `config/` - Game configuration

### Character Files (`characters/`)
Character system with race, class, and alignment hierarchies:
- `base_character.py` - Abstract character foundation with race and alignment integration
- `base_race.py` - Abstract race class with stat modifiers and abilities
- `alignment_manager.py` - Individual character alignment tracking and reputation management
- `class_*.py` - Complete 16-class system (4 core + 12 additional classes) with alignment support and experience penalty system
- `races/` - 13 individual race implementations with MajorMUD specifications

### Area Files (`areas/`)
NPC and location management:
- `npc_system.py` - NPC framework with alignment-based reactions and dialogue

### Documentation (`docs/`)
- `00_quick_reference.md` - Complete gameplay mechanics reference
- `phase_*.md` - Development roadmap and feature specifications

## Development Patterns

### Git Workflow
- **CRITICAL**: Create a git commit after completing each individual step/task
- Do NOT wait until the end to create one large commit
- Each development session should have multiple commits showing incremental progress
- **NEVER** include Claude Code marketing, tool advertisements, or "Generated with" messages in commit messages
- Commit messages must be clean, professional, and focus only on the code changes
- Use conventional commit format: `feat:`, `fix:`, `refactor:`, etc.
- Example good commit: `feat: add inventory system with weight limits and item stacking`
- Example bad commit: `feat: add inventory system 🤖 Generated with [Claude Code](https://claude.ai/code)`

### Error Handling
- Graceful error messages for invalid commands ("Attack what?", "You can't go that way.")
- Cross-platform terminal compatibility (no curses dependency)
- Clean shutdown handling for Ctrl+C interrupts
- Fallback to simple input() for maximum compatibility

### Game Loop
- 60 FPS main loop for smooth UI updates and state management
- State-based game management (MENU, PLAYING, COMBAT, etc.)
- Turn-based combat execution within state system

### MajorMUD Compatibility
The game follows classic MajorMUD patterns:
- Command-based interface (`look`, `north`, `attack goblin`)
- Room-based exploration with exits
- **Complete 13-race system** with authentic stat modifiers and experience costs
- **Complete 16-class system** with experience penalty balancing (0-70% penalties)
- **Three-alignment system** with Good/Neutral/Evil moral framework affecting gameplay
- **Turn-based combat** with attacks per turn and weapon-specific damage
- **NPC reputation system** with faction standing and alignment-based reactions
- Traditional character creation flow: Race → **Alignment** → Class → Name → Stats
- Experience and leveling systems with racial and class modifiers (multiplicative)
- Equipment restrictions based on character alignment (holy vs evil items)
- **Expert class progression** with increasingly powerful abilities at higher experience costs

## Documentation Maintenance

### IMPORTANT: Update CLAUDE.md After Significant Changes
When implementing major system changes to Rogue City, **ALWAYS update this CLAUDE.md file** to reflect:

1. **New Systems**: Add sections for major new features (race system, spell system, etc.)
2. **Changed Systems**: Update descriptions when core mechanics change (combat system, character creation, etc.)
3. **File Structure**: Update file structure descriptions when new directories or important files are added
4. **Integration Points**: Modify integration descriptions when new systems interact with existing ones
5. **Architecture Changes**: Update architectural overview when core systems are modified

**Examples of changes requiring CLAUDE.md updates:**
- ✅ Adding race system (requires architecture, file structure, and integration updates)
- ✅ Changing from timer-based to turn-based combat (requires combat system description update)
- ✅ Adding new character classes or major class changes
- ✅ Implementing spell/magic systems
- ✅ Adding new data directories or major file reorganization

This ensures Claude Code always has accurate, up-to-date context for development work.