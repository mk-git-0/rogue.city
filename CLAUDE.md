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
- **TimerSystem** (`timer_system.py`): Handles timer-based combat with weapon speed differences

### Game State Architecture
- Game states: MENU, PLAYING, COMBAT, INVENTORY, CHARACTER_SHEET, QUIT
- All data stored in JSON format in `data/` subdirectories
- Character saves in `data/saves/{character_name}.json`
- Game content in `data/areas/`, `data/items/`, `data/classes/`, etc.

### Combat System
- Timer-based combat with class-specific weapon speeds (Rogue: 2s, Knight: 4s, Mage: 6s, Mystic: 3s)
- Auto-combat continues after initial attack command
- D20 + modifiers vs AC for attacks, weapon dice + modifiers for damage
- Critical hits on natural 20 (Rogues crit on 19-20)

### Character Classes
Four classes with D&D-style stat modifiers and difficulty ratings:
- **Rogue** (Difficulty 11): DEX-focused, fast daggers, high crit chance
- **Knight** (Difficulty 3): STR/CON tank, slow swords, damage resistance  
- **Mage** (Difficulty 9): INT/WIS caster, slowest attacks, mana system
- **Mystic** (Difficulty 6): DEX/WIS hybrid, unarmed combat, evasion

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
- Timer ↔ Combat: Attack speeds create action delays
- Character ↔ Equipment: Stats affect combat bonuses
- UI ↔ Character Creation: Step-by-step prompts in traditional terminal style

## File Structure Patterns

### Data Files (`data/`)
All game content stored as human-readable JSON:
- `areas/` - Room definitions and connections
- `classes/` - Character class templates and abilities
- `items/` - Weapons, armor, consumables
- `enemies/` - Monster definitions and AI
- `saves/` - Character save files
- `config/` - Game configuration

### Documentation (`docs/`)
- `00_quick_reference.md` - Complete gameplay mechanics reference
- `phase_*.md` - Development roadmap and feature specifications

## Development Patterns

### Error Handling
- Graceful error messages for invalid commands ("Attack what?", "You can't go that way.")
- Cross-platform terminal compatibility (no curses dependency)
- Clean shutdown handling for Ctrl+C interrupts
- Fallback to simple input() for maximum compatibility

### Game Loop
- 60 FPS main loop for smooth timer processing
- State-based game management
- Automatic combat continuation after initial attack

### MajorMUD Compatibility
The game follows classic MajorMUD patterns:
- Command-based interface (`look`, `north`, `attack goblin`)
- Room-based exploration with exits
- Timer-based combat with weapon speed differences
- Experience and leveling systems