"""
Comprehensive help system for Rogue City with command reference and context-sensitive guidance.
Provides detailed help information in traditional MajorMUD style.
"""

from typing import Dict, List, Optional


class HelpSystem:
    """Comprehensive in-game help system with MajorMUD-style formatting."""
    
    def __init__(self, ui_manager):
        self.ui = ui_manager
        self.command_help: Dict[str, Dict[str, str]] = {}
        self.setup_command_help()
    
    def setup_command_help(self):
        """Initialize comprehensive command help database."""
        self.command_help = {
            # Movement Commands
            'north': {
                'syntax': 'NORTH (N)',
                'description': 'Move north if there is an exit in that direction.',
                'examples': ['north', 'n'],
                'aliases': 'n',
                'notes': 'Cannot move while in combat. Use \'flee\' to escape first.'
            },
            'south': {
                'syntax': 'SOUTH (S)',
                'description': 'Move south if there is an exit in that direction.',
                'examples': ['south', 's'],
                'aliases': 's',
                'notes': 'Cannot move while in combat. Use \'flee\' to escape first.'
            },
            'east': {
                'syntax': 'EAST (E)',
                'description': 'Move east if there is an exit in that direction.',
                'examples': ['east', 'e'],
                'aliases': 'e',
                'notes': 'Cannot move while in combat. Use \'flee\' to escape first.'
            },
            'west': {
                'syntax': 'WEST (W)',
                'description': 'Move west if there is an exit in that direction.',
                'examples': ['west', 'w'],
                'aliases': 'w',
                'notes': 'Cannot move while in combat. Use \'flee\' to escape first.'
            },
            'up': {
                'syntax': 'UP (U)',
                'description': 'Move up if there is an exit in that direction.',
                'examples': ['up', 'u'],
                'aliases': 'u',
                'notes': 'Cannot move while in combat. Use \'flee\' to escape first.'
            },
            'down': {
                'syntax': 'DOWN (D)',
                'description': 'Move down if there is an exit in that direction.',
                'examples': ['down', 'd'],
                'aliases': 'd',
                'notes': 'Cannot move while in combat. Use \'flee\' to escape first.'
            },
            
            # Examination Commands
            'look': {
                'syntax': 'LOOK [target]',
                'description': 'Look at the current room or examine a specific target.',
                'examples': ['look', 'look sword', 'look goblin', 'l chest'],
                'aliases': 'l',
                'notes': 'Without a target, shows room description. With target, examines specific object.'
            },
            'examine': {
                'syntax': 'EXAMINE <target>',
                'description': 'Examine a specific target in detail.',
                'examples': ['examine sword', 'examine armor', 'ex potion'],
                'aliases': 'ex',
                'notes': 'Provides detailed information about items, enemies, or room features.'
            },
            'exits': {
                'syntax': 'EXITS',
                'description': 'Display all available exits from the current room.',
                'examples': ['exits'],
                'aliases': '',
                'notes': 'Shows compass directions you can move: north, south, east, west, up, down.'
            },
            'map': {
                'syntax': 'MAP',
                'description': 'Display the area map if available.',
                'examples': ['map'],
                'aliases': '',
                'notes': 'Shows ASCII map of current area with your location marked.'
            },
            
            # Inventory Commands
            'inventory': {
                'syntax': 'INVENTORY',
                'description': 'Display your current inventory with weight and capacity.',
                'examples': ['inventory', 'inv', 'i'],
                'aliases': 'i, inv',
                'notes': 'Shows all carried items, total weight, and carrying capacity.'
            },
            'get': {
                'syntax': 'GET <item>',
                'description': 'Pick up an item from the current room.',
                'examples': ['get sword', 'get potion', 'take gold'],
                'aliases': 'take',
                'notes': 'Must have inventory space and carrying capacity. Item must be present in room.'
            },
            'drop': {
                'syntax': 'DROP <item>',
                'description': 'Drop an item from your inventory to the current room.',
                'examples': ['drop sword', 'drop torch'],
                'aliases': '',
                'notes': 'Cannot drop equipped items. Must unequip first.'
            },
            'equip': {
                'syntax': 'EQUIP <item>',
                'description': 'Equip a weapon or armor from your inventory.',
                'examples': ['equip sword', 'wear armor', 'wield dagger'],
                'aliases': 'wear, wield',
                'notes': 'Item must be in inventory and appropriate for your character class.'
            },
            'unequip': {
                'syntax': 'UNEQUIP <item>',
                'description': 'Unequip a currently equipped item.',
                'examples': ['unequip sword', 'remove armor'],
                'aliases': 'remove',
                'notes': 'Unequipped items return to your inventory if there is space.'
            },
            'use': {
                'syntax': 'USE <item>',
                'description': 'Use a consumable item from your inventory.',
                'examples': ['use potion', 'use scroll'],
                'aliases': '',
                'notes': 'Only works with consumable items like potions, food, and scrolls.'
            },
            'equipment': {
                'syntax': 'EQUIPMENT',
                'description': 'Display all currently equipped items and their bonuses.',
                'examples': ['equipment', 'eq'],
                'aliases': 'eq',
                'notes': 'Shows weapon, armor, and other equipped items with stat bonuses.'
            },
            
            # Combat Commands
            'attack': {
                'syntax': 'ATTACK <enemy>',
                'description': 'Attack a specific enemy, starting combat.',
                'examples': ['attack goblin', 'kill orc', 'a skeleton', 'k wolf'],
                'aliases': 'a, kill, k',
                'notes': 'Starts turn-based combat. Use \"auto\" to automate rounds until combat ends.'
            },
            'auto': {
                'syntax': 'AUTO',
                'description': 'Toggle automatic combat mode during battle.',
                'examples': ['auto'],
                'aliases': '',
                'notes': 'Only available during combat. When ON, the game runs full turn cycles automatically until combat ends or you toggle it OFF.'
            },
            'flee': {
                'syntax': 'FLEE',
                'description': 'Attempt to escape from combat.',
                'examples': ['flee', 'run', 'escape'],
                'aliases': 'run, escape',
                'notes': 'May fail based on enemy speed and your dexterity. Ends combat if successful.'
            },
            'status': {
                'syntax': 'STATUS',
                'description': 'Display current combat status and health.',
                'examples': ['status'],
                'aliases': '',
                'notes': 'Shows your HP, enemy HP, and combat state during battle.'
            },
            
            # Character Commands
            'stats': {
                'syntax': 'STATS',
                'description': 'Display complete character statistics and equipment bonuses.',
                'examples': ['stats', 'st'],
                'aliases': 'st',
                'notes': 'Shows level, experience, attributes, equipment, attack bonus, and armor class.'
            },
            'health': {
                'syntax': 'HEALTH',
                'description': 'Display current health status.',
                'examples': ['health', 'hp'],
                'aliases': 'hp',
                'notes': 'Shows current and maximum hit points with condition description.'
            },
            'experience': {
                'syntax': 'EXPERIENCE',
                'description': 'Display experience points and progress to next level.',
                'examples': ['experience', 'exp'],
                'aliases': 'exp',
                'notes': 'Shows current experience, experience needed for next level, and progress.'
            },
            
            # Game Commands
            'help': {
                'syntax': 'HELP [command]',
                'description': 'Display help information for all commands or a specific command.',
                'examples': ['help', 'help attack', '? look', 'h inventory'],
                'aliases': '?, h',
                'notes': 'Without argument shows general help. With command name shows detailed help.'
            },
            'save': {
                'syntax': 'SAVE',
                'description': 'Save your current game progress.',
                'examples': ['save'],
                'aliases': '',
                'notes': 'Saves character, inventory, equipment, location, and game statistics.'
            },
            'quit': {
                'syntax': 'QUIT',
                'description': 'Save and exit the game.',
                'examples': ['quit', 'exit', 'q'],
                'aliases': 'exit, q',
                'notes': 'Automatically saves your progress before exiting.'
            },
            'time': {
                'syntax': 'TIME',
                'description': 'Display current play time.',
                'examples': ['time'],
                'aliases': '',
                'notes': 'Shows total time played in current session.'
            },
            'settings': {
                'syntax': 'SETTINGS',
                'description': 'Display current game settings.',
                'examples': ['settings'],
                'aliases': '',
                'notes': 'Shows frame rate, combat system type, and other game configuration.'
            },
            
            # Tutorial Commands
            'tutorial': {
                'syntax': 'TUTORIAL',
                'description': 'Display tutorial information and guidance.',
                'examples': ['tutorial'],
                'aliases': '',
                'notes': 'Shows tutorial help and current lesson information.'
            },
            'hint': {
                'syntax': 'HINT',
                'description': 'Get context-sensitive hints for your current situation.',
                'examples': ['hint'],
                'aliases': '',
                'notes': 'Provides helpful suggestions based on your current location and state.'
            }
        }
    
    def show_general_help(self):
        """Display general help with command categories."""
        self.ui.display_message("=" * 50)
        self.ui.display_message("            ROGUE CITY COMMAND REFERENCE")
        self.ui.display_message("=" * 50)
        self.ui.display_message("")
        
        # Movement
        self.ui.display_message("MOVEMENT COMMANDS:")
        self.ui.display_message("  north, south, east, west, up, down")
        self.ui.display_message("  Aliases: n, s, e, w, u, d")
        self.ui.display_message("")
        
        # Examination
        self.ui.display_message("EXAMINATION COMMANDS:")
        self.ui.display_message("  look [target]     - Look at room or specific target")
        self.ui.display_message("  examine <target>  - Examine target in detail")
        self.ui.display_message("  exits             - Show available exits")
        self.ui.display_message("  map               - Display area map")
        self.ui.display_message("")
        
        # Inventory
        self.ui.display_message("INVENTORY COMMANDS:")
        self.ui.display_message("  inventory (i)     - Show your inventory")
        self.ui.display_message("  get <item>        - Pick up item")
        self.ui.display_message("  drop <item>       - Drop item")
        self.ui.display_message("  equip <item>      - Equip weapon/armor")
        self.ui.display_message("  unequip <item>    - Unequip item")
        self.ui.display_message("  use <item>        - Use consumable item")
        self.ui.display_message("  equipment (eq)    - Show equipped items")
        self.ui.display_message("")
        
        # Combat
        self.ui.display_message("COMBAT COMMANDS:")
        self.ui.display_message("  attack <enemy>    - Attack enemy")
        self.ui.display_message("  auto              - Toggle auto-combat")
        self.ui.display_message("  flee              - Escape from combat")
        self.ui.display_message("  status            - Show combat status")
        self.ui.display_message("")
        
        # Character
        self.ui.display_message("CHARACTER COMMANDS:")
        self.ui.display_message("  stats             - Character statistics")
        self.ui.display_message("  health (hp)       - Current health")
        self.ui.display_message("  experience (exp)  - Experience progress")
        self.ui.display_message("")
        
        # Game
        self.ui.display_message("GAME COMMANDS:")
        self.ui.display_message("  help [command]    - Show help information")
        self.ui.display_message("  save              - Save game progress")
        self.ui.display_message("  quit              - Save and exit")
        self.ui.display_message("  time              - Show play time")
        self.ui.display_message("  tutorial          - Tutorial information")
        self.ui.display_message("  hint              - Context-sensitive hints")
        self.ui.display_message("")
        
        self.ui.display_message("Type 'help <command>' for detailed information about a specific command.")
        self.ui.display_message("Example: help attack")
        self.ui.display_message("")
        
        # Quick tips
        self.ui.display_message("QUICK TIPS:")
        self.ui.display_message("• Most commands have short aliases (n for north, i for inventory)")
        self.ui.display_message("• Use 'look' frequently to examine your surroundings")
        self.ui.display_message("• Equipment affects your combat abilities and stats")
        self.ui.display_message("• Save regularly to preserve your progress")
        self.ui.display_message("=" * 50)
    
    def show_command_help(self, command: str):
        """Display detailed help for a specific command."""
        command = command.lower()
        
        # Check for aliases
        alias_map = {
            'n': 'north', 's': 'south', 'e': 'east', 'w': 'west', 'u': 'up', 'd': 'down',
            'l': 'look', 'ex': 'examine',
            'i': 'inventory', 'inv': 'inventory', 'take': 'get', 'wear': 'equip', 
            'wield': 'equip', 'remove': 'unequip', 'eq': 'equipment',
            'a': 'attack', 'kill': 'attack', 'k': 'attack', 'run': 'flee', 'escape': 'flee',
            'st': 'stats', 'hp': 'health', 'exp': 'experience',
            '?': 'help', 'h': 'help', 'exit': 'quit', 'q': 'quit'
        }
        
        if command in alias_map:
            command = alias_map[command]
        
        if command not in self.command_help:
            self.ui.display_message(f"No help available for '{command}'.")
            self.ui.display_message("Type 'help' for a list of all available commands.")
            return
        
        help_data = self.command_help[command]
        
        self.ui.display_message("=" * 40)
        self.ui.display_message(f"HELP: {command.upper()}")
        self.ui.display_message("=" * 40)
        
        # Syntax
        self.ui.display_message(f"SYNTAX: {help_data['syntax']}")
        
        # Aliases
        if help_data['aliases']:
            self.ui.display_message(f"ALIASES: {help_data['aliases']}")
        
        self.ui.display_message("")
        
        # Description
        self.ui.display_message("DESCRIPTION:")
        self.ui.display_message(f"  {help_data['description']}")
        self.ui.display_message("")
        
        # Examples
        if help_data['examples']:
            self.ui.display_message("EXAMPLES:")
            for example in help_data['examples']:
                self.ui.display_message(f"  > {example}")
            self.ui.display_message("")
        
        # Notes
        if help_data['notes']:
            self.ui.display_message("NOTES:")
            self.ui.display_message(f"  {help_data['notes']}")
            self.ui.display_message("")
        
        # Related commands
        related = self._get_related_commands(command)
        if related:
            self.ui.display_message("RELATED COMMANDS:")
            self.ui.display_message(f"  {', '.join(related)}")
            self.ui.display_message("")
        
        self.ui.display_message("=" * 40)
    
    def _get_related_commands(self, command: str) -> List[str]:
        """Get list of related commands for a given command."""
        relations = {
            'north': ['south', 'east', 'west', 'exits', 'map'],
            'south': ['north', 'east', 'west', 'exits', 'map'],
            'east': ['north', 'south', 'west', 'exits', 'map'],
            'west': ['north', 'south', 'east', 'exits', 'map'],
            'up': ['down', 'exits', 'map'],
            'down': ['up', 'exits', 'map'],
            'look': ['examine', 'exits'],
            'examine': ['look'],
            'inventory': ['get', 'drop', 'equip', 'equipment'],
            'get': ['drop', 'inventory', 'equip'],
            'drop': ['get', 'inventory'],
            'equip': ['unequip', 'equipment', 'inventory'],
            'unequip': ['equip', 'equipment'],
            'equipment': ['equip', 'unequip', 'stats'],
            'attack': ['flee', 'auto', 'status'],
            'auto': ['attack', 'flee', 'status'],
            'flee': ['attack', 'auto'],
            'status': ['attack', 'health', 'stats'],
            'stats': ['health', 'experience', 'equipment'],
            'health': ['stats', 'status'],
            'experience': ['stats'],
            'save': ['quit'],
            'quit': ['save']
        }
        
        return relations.get(command, [])
    
    def show_context_hint(self, game_state=None, player=None, area=None):
        """Show context-sensitive hints based on current game state."""
        if not player:
            self.ui.display_message("HINT: Create a character to start your adventure!")
            return
        
        # Check various game states and provide appropriate hints
        hints = []
        
        # Combat hints
        if game_state and hasattr(game_state, 'COMBAT') and game_state == game_state.COMBAT:
            hints.extend([
                "You are in combat! Use 'attack' to fight or 'flee' to escape.",
                "Try 'auto' to toggle automatic combat mode.",
                "Use 'status' to check your health during combat."
            ])
        
        # Area-specific hints
        elif area:
            if hasattr(area, 'items') and area.items:
                hints.append(f"There are items here! Use 'get <item>' to pick them up.")
            
            if hasattr(area, 'enemies') and area.enemies:
                hints.append(f"There are enemies here! Use 'attack <enemy>' to start combat.")
            
            if hasattr(area, 'exits') and area.exits:
                exits = list(area.exits.keys())
                if len(exits) > 1:
                    hints.append(f"You can go: {', '.join(exits)}. Use 'exits' to see all options.")
            
            # Tutorial-specific hints
            if hasattr(area, 'name') and 'tutorial' in area.name.lower():
                hints.extend([
                    "This is the tutorial area. Use 'look' to examine your surroundings.",
                    "Try 'tutorial' for specific tutorial guidance."
                ])
        
        # Character-specific hints
        if player:
            # Low health hint
            if hasattr(player, 'current_hp') and hasattr(player, 'max_hp'):
                if player.current_hp < player.max_hp * 0.3:
                    hints.append("Your health is low! Look for healing potions or rest areas.")
            
            # Inventory hints
            if hasattr(player, 'inventory_system'):
                inv = player.inventory_system
                if hasattr(inv, 'items') and len(inv.items) == 0:
                    hints.append("Your inventory is empty. Look for items to collect!")
                elif hasattr(inv, 'is_full') and inv.is_full():
                    hints.append("Your inventory is full! Consider dropping items you don't need.")
            
            # Equipment hints
            if hasattr(player, 'equipment_system'):
                eq = player.equipment_system
                equipped = eq.get_all_equipped()
                if not equipped.get('weapon'):
                    hints.append("You don't have a weapon equipped! Use 'equip <weapon>' to arm yourself.")
                if not equipped.get('armor'):
                    hints.append("You don't have armor equipped! Use 'equip <armor>' to protect yourself.")
            
            # Experience hint
            if hasattr(player, 'experience') and hasattr(player, 'experience_to_next_level'):
                exp_pct = (player.experience / player.experience_to_next_level) * 100
                if exp_pct > 80:
                    hints.append("You're close to leveling up! Defeat more enemies to gain experience.")
        
        # General gameplay hints
        general_hints = [
            "Use 'look' frequently to examine your surroundings and find hidden details.",
            "Check your 'stats' to see how equipment affects your character.",
            "Remember to 'save' your progress regularly!",
            "Use 'map' to see the layout of your current area.",
            "Type 'help <command>' to learn more about specific commands."
        ]
        
        # Add general hints if no specific ones apply
        if not hints:
            hints = general_hints[:2]  # Show first 2 general hints
        else:
            hints.append(general_hints[0])  # Always add the look hint
        
        # Display hints
        self.ui.display_message("=== HELPFUL HINTS ===")
        for i, hint in enumerate(hints[:3], 1):  # Show max 3 hints
            self.ui.display_message(f"{i}. {hint}")
        
        self.ui.display_message("")
        self.ui.display_message("Type 'help' for complete command reference.")
    
    def show_tutorial_help(self):
        """Show tutorial-specific help information."""
        self.ui.display_message("=== TUTORIAL GUIDANCE ===")
        self.ui.display_message("")
        self.ui.display_message("Welcome to Rogue City! This tutorial will teach you the basics.")
        self.ui.display_message("")
        self.ui.display_message("ESSENTIAL COMMANDS TO LEARN:")
        self.ui.display_message("• LOOK - Examine your surroundings")
        self.ui.display_message("• NORTH/SOUTH/EAST/WEST - Move around (or n/s/e/w)")
        self.ui.display_message("• GET <item> - Pick up items")
        self.ui.display_message("• EQUIP <item> - Equip weapons and armor")
        self.ui.display_message("• ATTACK <enemy> - Start combat")
        self.ui.display_message("• INVENTORY - Check what you're carrying")
        self.ui.display_message("")
        self.ui.display_message("TUTORIAL PROGRESSION:")
        self.ui.display_message("1. Learn basic movement and examination")
        self.ui.display_message("2. Practice inventory and equipment management")
        self.ui.display_message("3. Learn combat mechanics")
        self.ui.display_message("4. Complete tutorial challenges")
        self.ui.display_message("")
        self.ui.display_message("Use 'hint' anytime for context-sensitive help!")
        self.ui.display_message("Use 'help <command>' for detailed command information.")
        self.ui.display_message("")
    
    def show_new_player_guide(self):
        """Show comprehensive new player guide."""
        self.ui.display_message("=" * 60)
        self.ui.display_message("                    NEW PLAYER GUIDE")
        self.ui.display_message("=" * 60)
        self.ui.display_message("")
        
        self.ui.display_message("GETTING STARTED:")
        self.ui.display_message("1. Use 'look' to see your surroundings")
        self.ui.display_message("2. Use movement commands (north, south, east, west) to explore")
        self.ui.display_message("3. Pick up items with 'get <item>'")
        self.ui.display_message("4. Equip weapons and armor with 'equip <item>'")
        self.ui.display_message("5. Fight enemies with 'attack <enemy>'")
        self.ui.display_message("")
        
        self.ui.display_message("CHARACTER CLASSES:")
        self.ui.display_message("• ROGUE - Fast, high damage, difficult to master (Difficulty 11)")
        self.ui.display_message("• KNIGHT - Tanky, reliable, easy to play (Difficulty 3)")
        self.ui.display_message("• MAGE - Magical, complex abilities (Difficulty 9)")
        self.ui.display_message("• MYSTIC - Balanced, moderate difficulty (Difficulty 6)")
        self.ui.display_message("")
        
        self.ui.display_message("COMBAT BASICS:")
        self.ui.display_message("• Combat is turn-based - you and enemies alternate turns")
        self.ui.display_message("• Use 'auto' during combat for automatic attacking")
        self.ui.display_message("• Use 'flee' to escape difficult battles")
        self.ui.display_message("• Equipment affects your attack bonus and armor class")
        self.ui.display_message("")
        
        self.ui.display_message("IMPORTANT TIPS:")
        self.ui.display_message("• Save frequently with the 'save' command")
        self.ui.display_message("• Check your 'stats' to see character progression")
        self.ui.display_message("• Use 'inventory' to manage your items")
        self.ui.display_message("• Explore thoroughly - items and secrets are hidden everywhere")
        self.ui.display_message("")
        
        self.ui.display_message("Type 'help' for the complete command reference!")
        self.ui.display_message("=" * 60)
    
    def get_general_help(self) -> str:
        """Get general help text for external use."""
        return """=== ROGUE CITY COMMAND REFERENCE ===
MOVEMENT: north, south, east, west, up, down (n, s, e, w, u, d)
EXAMINATION: look [target], examine <target>, exits, map
INVENTORY: inventory (i), get <item>, drop <item>, equip <item>, unequip <item>
COMBAT: attack <enemy>, auto, flee, status
CHARACTER: stats, health, experience, equipment
GAME: help [command], save, quit, time

Type 'help <command>' for detailed information about a specific command."""
    
    def get_command_help(self, command: str) -> Optional[str]:
        """Get help text for a specific command."""
        command = command.lower()
        if command in self.command_help:
            help_data = self.command_help[command]
            return f"{help_data['syntax']}\n{help_data['description']}\nExample: {help_data['examples'][0] if help_data['examples'] else 'N/A'}"
        return None