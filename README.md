# 🏰 Rogue City

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-cross--platform-lightgrey.svg)]()

A classic MajorMUD-style text RPG built for the terminal, featuring turn-based combat, character progression, and dungeon exploration. Experience the nostalgia of 1990s BBS gaming with modern polish and cross-platform compatibility.

## ✨ Features

### 🎮 Core Gameplay
- **Four Character Classes** with unique abilities and difficulty ratings
  - 🗡️ **Rogue** (Difficulty 11): Fast, high damage, stealth-focused
  - 🛡️ **Knight** (Difficulty 3): Tanky, reliable, beginner-friendly  
  - 🔮 **Mage** (Difficulty 9): Magical, complex spell system
  - ⚖️ **Mystic** (Difficulty 6): Balanced, mind-body harmony

### ⚔️ Combat System
- **Turn-based Combat** with class/weapon-driven multiple attacks
- **Auto-combat Mode** for streamlined gameplay
- **Critical Hit System** with class-specific bonuses
- **Tactical Fleeing** with success chance calculations

### 🎒 Character Progression
- **Complete Inventory System** with weight limits and capacity
- **Equipment Bonuses** affecting combat and character stats
- **Experience & Leveling** with meaningful progression
- **Achievement System** tracking player accomplishments

### 🗺️ World Exploration
- **Tutorial Cave** - 15-minute guided learning experience
- **Forest Exploration** - 30-minute adventure to Rogue City
- **ASCII Maps** showing area layouts and player position
- **Dynamic Item Placement** with progression-based rewards

### 🏪 Merchants and Trading
- Buy and sell items with NPC merchants
- Dynamic pricing influenced by alignment and reputation
- Repair damaged equipment at blacksmiths

### 📜 Quest System
- Alignment-based quest lines with Good/Neutral/Evil paths
- Quest journal, accept/abandon commands, and rewards
- NPC dialogue integration (ask <npc> missions)

### 💾 Quality of Life
- **Automatic Save/Load** preserving all progress
- **Comprehensive Help System** with detailed command reference
- **Statistics Tracking** for playtime and achievements
- **Cross-platform Compatibility** (Windows, macOS, Linux)

## 🚀 Quick Start

### Prerequisites
- Python 3.6 or higher
- Terminal with curses support (standard on macOS/Linux, Windows Terminal/PowerShell recommended)

### Installation & Running

```bash
# Clone the repository
git clone https://github.com/mk-git-0/rogue.city.git
cd rogue.city

# Install dependencies (currently none - uses Python standard library)
pip install -r requirements.txt

# Run the game
python main.py
```

### First Time Playing

1. **Create a Character**: Choose from four classes with different difficulty levels
2. **Complete the Tutorial**: Learn basic commands in the tutorial cave (~15 minutes)
3. **Explore the Forest**: Adventure through dangerous paths to reach Rogue City (~30 minutes)
4. **Master the Commands**: Use `help` for complete command reference

## 🎯 Gameplay Guide

### Essential Commands

```
Movement:     north, south, east, west (n, s, e, w)
Examination:  look, examine <target>, exits, map
Inventory:    inventory (i), get <item>, drop <item>
Equipment:    equip <item>, unequip <item>, equipment (eq)
Combat:       attack <enemy>, auto, flee, status
Character:    stats, health, experience
Game:         help, save, quit, time
```

### Character Classes Deep Dive

| Class  | STR | DEX | CON | INT | WIS | CHA | Weapon Speed | Special Abilities |
|--------|-----|-----|-----|-----|-----|-----|--------------|-------------------|
| Rogue  | 8   | 13  | 8   | 12  | 9   | 9   | 2.0s (Fast)  | 19-20 Crit Range |
| Knight | 13  | 8   | 12  | 8   | 9   | 9   | 4.0s (Slow)  | Damage Resistance |
| Mage   | 8   | 9   | 8   | 13  | 12  | 9   | 6.0s (Slowest) | Mana System |
| Mystic | 9   | 12  | 9   | 9   | 13  | 8   | 3.0s (Medium) | Balanced Build |

### Combat Mechanics

- **Turn-based System**: Alternating player/enemy turns with initiative
- **D20 Combat**: Attack rolls use D20 + modifiers vs target AC
- **Critical Hits**: Natural 20 (Rogues: 19-20) deal double damage
- **Equipment Matters**: Weapon and armor bonuses significantly impact combat
- **Strategic Fleeing**: Escape difficult encounters based on DEX vs enemy speed

### Progression Path

1. **Tutorial Cave** (Level 1-2)
   - Learn basic movement and combat
   - Acquire starting equipment
   - Complete tutorial challenges

2. **Forest Exploration** (Level 2-3)
   - Face tougher enemies
   - Find better equipment
   - Navigate to Rogue City

3. **Game Completion**
   - Reach Rogue City for victory
   - View statistics and achievements
   - See class-specific completion messages

## 🛠️ Technical Architecture

### Project Structure
```
rogue.city/
├── core/                    # Core game systems
│   ├── game_engine.py      # Central game coordinator (60 FPS)
│   ├── command_parser.py   # MajorMUD-style command processing
│   ├── combat_system.py    # Turn-based combat mechanics
│   ├── inventory_system.py # Weight-based inventory management
│   ├── equipment_system.py # Equipment bonuses and restrictions
│   ├── help_system.py      # Comprehensive help system
│   ├── game_completion.py  # Statistics and achievements
│   └── simple_ui_manager.py # Cross-platform terminal interface
├── characters/              # Character class definitions
├── items/                   # Item system (weapons, armor, consumables)
├── areas/                   # World areas and room definitions
├── enemies/                 # Enemy types and encounter system
├── data/                    # Game data (JSON format)
│   ├── areas/              # Area definitions and maps
│   ├── classes/            # Character class templates
│   ├── items/              # Item databases
│   ├── config/             # Game configuration
│   └── saves/              # Character save files
└── docs/                    # Documentation and development phases
```

### Key Systems

- **Game Engine**: 60 FPS main loop coordinating all systems
- **Command Parser**: Comprehensive MajorMUD-style command processing
- **Combat System**: Turn-based with initiative and class abilities
- **World System**: Room-based exploration with dynamic events
- **Save System**: JSON-based with complete state preservation
- **UI System**: Cross-platform terminal interface using curses

## 🏆 Achievements

Track your progress with a comprehensive achievement system:

- **Tutorial Master**: Complete the cave tutorial
- **Monster Slayer**: Defeat 10+ enemies  
- **Explorer**: Discover 5+ areas
- **Master Thief**: Complete game as Rogue (Difficulty 11)
- **Speed Runner**: Complete in under 30 minutes
- **Perfectionist**: Complete without dying
- And many more!

## 📊 Development Phases

This project was built in 6 development phases:

1. **Phase 1**: Foundation (Game engine, UI, basic systems)
2. **Phase 2**: Character System (Classes, stats, progression)
3. **Phase 3**: Combat System (Turn-based, D&D mechanics)
4. **Phase 4**: World System (Areas, rooms, exploration)
5. **Phase 5**: Item System (Inventory, equipment, progression)
6. **Phase 6**: Final Polish (Commands, completion, documentation)

## 🤝 Contributing

This project was built for a hackathon demonstration, but contributions are welcome!

### Development Setup
```bash
# Clone and enter directory
git clone https://github.com/mk-git-0/rogue.city.git
cd rogue.city

# The game uses only Python standard library
python main.py
```

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Maintain MajorMUD-style command compatibility
- Preserve cross-platform compatibility

## 📝 Technical Requirements

### Minimum System Requirements
- **Python**: 3.6 or higher
- **Terminal**: Curses-compatible terminal
- **Memory**: 256 MB RAM
- **Storage**: 50 MB free space

### Recommended Environment
- **Terminal Size**: 80x24 or larger
- **Python**: 3.8+ for best performance
- **Platform**: macOS Terminal, Linux Terminal, Windows Terminal

## 🐛 Troubleshooting

### Common Issues

**Q: Game won't start - "Terminal does not support required features"**
A: Ensure you're using a proper terminal (not IDE console). On Windows, use Windows Terminal or PowerShell, not Command Prompt.

**Q: Characters/save files not loading**
A: Check that the `data/saves/` directory exists and has proper permissions.

**Q: Combat seems slow/unresponsive**
A: The game runs at 60 FPS. If your terminal is slow, try a different terminal emulator.

**Q: Unicode characters not displaying**
A: Ensure your terminal supports UTF-8 encoding for the best experience.

### Performance Optimization
- Game runs at 60 FPS for smooth timer processing
- Memory usage optimized for long play sessions
- Save files are human-readable JSON for debugging

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MajorMUD** - Original inspiration for game mechanics and UI style
- **Dungeons & Dragons** - Combat system and stat mechanics inspiration  
- **Classic BBS Games** - Terminal-based gaming nostalgia
- **Hackathon Community** - Motivation and development timeline

## 🎮 Fun Facts

- **Total Development Time**: ~6 phases of focused development
- **Lines of Code**: 5000+ lines of Python
- **File Count**: 50+ source files in modular architecture
- **Expected Playtime**: 45-60 minutes for complete experience
- **Easter Eggs**: Hidden references to classic MUD gaming
- **Cross-platform**: Tested on macOS, Linux, and Windows

---

**Ready to begin your adventure? Run `python main.py` and enter the world of Rogue City!** 🏰⚔️