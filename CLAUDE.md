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
- **CombatSystem** (`combat_system.py`): Turn-based combat with attacks per turn and dual-wielding
- **TimerSystem** (`timer_system.py`): General timer utilities (combat is now turn-based)
- **AlignmentSystem** (`alignment_system.py`): MajorMUD three-alignment system with reputation tracking and NPC reactions

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

#### Character Classes
Four classes with D&D-style stat modifiers and difficulty ratings:
- **Rogue** (Difficulty 11): DEX-focused, multiple attacks, high crit chance
- **Knight** (Difficulty 3): STR/CON tank, heavy armor, damage resistance  
- **Mage** (Difficulty 9): INT/WIS caster, mana system, elemental magic
- **Mystic** (Difficulty 6): DEX/WIS hybrid, evasion, spiritual abilities

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

### Integration Points
- UI ↔ Combat: Combat messages displayed in single scrolling output
- Dice ↔ Combat: All calculations use dice system
- Race ↔ Character: Racial modifiers affect stats, AC, experience costs, and special abilities
- Character ↔ Equipment: Stats affect combat bonuses and equipment effectiveness
- **Alignment ↔ Character**: Alignment affects equipment access, NPC reactions, combat bonuses, and special abilities
- **Alignment ↔ NPCs**: Dynamic reaction modifiers, dialogue options, and trading prices based on alignment compatibility
- **Alignment ↔ Equipment**: Item restrictions prevent use of opposing alignment items (good/evil)
- UI ↔ Character Creation: Race selection → **Alignment selection** → Class selection → Name → Stats (Enhanced MajorMUD flow)

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
- `class_*.py` - Four character classes (Rogue, Knight, Mage, Mystic) with alignment support
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
- **Three-alignment system** with Good/Neutral/Evil moral framework affecting gameplay
- **Turn-based combat** with attacks per turn and weapon-specific damage
- **NPC reputation system** with faction standing and alignment-based reactions
- Traditional character creation flow: Race → **Alignment** → Class → Name → Stats
- Experience and leveling systems with racial modifiers
- Equipment restrictions based on character alignment (holy vs evil items)

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