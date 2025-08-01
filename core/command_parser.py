"""
Comprehensive command parser for Rogue City with full MajorMUD command support.
Handles all player commands with aliases, error handling, and context validation.
"""

from typing import Dict, Callable, List, Optional, Any
import re


class CommandParser:
    """Comprehensive command parser with MajorMUD-style commands and aliases."""
    
    def __init__(self, game_engine):
        self.game = game_engine
        self.commands: Dict[str, Callable] = {}
        self.aliases: Dict[str, str] = {}
        self.setup_commands()
        self.setup_aliases()
    
    def setup_commands(self):
        """Register all available commands."""
        # Movement commands
        self.commands['north'] = self.cmd_north
        self.commands['south'] = self.cmd_south
        self.commands['east'] = self.cmd_east
        self.commands['west'] = self.cmd_west
        self.commands['up'] = self.cmd_up
        self.commands['down'] = self.cmd_down
        
        # Examination commands
        self.commands['look'] = self.cmd_look
        self.commands['examine'] = self.cmd_examine
        self.commands['exits'] = self.cmd_exits
        self.commands['map'] = self.cmd_map
        
        # Inventory commands
        self.commands['inventory'] = self.cmd_inventory
        self.commands['get'] = self.cmd_get
        self.commands['drop'] = self.cmd_drop
        self.commands['equip'] = self.cmd_equip
        self.commands['unequip'] = self.cmd_unequip
        self.commands['use'] = self.cmd_use
        self.commands['equipment'] = self.cmd_equipment
        
        # Combat commands
        self.commands['attack'] = self.cmd_attack
        self.commands['auto'] = self.cmd_auto
        self.commands['flee'] = self.cmd_flee
        self.commands['status'] = self.cmd_status
        
        # Character commands
        self.commands['stats'] = self.cmd_stats
        self.commands['health'] = self.cmd_health
        self.commands['experience'] = self.cmd_experience
        
        # Game commands
        self.commands['help'] = self.cmd_help
        self.commands['save'] = self.cmd_save
        self.commands['quit'] = self.cmd_quit
        self.commands['settings'] = self.cmd_settings
        self.commands['time'] = self.cmd_time
        
        # Tutorial commands
        self.commands['tutorial'] = self.cmd_tutorial
        self.commands['hint'] = self.cmd_hint
    
    def setup_aliases(self):
        """Setup command aliases for convenience."""
        # Movement aliases
        self.aliases['n'] = 'north'
        self.aliases['s'] = 'south'
        self.aliases['e'] = 'east'
        self.aliases['w'] = 'west'
        self.aliases['u'] = 'up'
        self.aliases['d'] = 'down'
        
        # Examination aliases
        self.aliases['l'] = 'look'
        self.aliases['ex'] = 'examine'
        
        # Inventory aliases
        self.aliases['i'] = 'inventory'
        self.aliases['inv'] = 'inventory'
        self.aliases['take'] = 'get'
        self.aliases['wear'] = 'equip'
        self.aliases['wield'] = 'equip'
        self.aliases['remove'] = 'unequip'
        self.aliases['eq'] = 'equipment'
        
        # Combat aliases
        self.aliases['a'] = 'attack'
        self.aliases['kill'] = 'attack'
        self.aliases['k'] = 'attack'
        self.aliases['run'] = 'flee'
        self.aliases['escape'] = 'flee'
        
        # Character aliases
        self.aliases['st'] = 'stats'
        self.aliases['hp'] = 'health'
        self.aliases['exp'] = 'experience'
        
        # Game aliases
        self.aliases['h'] = 'help'
        self.aliases['?'] = 'help'
        self.aliases['exit'] = 'quit'
        self.aliases['q'] = 'quit'
    
    def parse_command(self, input_text: str) -> bool:
        """Parse and execute a command. Returns True if game should continue."""
        if not input_text.strip():
            return True
        
        # Split command and arguments
        parts = input_text.strip().split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Check for alias
        if command in self.aliases:
            command = self.aliases[command]
        
        # Execute command
        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                self.game.ui.display_message(f"Error executing command: {e}")
                return True
        else:
            self.game.ui.display_message(f"Unknown command: '{command}'. Type 'help' for available commands.")
            return True
    
    # Movement Commands
    def cmd_north(self, args: List[str]) -> bool:
        return self._move_direction('north')
    
    def cmd_south(self, args: List[str]) -> bool:
        return self._move_direction('south')
    
    def cmd_east(self, args: List[str]) -> bool:
        return self._move_direction('east')
    
    def cmd_west(self, args: List[str]) -> bool:
        return self._move_direction('west')
    
    def cmd_up(self, args: List[str]) -> bool:
        return self._move_direction('up')
    
    def cmd_down(self, args: List[str]) -> bool:
        return self._move_direction('down')
    
    def _move_direction(self, direction: str) -> bool:
        """Handle directional movement."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        if self.game.state == self.game.GameState.COMBAT:
            self.game.ui.display_message("You cannot move while in combat! Use 'flee' to escape.")
            return True
        
        current_area = self.game.current_player.current_area
        if not current_area:
            self.game.ui.display_message("You are not in any area.")
            return True
        
        if current_area.move_player(direction):
            # Movement successful - area handles display
            return True
        else:
            self.game.ui.display_message("You can't go that way.")
            return True
    
    # Examination Commands
    def cmd_look(self, args: List[str]) -> bool:
        """Look at room or specific target."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        if not args:
            # Look at room
            current_area = self.game.current_player.current_area
            if current_area:
                current_area.display_room_info()
            else:
                self.game.ui.display_message("You are floating in a void.")
        else:
            # Look at specific target
            target = ' '.join(args).lower()
            self._examine_target(target)
        
        return True
    
    def cmd_examine(self, args: List[str]) -> bool:
        """Examine a specific target."""
        if not args:
            self.game.ui.display_message("Examine what?")
            return True
        
        target = ' '.join(args).lower()
        self._examine_target(target)
        return True
    
    def _examine_target(self, target: str):
        """Examine a specific target in detail."""
        if not self.game.current_player:
            return
        
        current_area = self.game.current_player.current_area
        if not current_area:
            self.game.ui.display_message("You are not in any area.")
            return
        
        # Check inventory first
        for item in self.game.current_player.inventory_system.items:
            if target in item.name.lower():
                self.game.ui.display_message(f"{item.name}: {item.description}")
                if hasattr(item, 'stats') and item.stats:
                    stats_text = ", ".join([f"{k}: {v:+d}" for k, v in item.stats.items() if v != 0])
                    if stats_text:
                        self.game.ui.display_message(f"Stats: {stats_text}")
                return
        
        # Check room items
        if hasattr(current_area, 'items'):
            for item in current_area.items:
                if target in item.name.lower():
                    self.game.ui.display_message(f"{item.name}: {item.description}")
                    return
        
        # Check enemies
        if hasattr(current_area, 'enemies'):
            for enemy in current_area.enemies:
                if target in enemy.name.lower():
                    self.game.ui.display_message(f"A {enemy.name} - {enemy.description}")
                    self.game.ui.display_message(f"HP: {enemy.current_hp}/{enemy.max_hp}")
                    return
        
        self.game.ui.display_message(f"You don't see '{target}' here.")
    
    def cmd_exits(self, args: List[str]) -> bool:
        """Show available exits."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        current_area = self.game.current_player.current_area
        if current_area and hasattr(current_area, 'exits'):
            if current_area.exits:
                exits = list(current_area.exits.keys())
                self.game.ui.display_message(f"Exits: {', '.join(exits)}")
            else:
                self.game.ui.display_message("There are no exits here.")
        else:
            self.game.ui.display_message("You are not in any area.")
        
        return True
    
    def cmd_map(self, args: List[str]) -> bool:
        """Display area map if available."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        current_area = self.game.current_player.current_area
        if current_area and hasattr(current_area, 'show_map'):
            current_area.show_map()
        else:
            self.game.ui.display_message("No map available for this area.")
        
        return True
    
    # Inventory Commands
    def cmd_inventory(self, args: List[str]) -> bool:
        """Display player inventory."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        self.game.current_player.inventory_system.display_inventory()
        return True
    
    def cmd_get(self, args: List[str]) -> bool:
        """Get an item from the current area."""
        if not args:
            self.game.ui.display_message("Get what?")
            return True
        
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        item_name = ' '.join(args).lower()
        current_area = self.game.current_player.current_area
        
        if not current_area or not hasattr(current_area, 'items'):
            self.game.ui.display_message("There are no items here.")
            return True
        
        # Find matching item
        item_to_get = None
        for item in current_area.items[:]:  # Copy list to avoid modification issues
            if item_name in item.name.lower():
                item_to_get = item
                break
        
        if item_to_get:
            if self.game.current_player.inventory_system.add_item(item_to_get):
                current_area.items.remove(item_to_get)
                self.game.ui.display_message(f"You get the {item_to_get.name}.")
            else:
                self.game.ui.display_message("You cannot carry that item.")
        else:
            self.game.ui.display_message(f"There is no '{item_name}' here.")
        
        return True
    
    def cmd_drop(self, args: List[str]) -> bool:
        """Drop an item from inventory."""
        if not args:
            self.game.ui.display_message("Drop what?")
            return True
        
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        item_name = ' '.join(args).lower()
        
        # Find item in inventory
        item_to_drop = None
        for item in self.game.current_player.inventory_system.items:
            if item_name in item.name.lower():
                item_to_drop = item
                break
        
        if item_to_drop:
            # Check if item is equipped
            if (hasattr(self.game.current_player, 'equipment_system') and 
                self.game.current_player.equipment_system.is_equipped(item_to_drop)):
                self.game.ui.display_message(f"You must unequip the {item_to_drop.name} first.")
                return True
            
            self.game.current_player.inventory_system.remove_item(item_to_drop)
            
            # Add to current area
            current_area = self.game.current_player.current_area
            if current_area and hasattr(current_area, 'items'):
                current_area.items.append(item_to_drop)
            
            self.game.ui.display_message(f"You drop the {item_to_drop.name}.")
        else:
            self.game.ui.display_message(f"You don't have '{item_name}'.")
        
        return True
    
    def cmd_equip(self, args: List[str]) -> bool:
        """Equip an item."""
        if not args:
            self.game.ui.display_message("Equip what?")
            return True
        
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        if not hasattr(self.game.current_player, 'equipment_system'):
            self.game.ui.display_message("Equipment system not available.")
            return True
        
        item_name = ' '.join(args).lower()
        
        # Find item in inventory
        item_to_equip = None
        for item in self.game.current_player.inventory_system.items:
            if item_name in item.name.lower():
                item_to_equip = item
                break
        
        if item_to_equip:
            if self.game.current_player.equipment_system.equip_item(item_to_equip):
                self.game.ui.display_message(f"You equip the {item_to_equip.name}.")
            else:
                self.game.ui.display_message(f"You cannot equip the {item_to_equip.name}.")
        else:
            self.game.ui.display_message(f"You don't have '{item_name}'.")
        
        return True
    
    def cmd_unequip(self, args: List[str]) -> bool:
        """Unequip an item."""
        if not args:
            self.game.ui.display_message("Unequip what?")
            return True
        
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        if not hasattr(self.game.current_player, 'equipment_system'):
            self.game.ui.display_message("Equipment system not available.")
            return True
        
        item_name = ' '.join(args).lower()
        
        # Find equipped item
        equipped_items = self.game.current_player.equipment_system.get_all_equipped()
        item_to_unequip = None
        
        for slot, item in equipped_items.items():
            if item and item_name in item.name.lower():
                item_to_unequip = item
                break
        
        if item_to_unequip:
            if self.game.current_player.equipment_system.unequip_item(item_to_unequip):
                self.game.ui.display_message(f"You unequip the {item_to_unequip.name}.")
            else:
                self.game.ui.display_message(f"You cannot unequip the {item_to_unequip.name}.")
        else:
            self.game.ui.display_message(f"You don't have '{item_name}' equipped.")
        
        return True
    
    def cmd_use(self, args: List[str]) -> bool:
        """Use a consumable item."""
        if not args:
            self.game.ui.display_message("Use what?")
            return True
        
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        item_name = ' '.join(args).lower()
        
        # Find item in inventory
        item_to_use = None
        for item in self.game.current_player.inventory_system.items:
            if item_name in item.name.lower():
                item_to_use = item
                break
        
        if item_to_use:
            if hasattr(item_to_use, 'use'):
                item_to_use.use(self.game.current_player)
            else:
                self.game.ui.display_message(f"You cannot use the {item_to_use.name}.")
        else:
            self.game.ui.display_message(f"You don't have '{item_name}'.")
        
        return True
    
    def cmd_equipment(self, args: List[str]) -> bool:
        """Display equipped items."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        if hasattr(self.game.current_player, 'equipment_system'):
            self.game.current_player.equipment_system.display_equipment()
        else:
            self.game.ui.display_message("Equipment system not available.")
        
        return True
    
    # Combat Commands
    def cmd_attack(self, args: List[str]) -> bool:
        """Attack an enemy."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        if not args:
            if self.game.state == self.game.GameState.COMBAT:
                # Attack current target
                self.game.combat_system.player_attack()
            else:
                self.game.ui.display_message("Attack what?")
            return True
        
        target_name = ' '.join(args).lower()
        current_area = self.game.current_player.current_area
        
        if not current_area or not hasattr(current_area, 'enemies'):
            self.game.ui.display_message("There are no enemies here.")
            return True
        
        # Find matching enemy
        target_enemy = None
        for enemy in current_area.enemies:
            if target_name in enemy.name.lower():
                target_enemy = enemy
                break
        
        if target_enemy:
            # Start combat
            self.game.start_combat(target_enemy)
        else:
            self.game.ui.display_message(f"There is no '{target_name}' here.")
        
        return True
    
    def cmd_auto(self, args: List[str]) -> bool:
        """Toggle auto-combat mode."""
        if self.game.state != self.game.GameState.COMBAT:
            self.game.ui.display_message("You are not in combat.")
            return True
        
        if hasattr(self.game.combat_system, 'toggle_auto_combat'):
            self.game.combat_system.toggle_auto_combat()
        else:
            self.game.ui.display_message("Auto-combat not available.")
        
        return True
    
    def cmd_flee(self, args: List[str]) -> bool:
        """Flee from combat."""
        if self.game.state != self.game.GameState.COMBAT:
            self.game.ui.display_message("You are not in combat.")
            return True
        
        if hasattr(self.game.combat_system, 'flee_combat'):
            self.game.combat_system.flee_combat()
        else:
            self.game.ui.display_message("Cannot flee.")
        
        return True
    
    def cmd_status(self, args: List[str]) -> bool:
        """Show combat status."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        if self.game.state == self.game.GameState.COMBAT:
            if hasattr(self.game.combat_system, 'display_combat_status'):
                self.game.combat_system.display_combat_status()
            else:
                self._display_basic_status()
        else:
            self._display_basic_status()
        
        return True
    
    def _display_basic_status(self):
        """Display basic character status."""
        player = self.game.current_player
        self.game.ui.display_message(f"{player.name} the {player.character_class}")
        self.game.ui.display_message(f"Level: {player.level}  HP: {player.current_hp}/{player.max_hp}")
        if hasattr(player, 'current_area') and player.current_area:
            self.game.ui.display_message(f"Location: {player.current_area.name}")
    
    # Character Commands
    def cmd_stats(self, args: List[str]) -> bool:
        """Display character statistics."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        player = self.game.current_player
        self.game.ui.display_message(f"=== {player.name.upper()} THE {player.character_class.upper()} ===")
        self.game.ui.display_message(f"Level: {player.level}    Experience: {player.experience}/{player.experience_to_next_level}")
        self.game.ui.display_message(f"HP: {player.current_hp}/{player.max_hp}")
        
        # Show equipped items
        if hasattr(player, 'equipment_system'):
            equipped = player.equipment_system.get_all_equipped()
            weapon = equipped.get('weapon')
            armor = equipped.get('armor')
            
            weapon_text = weapon.name if weapon else "None"
            armor_text = armor.name if armor else "None"
            
            if weapon:
                weapon_bonus = weapon.stats.get('attack_bonus', 0)
                weapon_text += f" (+{weapon_bonus} attack)" if weapon_bonus > 0 else ""
            
            if armor:
                armor_bonus = armor.stats.get('armor_class', 0)
                armor_text += f" (+{armor_bonus} AC)" if armor_bonus > 0 else ""
            
            self.game.ui.display_message(f"Equipped: {weapon_text}, {armor_text}")
        
        # Base stats
        self.game.ui.display_message(f"STR: {player.strength}  DEX: {player.dexterity}  CON: {player.constitution}")
        self.game.ui.display_message(f"INT: {player.intelligence}  WIS: {player.wisdom}  CHA: {player.charisma}")
        
        # Combat stats
        attack_bonus = player.get_attack_bonus()
        armor_class = player.get_armor_class()
        self.game.ui.display_message(f"Attack Bonus: +{attack_bonus}    Armor Class: {armor_class}")
        
        return True
    
    def cmd_health(self, args: List[str]) -> bool:
        """Display current health."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        player = self.game.current_player
        hp_percent = int((player.current_hp / player.max_hp) * 100)
        
        if hp_percent >= 75:
            status = "excellent"
        elif hp_percent >= 50:
            status = "good"
        elif hp_percent >= 25:
            status = "wounded"
        else:
            status = "badly wounded"
        
        self.game.ui.display_message(f"You are in {status} condition. ({player.current_hp}/{player.max_hp} HP)")
        return True
    
    def cmd_experience(self, args: List[str]) -> bool:
        """Display experience information."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        player = self.game.current_player
        self.game.ui.display_message(f"Experience: {player.experience}/{player.experience_to_next_level}")
        
        exp_needed = player.experience_to_next_level - player.experience
        self.game.ui.display_message(f"You need {exp_needed} more experience to reach level {player.level + 1}.")
        
        return True
    
    # Game Commands
    def cmd_help(self, args: List[str]) -> bool:
        """Display help information."""
        if hasattr(self.game, 'help_system'):
            if args:
                command = args[0].lower()
                self.game.help_system.show_command_help(command)
            else:
                self.game.help_system.show_general_help()
        else:
            # Fallback help
            if args:
                self._show_command_help(args[0].lower())
            else:
                self._show_general_help()
        
        return True
    
    def _show_general_help(self):
        """Show general help information."""
        self.game.ui.display_message("=== ROGUE CITY COMMAND REFERENCE ===")
        self.game.ui.display_message("MOVEMENT: north, south, east, west, up, down (n, s, e, w, u, d)")
        self.game.ui.display_message("EXAMINATION: look [target], examine <target>, exits, map")
        self.game.ui.display_message("INVENTORY: inventory (i), get <item>, drop <item>, equip <item>, unequip <item>")
        self.game.ui.display_message("COMBAT: attack <enemy>, auto, flee, status")
        self.game.ui.display_message("CHARACTER: stats, health, experience, equipment")
        self.game.ui.display_message("GAME: help [command], save, quit, time")
        self.game.ui.display_message("")
        self.game.ui.display_message("Type 'help <command>' for detailed information about a specific command.")
    
    def _show_command_help(self, command: str):
        """Show help for a specific command."""
        help_text = {
            'attack': "ATTACK <enemy>\nAttack a specific enemy in combat.\nExample: attack goblin",
            'look': "LOOK [target]\nLook at the room or examine a specific target.\nExample: look, look sword",
            'get': "GET <item>\nPick up an item from the current room.\nExample: get sword",
            'equip': "EQUIP <item>\nEquip a weapon or armor from your inventory.\nExample: equip sword",
            'stats': "STATS\nDisplay your character's statistics and equipment.",
            'inventory': "INVENTORY\nDisplay your current inventory and carrying capacity.",
            'save': "SAVE\nSave your current game progress.",
            'north': "NORTH (N)\nMove north if there is an exit in that direction.",
        }
        
        if command in help_text:
            self.game.ui.display_message(help_text[command])
        else:
            self.game.ui.display_message(f"No help available for '{command}'.")
    
    def cmd_save(self, args: List[str]) -> bool:
        """Save the game."""
        if not self.game.current_player:
            self.game.ui.display_message("No character loaded.")
            return True
        
        if hasattr(self.game, 'save_manager'):
            if self.game.save_manager.save_character(self.game.current_player):
                self.game.ui.display_message("Game saved successfully.")
            else:
                self.game.ui.display_message("Failed to save game.")
        else:
            self.game.ui.display_message("Save system not available.")
        
        return True
    
    def cmd_quit(self, args: List[str]) -> bool:
        """Quit the game."""
        if self.game.current_player:
            self.game.ui.display_message("Saving game before exit...")
            if hasattr(self.game, 'save_manager'):
                self.game.save_manager.save_character(self.game.current_player)
        
        self.game.ui.display_message("Thank you for playing Rogue City!")
        return False  # Signal game should exit
    
    def cmd_settings(self, args: List[str]) -> bool:
        """Display game settings."""
        self.game.ui.display_message("=== GAME SETTINGS ===")
        self.game.ui.display_message("Game running at 60 FPS")
        self.game.ui.display_message("Combat system: Timer-based")
        self.game.ui.display_message("Auto-save: On character action")
        return True
    
    def cmd_time(self, args: List[str]) -> bool:
        """Display game time information."""
        if hasattr(self.game, 'start_time'):
            import time
            elapsed = time.time() - self.game.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.game.ui.display_message(f"Play time: {minutes}m {seconds}s")
        else:
            self.game.ui.display_message("Time tracking not available.")
        return True
    
    # Tutorial Commands
    def cmd_tutorial(self, args: List[str]) -> bool:
        """Show tutorial information."""
        if hasattr(self.game, 'tutorial_system'):
            self.game.tutorial_system.show_tutorial_help()
        else:
            self.game.ui.display_message("Tutorial system not available.")
        return True
    
    def cmd_hint(self, args: List[str]) -> bool:
        """Show context-sensitive hints."""
        if hasattr(self.game, 'tutorial_system'):
            self.game.tutorial_system.show_context_hint()
        else:
            self._show_basic_hint()
        return True
    
    def _show_basic_hint(self):
        """Show basic hints based on game state."""
        if not self.game.current_player:
            self.game.ui.display_message("Hint: Create a character to start playing!")
            return
        
        if self.game.state == self.game.GameState.COMBAT:
            self.game.ui.display_message("Hint: Use 'attack' to fight, 'auto' for automatic combat, or 'flee' to escape.")
        elif hasattr(self.game.current_player, 'current_area'):
            area = self.game.current_player.current_area
            if hasattr(area, 'items') and area.items:
                self.game.ui.display_message("Hint: Use 'get <item>' to pick up items you see.")
            elif hasattr(area, 'enemies') and area.enemies:
                self.game.ui.display_message("Hint: Use 'attack <enemy>' to start combat.")
            else:
                self.game.ui.display_message("Hint: Use 'look' to examine your surroundings and 'exits' to see where you can go.")
        else:
            self.game.ui.display_message("Hint: Type 'help' for a list of available commands.")