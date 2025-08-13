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
        # Resting commands
        self.commands['rest'] = self.cmd_rest
        self.commands['stoprest'] = self.cmd_stop_rest
        
        # Character commands
        self.commands['stats'] = self.cmd_stats
        self.commands['health'] = self.cmd_health
        self.commands['experience'] = self.cmd_experience
        
        # Game commands
        self.commands['help'] = self.cmd_help
        self.commands['save'] = self.cmd_save
        self.commands['quit'] = self.cmd_quit
        self.commands['settings'] = self.cmd_settings
        self.commands['statline'] = self.cmd_statline
        self.commands['time'] = self.cmd_time
        
        # Tutorial commands
        self.commands['tutorial'] = self.cmd_tutorial
        self.commands['hint'] = self.cmd_hint
        
        # === NEW MAJORMUD COMMANDS ===
        
        # Stealth & Movement commands
        self.commands['sneak'] = self.cmd_sneak
        self.commands['hide'] = self.cmd_hide
        self.commands['search'] = self.cmd_search
        self.commands['climb'] = self.cmd_climb
        self.commands['swim'] = self.cmd_swim
        self.commands['listen'] = self.cmd_listen
        
        # Skill & Utility commands
        self.commands['pick'] = self.cmd_pick
        self.commands['disarm'] = self.cmd_disarm
        self.commands['backstab'] = self.cmd_backstab
        self.commands['steal'] = self.cmd_steal
        self.commands['track'] = self.cmd_track
        self.commands['forage'] = self.cmd_forage
        
        # Combat Enhancement commands
        self.commands['dual'] = self.cmd_dual
        self.commands['defend'] = self.cmd_defend
        self.commands['block'] = self.cmd_block
        self.commands['parry'] = self.cmd_parry
        self.commands['charge'] = self.cmd_charge
        self.commands['aim'] = self.cmd_aim
        
        # Magic & Class Ability commands
        self.commands['cast'] = self.cmd_cast
        self.commands['meditate'] = self.cmd_meditate
        self.commands['spells'] = self.cmd_spells
        self.commands['turn'] = self.cmd_turn_undead
        self.commands['lay'] = self.cmd_lay_hands
        self.commands['sing'] = self.cmd_sing
        self.commands['shapeshift'] = self.cmd_shapeshift
        
        # Skill display commands
        self.commands['skills'] = self.cmd_skills
        
        # Commerce & Economy commands
        self.commands['buy'] = self.cmd_buy
        self.commands['sell'] = self.cmd_sell
        self.commands['list'] = self.cmd_list
        self.commands['appraise'] = self.cmd_appraise
        self.commands['repair'] = self.cmd_repair
        self.commands['wealth'] = self.cmd_wealth
        
        # Social & Conversation commands
        self.commands['talk'] = self.cmd_talk
        self.commands['say'] = self.cmd_say
        self.commands['tell'] = self.cmd_tell
        self.commands['ask'] = self.cmd_ask
        self.commands['greet'] = self.cmd_greet
        self.commands['whisper'] = self.cmd_whisper
        self.commands['broadcast'] = self.cmd_broadcast
        
        # Quest System commands
        self.commands['quest'] = self.cmd_quest
        self.commands['accept'] = self.cmd_accept_quest
        self.commands['abandon'] = self.cmd_abandon_quest
        self.commands['journal'] = self.cmd_quest_journal
    
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
        self.aliases['sleep'] = 'rest'
        self.aliases['wait'] = 'rest'
        
        # Character aliases
        self.aliases['st'] = 'stats'
        self.aliases['stat'] = 'status'
        self.aliases['hp'] = 'health'
        self.aliases['hea'] = 'health'
        self.aliases['exp'] = 'experience'
        
        # Game aliases
        self.aliases['h'] = 'help'
        self.aliases['?'] = 'help'
        self.aliases['exit'] = 'quit'
        self.aliases['q'] = 'quit'
        
        # === NEW MAJORMUD COMMAND ALIASES ===
        
        # Stealth & Movement aliases
        self.aliases['sn'] = 'sneak'
        self.aliases['hi'] = 'hide'
        self.aliases['se'] = 'search'
        self.aliases['cl'] = 'climb'
        self.aliases['sw'] = 'swim'
        self.aliases['lis'] = 'listen'
        
        # Skill & Utility aliases
        self.aliases['pi'] = 'pick'
        self.aliases['dis'] = 'disarm'
        self.aliases['bs'] = 'backstab'
        self.aliases['st'] = 'steal'  # Note: conflicts with 'stats', but 'steal' is more specific
        self.aliases['tr'] = 'track'
        self.aliases['fo'] = 'forage'
        
        # Combat Enhancement aliases
        self.aliases['du'] = 'dual'
        self.aliases['def'] = 'defend'
        self.aliases['bl'] = 'block'
        self.aliases['pa'] = 'parry'
        self.aliases['ch'] = 'charge'
        self.aliases['ai'] = 'aim'
        
        # Magic & Class Ability aliases
        self.aliases['c'] = 'cast'
        self.aliases['ca'] = 'cast'
        self.aliases['med'] = 'meditate'
        self.aliases['sp'] = 'spells'
        self.aliases['tu'] = 'turn'
        self.aliases['lay hands'] = 'lay'
        self.aliases['lh'] = 'lay'
        self.aliases['si'] = 'sing'
        self.aliases['sh'] = 'shapeshift'
        
        # Commerce & Economy aliases
        self.aliases['b'] = 'buy'
        self.aliases['purchase'] = 'buy'
        # Removed 's' -> 'sell' to avoid conflict with movement 'south'
        self.aliases['trade'] = 'sell'
        self.aliases['ls'] = 'list'
        self.aliases['shop'] = 'list'
        self.aliases['app'] = 'appraise'
        self.aliases['value'] = 'appraise'
        self.aliases['fix'] = 'repair'
        self.aliases['money'] = 'wealth'
        self.aliases['gold'] = 'wealth'
        
        # Social & Conversation aliases  
        self.aliases['t'] = 'talk'
        self.aliases['speak'] = 'talk'
        self.aliases['chat'] = 'talk'
        self.aliases['"'] = 'say'  # Support for say "message"
        self.aliases['tel'] = 'tell'
        self.aliases['as'] = 'ask'
        self.aliases['gr'] = 'greet'
        self.aliases['wh'] = 'whisper'
        self.aliases['br'] = 'broadcast'
        self.aliases['shout'] = 'broadcast'
        
        # Quest System aliases
        self.aliases['q'] = 'quest'  # Note: overrides 'quit', but 'quit' is less common
        self.aliases['que'] = 'quest'
        self.aliases['quests'] = 'quest'
        self.aliases['acc'] = 'accept'
        self.aliases['take quest'] = 'accept'
        self.aliases['aban'] = 'abandon'
        self.aliases['drop quest'] = 'abandon'
        self.aliases['jour'] = 'journal'
        self.aliases['log'] = 'journal'
    
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
                self.game.ui_manager.log_error(f"Error executing command: {e}")
                return True
        else:
            self.game.ui_manager.log_error(f"Unknown command: '{command}'. Type 'help' for available commands.")
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
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if self.game.state == self.game.GameState.COMBAT:
            self.game.ui_manager.log_error("You cannot move while in combat! Use 'flee' to escape.")
            return True
        
        # Use the game engine's move command instead
        self.game._move_command(direction)
        return True
    
    # Examination Commands
    def cmd_look(self, args: List[str]) -> bool:
        """Look at room or specific target."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            # Use the game engine's look command
            self.game._look_command()
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
        # Use the game engine's exits command
        self.game._exits_command()
        return True
    
    def cmd_map(self, args: List[str]) -> bool:
        """Display area map if available."""
        # Use the game engine's map command  
        self.game._map_command()
        return True
    
    # Inventory Commands
    def cmd_inventory(self, args: List[str]) -> bool:
        """Display player inventory."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Use the game engine's inventory command
        self.game._inventory_command()
        return True
    
    def cmd_get(self, args: List[str]) -> bool:
        """Get an item from the current area."""
        if not args:
            self.game.ui_manager.log_error("Get what?")
            return True
        
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Use the game engine's get command
        self.game._get_command(args)
        return True
        
    
    def cmd_drop(self, args: List[str]) -> bool:
        """Drop an item from inventory (delegates to engine)."""
        self.game._drop_command(args)
        return True
    
    def cmd_equip(self, args: List[str]) -> bool:
        """Equip an item."""
        # Use the game engine's equip command
        self.game._equip_command(args)
        return True
    
    def cmd_unequip(self, args: List[str]) -> bool:
        """Unequip an item."""
        # Use the game engine's unequip command
        self.game._unequip_command(args)
        return True
    
    def cmd_use(self, args: List[str]) -> bool:
        """Use a consumable item."""
        # Use the game engine's use command
        self.game._use_command(args)
        return True
    
    def cmd_equipment(self, args: List[str]) -> bool:
        """Display equipped items."""
        # Use the game engine's equipment command
        self.game._equipment_command()
        return True
    
    # Combat Commands
    def cmd_attack(self, args: List[str]) -> bool:
        """Attack an enemy."""
        # Use the game engine's attack command
        self.game._attack_command(args)
        return True
    
    def cmd_auto(self, args: List[str]) -> bool:
        """Toggle auto-combat mode."""
        # Use the game engine's auto command
        self.game._auto_combat_command()
        return True
    
    def cmd_flee(self, args: List[str]) -> bool:
        """Flee from combat."""
        # Use the game engine's flee command
        self.game._flee_command()
        return True
    
    def cmd_status(self, args: List[str]) -> bool:
        """Show comprehensive character status (MajorMUD STATUS command)."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
            
        # Show comprehensive character status
        self._show_comprehensive_status()
        return True
    
    def _show_comprehensive_status(self):
        """Display comprehensive character status (MajorMUD STATUS command style)."""
        player = self.game.current_player
        
        print()
        print("=== CHARACTER STATUS ===")
        
        # Character identification
        print(f"Name: {player.name}")
        print(f"Class: {player.character_class.title()}")
        print(f"Level: {player.level}")
        
        # Experience information
        if hasattr(player, 'experience'):
            required_exp = player.calculate_required_experience()
            if required_exp != float('inf'):
                exp_needed = required_exp - player.experience
                print(f"Experience: {player.experience} (need {exp_needed} for next level)")
            else:
                print(f"Experience: {player.experience} (maximum level reached)")
        
        # Health and combat stats
        hp_percent = int((player.current_hp / player.max_hp) * 100)
        print(f"Hit Points: {player.current_hp}/{player.max_hp} ({hp_percent}%)")
        
        # Mana for applicable classes
        if hasattr(player, 'current_mana') and hasattr(player, 'max_mana'):
            if player.max_mana > 0:
                mana_percent = int((player.current_mana / player.max_mana) * 100)
                print(f"Mana Points: {player.current_mana}/{player.max_mana} ({mana_percent}%)")
        
        print(f"Armor Class: {player.armor_class}")
        print(f"Base Attack Bonus: +{player.base_attack_bonus}")
        
        # Abilities (stats with modifiers)
        print("\n=== ABILITIES ===")
        for stat, value in player.stats.items():
            modifier = player.get_stat_modifier(stat)
            mod_str = f"({modifier:+d})" if modifier != 0 else "(+0)"
            print(f"{stat.title()}: {value} {mod_str}")
        
        # Equipment summary
        if hasattr(player, 'equipment_system') and player.equipment_system:
            print("\n=== EQUIPMENT SUMMARY ===")
            weapon = player.equipment_system.get_equipped_weapon()
            armor = player.equipment_system.get_equipped_armor()
            
            weapon_name = weapon.name if weapon else "None"
            armor_name = armor.name if armor else "None"
            
            print(f"Weapon: {weapon_name}")
            print(f"Armor: {armor_name}")
            
            # Show dual-wielding for rogues
            if (hasattr(player, 'character_class') and player.character_class == 'rogue' and
                hasattr(player.equipment_system, 'get_offhand_weapon')):
                offhand = player.equipment_system.get_offhand_weapon()
                if offhand:
                    print(f"Off-hand: {offhand.name}")
        
        # Location
        if hasattr(player, 'current_area') and player.current_area:
            area_name = getattr(player.current_area, 'name', 'Unknown Area')
            room_name = getattr(player.current_room, 'name', 'Unknown Room') if player.current_room else 'Unknown Room'
            print(f"\nLocation: {area_name} - {room_name}")
        
        # Combat status
        if hasattr(self.game, 'combat_system') and self.game.combat_system.is_active():
            combat_status = self.game.combat_system.get_combat_status()
            living_enemies = combat_status.get('living_enemies', 0)
            print(f"\n*** IN COMBAT with {living_enemies} enemies ***")
            
        print()

    # Resting Commands
    def cmd_rest(self, args: List[str]) -> bool:
        """Sit and rest to regenerate HP and mana over time."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        if hasattr(self.game, '_start_resting'):
            self.game._start_resting()
        else:
            self.game.ui_manager.log_error("Resting is not available.")
        return True

    def cmd_stop_rest(self, args: List[str]) -> bool:
        """Stop resting immediately."""
        if hasattr(self.game, '_stop_resting'):
            self.game._stop_resting(reason="You stop resting.")
        return True
    
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
        """Display current health and mana (MajorMUD HEALTH command)."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Use the UI manager's detailed health display
        self.game.ui_manager.show_health_status(self.game.current_player)
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
        self.game.ui.display_message("=== NEW MAJORMUD COMMANDS ===")
        self.game.ui.display_message("STEALTH: sneak [off], hide, backstab <enemy>")
        self.game.ui.display_message("SKILLS: pick <lock>, disarm <trap>, search [target], track <creature>")
        self.game.ui.display_message("UTILITY: steal <item> <target>, listen, climb <direction>, swim <direction>")
        self.game.ui.display_message("COMBAT+: dual, defend, block, parry, charge [enemy], aim <target>")
        self.game.ui.display_message("MAGIC: cast <spell> [target], meditate")
        self.game.ui.display_message("CLASS: turn (undead), lay [hands] [target], sing <song>, shapeshift <form>")
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
        self.game.ui.display_message("Combat system: Turn-based")
        self.game.ui.display_message("Auto-save: On character action")
        return True
    
    def cmd_statline(self, args: List[str]) -> bool:
        """Toggle status line display (MajorMUD STATLINE command)."""
        if not args:
            # Show current setting
            status = "ON" if self.game.ui_manager.show_status_line else "OFF"
            self.game.ui_manager.log_info(f"Status line is currently {status}")
            self.game.ui_manager.log_info("Usage: STATLINE ON/OFF")
            return True
            
        setting = args[0].lower()
        if setting in ['on', 'true', '1', 'yes']:
            self.game.ui_manager.show_status_line = True
            self.game.ui_manager.log_success("Status line enabled - HP/Mana will show at prompt")
        elif setting in ['off', 'false', '0', 'no']:
            self.game.ui_manager.show_status_line = False
            self.game.ui_manager.log_success("Status line disabled")
        else:
            self.game.ui_manager.log_error("Usage: STATLINE ON/OFF")
            
        return True
    
    def cmd_time(self, args: List[str]) -> bool:
        """Display game time information."""
        if hasattr(self.game, 'start_time'):
            import time
            elapsed = time.time() - self.game.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.game.ui_manager.log_info(f"Play time: {minutes}m {seconds}s")
        else:
            self.game.ui_manager.log_info("Time tracking not available.")
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
    
    # ====================================================================
    # NEW MAJORMUD COMMAND IMPLEMENTATIONS
    # ====================================================================
    
    # Stealth & Movement Commands
    def cmd_sneak(self, args: List[str]) -> bool:
        """Enter or exit stealth mode."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Initialize stealth system if needed
        if not hasattr(self.game, 'stealth_system'):
            from .stealth_system import StealthSystem
            # Initialize skill system if needed
            if not hasattr(self.game, 'skill_system'):
                from .skill_system import SkillSystem
                self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
            self.game.stealth_system = StealthSystem(self.game.dice_system, self.game.ui_manager, self.game.skill_system)
        
        if args and args[0].lower() == 'off':
            self.game.stealth_system.exit_stealth_mode(self.game.current_player)
        else:
            self.game.stealth_system.enter_stealth_mode(self.game.current_player)
        
        return True
    
    def cmd_hide(self, args: List[str]) -> bool:
        """Attempt to hide in current location."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Initialize stealth system if needed
        if not hasattr(self.game, 'stealth_system'):
            from .stealth_system import StealthSystem
            # Initialize skill system if needed
            if not hasattr(self.game, 'skill_system'):
                from .skill_system import SkillSystem
                self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
            self.game.stealth_system = StealthSystem(self.game.dice_system, self.game.ui_manager, self.game.skill_system)
        
        current_area = getattr(self.game.current_player, 'current_area', None)
        self.game.stealth_system.attempt_hide(self.game.current_player, current_area)
        
        return True
    
    def cmd_search(self, args: List[str]) -> bool:
        """Search for hidden items, doors, or secrets."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Initialize skill system if needed
        if not hasattr(self.game, 'skill_system'):
            from .skill_system import SkillSystem
            self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
        
        target = ' '.join(args) if args else None
        current_area = getattr(self.game.current_player, 'current_area', None)
        self.game.skill_system.attempt_search(self.game.current_player, current_area, target)
        
        return True
    
    def cmd_climb(self, args: List[str]) -> bool:
        """Attempt to climb in a direction or object."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Climb what?")
            return True
        
        direction_or_object = args[0].lower()
        
        # For now, treat as movement command for climbing directions
        if direction_or_object in ['up', 'down', 'north', 'south', 'east', 'west']:
            self.game.ui_manager.log_info(f"You attempt to climb {direction_or_object}...")
            # Use existing movement system
            return self._move_direction(direction_or_object)
        else:
            self.game.ui_manager.log_info(f"You attempt to climb the {direction_or_object}...")
            self.game.ui_manager.log_error("There is nothing suitable to climb here.")
        
        return True
    
    def cmd_swim(self, args: List[str]) -> bool:
        """Attempt to swim in a direction."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Swim where?")
            return True
        
        direction = args[0].lower()
        if direction in ['north', 'south', 'east', 'west', 'up', 'down']:
            self.game.ui_manager.log_info(f"You swim {direction}...")
            # Use existing movement system
            return self._move_direction(direction)
        else:
            self.game.ui_manager.log_error("You can't swim in that direction.")
        
        return True
    
    def cmd_listen(self, args: List[str]) -> bool:
        """Listen for sounds and movements."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Initialize skill system if needed
        if not hasattr(self.game, 'skill_system'):
            from .skill_system import SkillSystem
            self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
        
        current_area = getattr(self.game.current_player, 'current_area', None)
        self.game.skill_system.attempt_listening(self.game.current_player, current_area)
        
        return True
    
    # Skill & Utility Commands
    def cmd_pick(self, args: List[str]) -> bool:
        """Pick locks on doors or containers."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Pick what?")
            return True
        
        # Initialize skill system if needed
        if not hasattr(self.game, 'skill_system'):
            from .skill_system import SkillSystem
            self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
        
        target = ' '.join(args)
        from .skill_system import SkillDifficulty
        self.game.skill_system.attempt_lockpicking(self.game.current_player, target, SkillDifficulty.MODERATE)
        
        return True
    
    def cmd_disarm(self, args: List[str]) -> bool:
        """Disarm detected traps."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Disarm what?")
            return True
        
        # Initialize skill system if needed
        if not hasattr(self.game, 'skill_system'):
            from .skill_system import SkillSystem
            self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
        
        trap_name = ' '.join(args)
        self.game.skill_system.attempt_trap_disarmament(self.game.current_player, trap_name)
        
        return True
    
    def cmd_backstab(self, args: List[str]) -> bool:
        """Perform a backstab attack on an enemy."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Backstab whom?")
            return True
        
        # Initialize stealth system if needed
        if not hasattr(self.game, 'stealth_system'):
            from .stealth_system import StealthSystem
            self.game.stealth_system = StealthSystem(self.game.dice_system, self.game.ui_manager)
        
        # Check if in combat
        if not (hasattr(self.game, 'combat_system') and self.game.combat_system.is_active()):
            self.game.ui_manager.log_error("You can only backstab in combat!")
            return True
        
        target_name = ' '.join(args)
        
        # Attempt backstab (this would integrate with combat system)
        success, multiplier = self.game.stealth_system.attempt_backstab(self.game.current_player, None)
        
        if success:
            self.game.ui_manager.log_info(f"You attempt to backstab {target_name} from the shadows!")
            # This would trigger a special attack in the combat system
            # For now, just use regular attack with message
            return self.cmd_attack([target_name])
        
        return True
    
    def cmd_steal(self, args: List[str]) -> bool:
        """Attempt to pickpocket from NPCs."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if len(args) < 2:
            self.game.ui_manager.log_error("Usage: steal <item> <target>")
            return True
        
        # Initialize skill system if needed
        if not hasattr(self.game, 'skill_system'):
            from .skill_system import SkillSystem
            self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
        
        item_name = args[0]
        target_name = ' '.join(args[1:])
        
        self.game.ui_manager.log_info(f"You attempt to steal {item_name} from {target_name}...")
        self.game.skill_system.attempt_pickpocketing(self.game.current_player, target_name)
        
        return True
    
    def cmd_track(self, args: List[str]) -> bool:
        """Track creatures in the area."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Track what?")
            return True
        
        # Initialize skill system if needed
        if not hasattr(self.game, 'skill_system'):
            from .skill_system import SkillSystem
            self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
        
        creature_name = ' '.join(args)
        self.game.skill_system.attempt_tracking(self.game.current_player, creature_name)
        
        return True
    
    def cmd_forage(self, args: List[str]) -> bool:
        """Forage for food and natural items."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        self.game.ui_manager.log_info("You search the area for useful natural items...")
        
        # Simple foraging implementation
        import random
        if random.randint(1, 100) <= 30:  # 30% success rate
            found_items = ["some berries", "edible roots", "medicinal herbs", "fresh water"]
            found = random.choice(found_items)
            self.game.ui_manager.log_success(f"You find {found}!")
        else:
            self.game.ui_manager.log_info("You don't find anything useful here.")
        
        return True
    
    # Combat Enhancement Commands
    def cmd_dual(self, args: List[str]) -> bool:
        """Toggle dual-wielding mode."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.toggle_dual_wield(self.game.current_player)
        else:
            self.game.ui_manager.log_error("Combat system not available.")
        
        return True
    
    def cmd_defend(self, args: List[str]) -> bool:
        """Enter defensive fighting stance."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.enter_defensive_stance(self.game.current_player)
        else:
            self.game.ui_manager.log_error("Combat system not available.")
        
        return True
    
    def cmd_block(self, args: List[str]) -> bool:
        """Attempt to block with shield."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.attempt_block(self.game.current_player)
        else:
            self.game.ui_manager.log_error("Combat system not available.")
        
        return True
    
    def cmd_parry(self, args: List[str]) -> bool:
        """Attempt to parry with weapon."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.attempt_parry(self.game.current_player)
        else:
            self.game.ui_manager.log_error("Combat system not available.")
        
        return True
    
    def cmd_charge(self, args: List[str]) -> bool:
        """Execute a charging attack."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        target_name = ' '.join(args) if args else None
        
        if hasattr(self.game, 'combat_system'):
            self.game.combat_system.attempt_charge_attack(self.game.current_player, target_name)
        else:
            self.game.ui_manager.log_error("Combat system not available.")
        
        return True
    
    def cmd_aim(self, args: List[str]) -> bool:
        """Aim carefully for ranged attacks."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Aim at what?")
            return True
        
        target_name = ' '.join(args)
        self.game.ui_manager.log_success(f"You take careful aim at {target_name}.")
        self.game.ui_manager.log_system("[Next ranged attack gets +2 accuracy bonus]")
        
        # Set aiming flag on character
        self.game.current_player._aiming = True
        
        return True
    
    # Magic & Class Ability Commands
    def cmd_cast(self, args: List[str]) -> bool:
        """Cast a spell."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        player = self.game.current_player
        
        if not args:
            self.game.ui_manager.log_error("Cast what spell?")
            if hasattr(player, 'known_spells') and player.known_spells:
                self.game.ui_manager.log_info(f"Known spells: {', '.join(player.known_spells)}")
            return True
        
        # Check if player can cast spells
        if not player.is_spellcaster():
            self.game.ui_manager.log_error("You don't know how to cast spells.")
            return True
        
        # Initialize spell system if needed
        if not hasattr(self.game, 'spell_system'):
            from core.spell_system import SpellSystem
            self.game.spell_system = SpellSystem(self.game.dice_system, self.game.ui_manager)
        
        # Parse spell name and target
        spell_name = args[0].lower().replace(' ', '_')
        target_name = ' '.join(args[1:]) if len(args) > 1 else None
        
        # Check if in combat and use combat spell casting
        if hasattr(self.game, 'combat_system') and self.game.combat_system.is_active():
            success = self.game.combat_system.cast_spell_in_combat(spell_name, target_name)
        else:
            # Out of combat spell casting
            target = None
            if target_name:
                if target_name.lower() in ['self', 'me']:
                    target = player
                else:
                    # Mock target for testing - in real game would resolve from current area
                    target = {'name': target_name, 'type': 'enemy'}
            
            # Attempt to cast the spell
            success, message, effects_data = self.game.spell_system.cast_spell(
                player, spell_name, target, self.game.combat_system if hasattr(self.game, 'combat_system') else None
            )
            
            if not success:
                self.game.ui_manager.log_error(message)
        
        return True
    
    def cmd_meditate(self, args: List[str]) -> bool:
        """Meditate to recover mana or ki."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        player = self.game.current_player
        
        # Check if player can meditate
        if not player.is_spellcaster():
            self.game.ui_manager.log_error("You don't know how to meditate.")
            return True
        
        # Initialize magic system if needed
        if not hasattr(self.game, 'magic_system'):
            from core.magic_system import MagicSystem
            self.game.magic_system = MagicSystem()
        
        success, message, recovery = self.game.magic_system.meditate(player)
        
        if success:
            self.game.ui_manager.log_success(message)
        else:
            self.game.ui_manager.log_error(message)
        
        return True
    
    def cmd_spells(self, args: List[str]) -> bool:
        """Show known spells and mana status."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        player = self.game.current_player
        
        if not player.is_spellcaster():
            self.game.ui_manager.log_error("You don't know any spells.")
            return True
        
        # Show mana status
        mana_status = f"Mana: {player.current_mana}/{player.max_mana}"
        mana_percent = int(player.get_mana_percentage() * 100)
        self.game.ui_manager.log_info(f"{mana_status} ({mana_percent}%)")
        
        # Show known spells
        if not player.known_spells:
            self.game.ui_manager.log_info("You don't know any spells yet.")
            return True
        
        self.game.ui_manager.log_info("Known Spells:")
        
        # Initialize spell system to get spell details
        if not hasattr(self.game, 'spell_system'):
            from core.spell_system import SpellSystem
            self.game.spell_system = SpellSystem()
        
        for spell_name in player.known_spells:
            spell_data = self.game.spell_system.get_spell_data(spell_name)
            if spell_data:
                mana_cost = spell_data.get('mana_cost', '?')
                level = spell_data.get('level', '?')
                school = spell_data.get('school', '?').title()
                description = spell_data.get('description', 'Unknown spell')
                self.game.ui_manager.log_info(f"  {spell_data['name']} (Level {level} {school}, {mana_cost} mana)")
                self.game.ui_manager.log_info(f"    {description}")
            else:
                self.game.ui_manager.log_info(f"  {spell_name} (Unknown spell)")
        
        return True
    
    def cmd_turn_undead(self, args: List[str]) -> bool:
        """Turn undead creatures (Paladin/Missionary ability)."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        char_class = getattr(self.game.current_player, 'character_class', '').lower()
        if char_class not in ['paladin', 'missionary']:
            self.game.ui_manager.log_error("You don't have the ability to turn undead.")
            return True
        
        self.game.ui_manager.log_info("You raise your holy symbol and call upon divine power!")
        self.game.ui_manager.log_success("Undead creatures cower before your divine presence!")
        
        # In full implementation, would affect undead enemies in combat
        
        return True
    
    def cmd_lay_hands(self, args: List[str]) -> bool:
        """Heal through laying on of hands (Paladin ability)."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        char_class = getattr(self.game.current_player, 'character_class', '').lower()
        if char_class not in ['paladin']:
            self.game.ui_manager.log_error("You don't have the ability to lay on hands.")
            return True
        
        target_name = ' '.join(args) if args else "yourself"
        
        self.game.ui_manager.log_info(f"You place your hands upon {target_name} and channel divine healing...")
        
        # Calculate healing based on level
        level = getattr(self.game.current_player, 'level', 1)
        healing = level * 2
        
        self.game.ui_manager.log_success(f"{target_name.title()} {'are' if target_name != 'yourself' else 'is'} healed for {healing} hit points!")
        
        return True
    
    def cmd_sing(self, args: List[str]) -> bool:
        """Sing bardic songs for party benefits."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        char_class = getattr(self.game.current_player, 'character_class', '').lower()
        if char_class not in ['bard']:
            self.game.ui_manager.log_error("You don't know any bardic songs.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Sing what song?")
            return True
        
        song_name = ' '.join(args)
        self.game.ui_manager.log_success(f"You begin singing '{song_name}'...")
        self.game.ui_manager.log_info("Your inspiring melody fills the air!")
        
        # In full implementation, would provide party buffs
        
        return True
    
    def cmd_shapeshift(self, args: List[str]) -> bool:
        """Shapeshift into animal forms (Druid ability)."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        char_class = getattr(self.game.current_player, 'character_class', '').lower()
        if char_class not in ['druid']:
            self.game.ui_manager.log_error("You don't have the ability to shapeshift.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Shapeshift into what form?")
            return True
        
        form_name = ' '.join(args)
        valid_forms = ['wolf', 'bear', 'eagle', 'panther', 'human']
        
        if form_name.lower() not in valid_forms:
            self.game.ui_manager.log_error(f"You don't know how to become a {form_name}.")
            self.game.ui_manager.log_info(f"Available forms: {', '.join(valid_forms)}")
            return True
        
        self.game.ui_manager.log_success(f"You transform into a {form_name}!")
        self.game.ui_manager.log_system(f"[Shapeshift: You are now in {form_name} form]")
        
        return True
    
    def cmd_skills(self, args: List[str]) -> bool:
        """Display character's skill bonuses and abilities."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Initialize skill system if needed
        if not hasattr(self.game, 'skill_system'):
            from .skill_system import SkillSystem
            self.game.skill_system = SkillSystem(self.game.dice_system, self.game.ui_manager)
        
        # Display character skills using the skill system
        self.game.skill_system.display_character_skills(self.game.current_player)
        
        return True
    
    # Commerce & Economy Commands
    def cmd_buy(self, args: List[str]) -> bool:
        """Buy item from a merchant."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Check if we're near a merchant
        merchants = self._get_nearby_merchants()
        if not merchants:
            self.game.ui_manager.log_error("There are no merchants here.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Buy what? Use 'list' to see what's for sale.")
            return True
        
        # Get the active merchant (first one found)
        merchant = merchants[0]
        
        # Initialize merchant system if needed
        if not hasattr(self.game, 'merchant_system'):
            from .merchant_system import MerchantSystem
            self.game.merchant_system = MerchantSystem(self.game)
        
        # Parse item name and quantity
        item_name = ' '.join(args).lower()
        quantity = 1
        
        # Check if quantity specified (e.g., "buy 3 potions")
        if args[0].isdigit():
            try:
                quantity = int(args[0])
                item_name = ' '.join(args[1:]).lower()
            except (ValueError, IndexError):
                self.game.ui_manager.log_error("Invalid quantity.")
                return True
        
        # Find item in merchant's inventory
        item_id = self._find_item_in_merchant_inventory(merchant, item_name)
        if not item_id:
            self.game.ui_manager.log_error(f"{merchant.name} doesn't sell '{item_name}'.")
            return True
        
        # Attempt purchase
        success, message = self.game.merchant_system.attempt_purchase(
            self.game.current_player, merchant, item_id, quantity
        )
        
        if success:
            self.game.ui_manager.log_success(message)
        else:
            self.game.ui_manager.log_error(message)
        
        return True
    
    def cmd_sell(self, args: List[str]) -> bool:
        """Sell item to a merchant."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Check if we're near a merchant
        merchants = self._get_nearby_merchants()
        if not merchants:
            self.game.ui_manager.log_error("There are no merchants here.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Sell what? Use 'inventory' to see what you have.")
            return True
        
        # Get the active merchant (first one found)
        merchant = merchants[0]
        
        # Initialize merchant system if needed
        if not hasattr(self.game, 'merchant_system'):
            from .merchant_system import MerchantSystem
            self.game.merchant_system = MerchantSystem(self.game)
        
        # Parse item name and quantity
        item_name = ' '.join(args).lower()
        quantity = 1
        
        # Check if quantity specified
        if args[0].isdigit():
            try:
                quantity = int(args[0])
                item_name = ' '.join(args[1:]).lower()
            except (ValueError, IndexError):
                self.game.ui_manager.log_error("Invalid quantity.")
                return True
        
        # Find item in player's inventory
        item_id = self._find_item_in_player_inventory(item_name)
        if not item_id:
            self.game.ui_manager.log_error(f"You don't have '{item_name}'.")
            return True
        
        # Attempt sale
        success, message = self.game.merchant_system.attempt_sale(
            self.game.current_player, merchant, item_id, quantity
        )
        
        if success:
            self.game.ui_manager.log_success(message)
        else:
            self.game.ui_manager.log_error(message)
        
        return True
    
    def cmd_list(self, args: List[str]) -> bool:
        """List merchant's inventory and prices."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Check if we're near a merchant
        merchants = self._get_nearby_merchants()
        if not merchants:
            self.game.ui_manager.log_error("There are no merchants here.")
            return True
        
        # Get the active merchant (first one found)
        merchant = merchants[0]
        
        # Initialize merchant system if needed
        if not hasattr(self.game, 'merchant_system'):
            from .merchant_system import MerchantSystem
            self.game.merchant_system = MerchantSystem(self.game)
        
        # Display merchant inventory
        inventory_display = self.game.merchant_system.get_merchant_inventory_display(
            merchant, self.game.current_player
        )
        self.game.ui_manager.log_info(inventory_display)
        
        return True
    
    def cmd_appraise(self, args: List[str]) -> bool:
        """Get an item's value estimate from a merchant."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Appraise what?")
            return True
        
        item_name = ' '.join(args).lower()
        
        # Find item in player's inventory
        item_id = self._find_item_in_player_inventory(item_name)
        if not item_id:
            self.game.ui_manager.log_error(f"You don't have '{item_name}'.")
            return True
        
        # Get the item
        item = self.game.current_player.inventory_system.get_item(item_id)
        if not item:
            self.game.ui_manager.log_error("Item not found.")
            return True
        
        # Check if we're near a merchant for better appraisal
        merchants = self._get_nearby_merchants()
        if merchants:
            merchant = merchants[0]
            
            # Initialize merchant system if needed
            if not hasattr(self.game, 'merchant_system'):
                from .merchant_system import MerchantSystem
                self.game.merchant_system = MerchantSystem(self.game)
            
            buy_price = self.game.merchant_system.calculate_sell_price(
                item, merchant, self.game.current_player
            )
            
            if buy_price.total_copper() > 0:
                self.game.ui_manager.log_info(
                    f"{merchant.name} examines your {item.name}.\n"
                    f"{merchant.name} says: \"I can offer you {buy_price} for this {item.name}.\""
                )
            else:
                self.game.ui_manager.log_info(
                    f"{merchant.name} examines your {item.name}.\n"
                    f"{merchant.name} says: \"I don't buy {item.item_type.value}s.\""
                )
        else:
            # Basic appraisal without merchant
            base_value = item.get_effective_value()
            condition = item.get_condition()
            
            self.game.ui_manager.log_info(
                f"You examine your {item.name}.\n"
                f"Base value: {base_value} gold\n"
                f"Condition: {condition}\n"
                f"A merchant might pay around {int(base_value * 0.6)} gold for this."
            )
        
        return True
    
    def cmd_repair(self, args: List[str]) -> bool:
        """Repair a damaged item at a blacksmith."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        # Check if we're near a blacksmith
        merchants = self._get_nearby_merchants()
        blacksmiths = [m for m in merchants if m.merchant_type.value == "blacksmith"]
        if not blacksmiths:
            self.game.ui_manager.log_error("You need to find a blacksmith to repair items.")
            return True
        
        if not args:
            self.game.ui_manager.log_error("Repair what?")
            return True
        
        item_name = ' '.join(args).lower()
        
        # Find item in player's inventory
        item_id = self._find_item_in_player_inventory(item_name)
        if not item_id:
            self.game.ui_manager.log_error(f"You don't have '{item_name}'.")
            return True
        
        # Get the item
        item = self.game.current_player.inventory_system.get_item(item_id)
        if not item:
            self.game.ui_manager.log_error("Item not found.")
            return True
        
        # Check if item needs repair
        if item.condition_percentage >= 100.0:
            self.game.ui_manager.log_info(f"Your {item.name} is already in perfect condition.")
            return True
        
        # Calculate repair cost
        from .item_condition_system import ItemConditionSystem
        condition_system = ItemConditionSystem()
        repair_cost = condition_system.calculate_repair_cost(
            item.value, item.condition_percentage, 100.0
        )
        
        # Check if player can afford repair
        from .currency_system import Currency
        cost_currency = Currency(gold=repair_cost)
        
        if not self.game.current_player.currency.can_afford(cost_currency):
            self.game.ui_manager.log_error(
                f"Repair costs {cost_currency}, but you only have {self.game.current_player.currency}."
            )
            return True
        
        # Perform repair
        blacksmith = blacksmiths[0]
        self.game.current_player.currency.subtract(cost_currency)
        item.repair_item(100.0 - item.condition_percentage)  # Repair to perfect
        
        self.game.ui_manager.log_success(
            f"{blacksmith.name} repairs your {item.name} for {cost_currency}.\n"
            f"Your {item.name} is now in perfect condition!"
        )
        
        return True
    
    def cmd_wealth(self, args: List[str]) -> bool:
        """Display character's current wealth."""
        if not self.game.current_player:
            self.game.ui_manager.log_error("No character loaded.")
            return True
        
        currency = self.game.current_player.currency
        if currency:
            self.game.ui_manager.log_info(f"Your wealth: {currency}")
            if currency.total_copper() >= 100:
                self.game.ui_manager.log_info(f"Total value: {currency.display_total_gold()}")
        else:
            self.game.ui_manager.log_info("You have no money.")
        
        return True
    
    # Helper methods for commerce commands
    def _get_nearby_merchants(self) -> List:
        """Get merchants in the current location."""
        if not hasattr(self.game, 'merchant_system'):
            from .merchant_system import MerchantSystem
            self.game.merchant_system = MerchantSystem(self.game)
        
        if not self.game.current_player.current_area or not self.game.current_player.current_room:
            return []
        
        merchants = self.game.merchant_system.get_merchants_in_area(
            self.game.current_player.current_area,
            self.game.current_player.current_room
        )
        
        # Filter out hidden merchants the player hasn't discovered
        discovered_merchants = []
        for merchant in merchants:
            if merchant.is_hidden:
                if self.game.merchant_system.is_merchant_discovered(
                    self.game.current_player.name, merchant.merchant_id
                ):
                    discovered_merchants.append(merchant)
            else:
                discovered_merchants.append(merchant)
        
        return discovered_merchants
    
    def _find_item_in_merchant_inventory(self, merchant, item_name: str) -> Optional[str]:
        """Find item ID in merchant's inventory by name."""
        from .item_factory import ItemFactory
        item_factory = ItemFactory()
        
        for item_id in merchant.inventory:
            if merchant.inventory[item_id] > 0:
                item = item_factory.create_item(item_id)
                if item and item_name in item.name.lower():
                    return item_id
        
        return None
    
    def _find_item_in_player_inventory(self, item_name: str) -> Optional[str]:
        """Find item ID in player's inventory by name."""
        if not self.game.current_player.inventory_system:
            return None
        
        # Get all items in inventory
        for item_id, quantity in self.game.current_player.inventory_system.items.items():
            if quantity > 0:
                item = self.game.current_player.inventory_system.get_item(item_id)
                if item and item_name in item.name.lower():
                    return item_id
        
        return None

    # === SOCIAL & CONVERSATION COMMANDS ===
    
    def cmd_talk(self, args: List[str]) -> str:
        """Talk to an NPC to start a conversation."""
        if not args:
            return "Talk to whom?"
        
        target_name = ' '.join(args).lower()
        
        # Initialize conversation engine if not already done
        if not hasattr(self.game, 'conversation_engine'):
            from core.conversation_engine import ConversationEngine
            self.game.conversation_engine = ConversationEngine(self.game)
        
        try:
            return self.game.conversation_engine.handle_talk_command(
                self.game.current_player, target_name
            )
        except Exception as e:
            return f"Could not talk to {target_name}. {str(e)}"
    
    def cmd_say(self, args: List[str]) -> str:
        """Say something out loud in the current area."""
        if not args:
            return "Say what?"
        
        message = ' '.join(args)
        player_name = self.game.current_player.name
        
        # Remove quotes if present
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]
        
        return f"You say: \"{message}\""
    
    def cmd_tell(self, args: List[str]) -> str:
        """Tell something specific to an NPC."""
        if len(args) < 2:
            return "Usage: tell <person> <message>"
        
        target_name = args[0].lower()
        message = ' '.join(args[1:])
        
        # Initialize conversation engine if not already done
        if not hasattr(self.game, 'conversation_engine'):
            from core.conversation_engine import ConversationEngine
            self.game.conversation_engine = ConversationEngine(self.game)
        
        try:
            return self.game.conversation_engine.handle_tell_command(
                self.game.current_player, target_name, message
            )
        except Exception as e:
            return f"Could not tell {target_name} anything. {str(e)}"
    
    def cmd_ask(self, args: List[str]) -> str:
        """Ask an NPC about a specific topic or for missions."""
        if len(args) < 2:
            return "Usage: ask <person> <topic> or ask <person> missions"
        
        target_name = args[0].lower()
        
        # Handle quest-specific "ask <npc> missions" command
        if len(args) == 2 and args[1].lower() in ['missions', 'mission', 'quest', 'quests', 'task', 'tasks']:
            return self._handle_ask_missions(target_name)
        
        # Standard ask command format: ask <person> about <topic>
        if len(args) < 3 or args[1].lower() != 'about':
            return "Usage: ask <person> about <topic> or ask <person> missions"
        
        topic = ' '.join(args[2:]).lower()
        
        # Initialize conversation engine if not already done
        if not hasattr(self.game, 'conversation_engine'):
            from core.conversation_engine import ConversationEngine
            self.game.conversation_engine = ConversationEngine(self.game)
        
        try:
            return self.game.conversation_engine.handle_ask_command(
                self.game.current_player, target_name, topic
            )
        except Exception as e:
            return f"Could not ask {target_name} about {topic}. {str(e)}"
    
    def _handle_ask_missions(self, target_name: str) -> str:
        """Handle asking NPCs for missions/quests"""
        # Check if target is a quest giver
        from npcs.quest_giver_npc import create_quest_giver
        
        # Try to create quest giver by name mapping
        npc_id_map = {
            'annora': 'chancellor_annora',
            'chancellor': 'chancellor_annora',
            'chancellor annora': 'chancellor_annora',
            'traveller': 'hooded_traveller',
            'hooded': 'hooded_traveller',
            'hooded traveller': 'hooded_traveller',
            'balthazar': 'balthazar_dark_lord',
            'dark lord': 'balthazar_dark_lord',
            'balthazar dark lord': 'balthazar_dark_lord'
        }
        
        npc_id = npc_id_map.get(target_name)
        if not npc_id:
            return f"{target_name} doesn't appear to offer missions."
        
        quest_giver = create_quest_giver(npc_id)
        if not quest_giver:
            return f"{target_name} is not available to give missions."
        
        # Initialize quest system if needed
        if not hasattr(self.game, 'quest_system'):
            from core.quest_system import QuestSystem
            self.game.quest_system = QuestSystem(self.game)
        
        if not hasattr(self.game.current_player, 'quest_manager'):
            from core.quest_manager import CharacterQuestManager
            self.game.current_player.quest_manager = CharacterQuestManager(
                self.game.current_player, self.game.quest_system
            )
        
        # Set game reference for quest giver
        self.game.current_player.game_engine = self.game
        
        try:
            return quest_giver.handle_ask_missions(self.game.current_player)
        except Exception as e:
            return f"Error asking {target_name} for missions: {str(e)}"
    
    def cmd_greet(self, args: List[str]) -> str:
        """Formally greet an NPC."""
        if not args:
            return "Greet whom?"
        
        target_name = ' '.join(args).lower()
        
        # Initialize conversation engine if not already done
        if not hasattr(self.game, 'conversation_engine'):
            from core.conversation_engine import ConversationEngine
            self.game.conversation_engine = ConversationEngine(self.game)
        
        try:
            return self.game.conversation_engine.handle_greet_command(
                self.game.current_player, target_name
            )
        except Exception as e:
            return f"Could not greet {target_name}. {str(e)}"
    
    def cmd_whisper(self, args: List[str]) -> str:
        """Whisper something to an NPC."""
        if len(args) < 2:
            return "Usage: whisper <person> <message>"
        
        target_name = args[0].lower()
        message = ' '.join(args[1:])
        
        # Initialize conversation engine if not already done
        if not hasattr(self.game, 'conversation_engine'):
            from core.conversation_engine import ConversationEngine
            self.game.conversation_engine = ConversationEngine(self.game)
        
        try:
            return self.game.conversation_engine.handle_whisper_command(
                self.game.current_player, target_name, message
            )
        except Exception as e:
            return f"Could not whisper to {target_name}. {str(e)}"
    
    def cmd_broadcast(self, args: List[str]) -> str:
        """Broadcast a message publicly."""
        if not args:
            return "Broadcast what?"
        
        message = ' '.join(args)
        player_name = self.game.current_player.name
        
        # Remove quotes if present
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]
        
        return f"{player_name} broadcasts: \"{message}\""
    
    # === QUEST SYSTEM COMMANDS ===
    
    def cmd_quest(self, args: List[str]) -> str:
        """Display quest information and manage quests."""
        # Initialize quest system if not already done
        if not hasattr(self.game, 'quest_system'):
            from core.quest_system import QuestSystem
            self.game.quest_system = QuestSystem(self.game)
        
        if not hasattr(self.game.current_player, 'quest_manager'):
            from core.quest_manager import CharacterQuestManager
            self.game.current_player.quest_manager = CharacterQuestManager(
                self.game.current_player, self.game.quest_system
            )
        
        quest_manager = self.game.current_player.quest_manager
        
        if not args:
            # Display quest journal
            return self._format_quest_journal(quest_manager.get_journal())
        
        subcommand = args[0].lower()
        
        if subcommand == 'log' or subcommand == 'journal':
            return self._format_quest_journal(quest_manager.get_journal())
        elif subcommand == 'info' and len(args) > 1:
            quest_name = ' '.join(args[1:]).lower()
            return self._format_quest_info(quest_manager, quest_name)
        elif subcommand == 'available':
            available_quests = quest_manager.get_available_quests()
            return self._format_available_quests(available_quests)
        else:
            return ("Quest commands:\n"
                   "  quest           - Show quest journal\n"
                   "  quest log       - Show quest journal\n"
                   "  quest info <quest> - Show detailed quest information\n"
                   "  quest available - Show available quests\n"
                   "  accept <quest>  - Accept a quest\n"
                   "  abandon <quest> - Abandon a quest")
    
    def cmd_accept_quest(self, args: List[str]) -> str:
        """Accept a quest from an NPC or by name."""
        if not args:
            return "Accept which quest? Use 'quest available' to see available quests."
        
        # Initialize quest system
        if not hasattr(self.game, 'quest_system'):
            from core.quest_system import QuestSystem
            self.game.quest_system = QuestSystem(self.game)
        
        if not hasattr(self.game.current_player, 'quest_manager'):
            from core.quest_manager import CharacterQuestManager
            self.game.current_player.quest_manager = CharacterQuestManager(
                self.game.current_player, self.game.quest_system
            )
        
        quest_manager = self.game.current_player.quest_manager
        quest_name = ' '.join(args).lower()
        
        # Find quest by name
        available_quests = quest_manager.get_available_quests()
        target_quest = None
        
        for quest in available_quests:
            if quest_name in quest.name.lower():
                target_quest = quest
                break
        
        if not target_quest:
            return f"Quest '{quest_name}' not found or not available."
        
        # Accept the quest
        if quest_manager.accept_quest(target_quest.quest_id):
            return f"You have accepted the quest: {target_quest.name}"
        else:
            return f"You cannot accept '{target_quest.name}' at this time."
    
    def cmd_abandon_quest(self, args: List[str]) -> str:
        """Abandon an active quest."""
        if not args:
            return "Abandon which quest? Use 'quest' to see active quests."
        
        # Initialize quest system
        if not hasattr(self.game, 'quest_system'):
            from core.quest_system import QuestSystem
            self.game.quest_system = QuestSystem(self.game)
        
        if not hasattr(self.game.current_player, 'quest_manager'):
            from core.quest_manager import CharacterQuestManager
            self.game.current_player.quest_manager = CharacterQuestManager(
                self.game.current_player, self.game.quest_system
            )
        
        quest_manager = self.game.current_player.quest_manager
        quest_name = ' '.join(args).lower()
        
        # Find active quest by name
        active_quests = quest_manager.get_journal()['active']
        target_quest_id = None
        
        for quest_info in active_quests:
            if quest_name in quest_info['name'].lower():
                target_quest_id = quest_info['quest_id']
                break
        
        if not target_quest_id:
            return f"Active quest '{quest_name}' not found."
        
        # Confirm abandonment
        quest = self.game.quest_system.quest_definitions.get(target_quest_id)
        if quest:
            consequences = quest.abandon_consequences
            warning = ""
            if consequences:
                warning = " Warning: Abandoning this quest may have consequences."
            
            # For now, abandon immediately. In a full implementation, 
            # you might want to add a confirmation system
            if quest_manager.abandon_quest(target_quest_id):
                return f"You have abandoned the quest: {quest.name}.{warning}"
            else:
                return f"Could not abandon quest '{quest.name}'."
        
        return f"Quest '{quest_name}' not found."
    
    def cmd_quest_journal(self, args: List[str]) -> str:
        """Display the quest journal."""
        # Initialize quest system
        if not hasattr(self.game, 'quest_system'):
            from core.quest_system import QuestSystem
            self.game.quest_system = QuestSystem(self.game)
        
        if not hasattr(self.game.current_player, 'quest_manager'):
            from core.quest_manager import CharacterQuestManager
            self.game.current_player.quest_manager = CharacterQuestManager(
                self.game.current_player, self.game.quest_system
            )
        
        quest_manager = self.game.current_player.quest_manager
        return self._format_quest_journal(quest_manager.get_journal())
    
    def _format_quest_journal(self, journal: Dict[str, Any]) -> str:
        """Format the quest journal for display."""
        output = []
        output.append(f"=== QUEST JOURNAL - {journal['character_name'].upper()} ===")
        output.append(f"Level {journal['character_level']} {journal['character_alignment']} Character")
        output.append("")
        
        # Active quests
        if journal['active']:
            output.append("ACTIVE QUESTS:")
            for quest in journal['active']:
                status_icon = "★"
                output.append(f"{status_icon} [{quest['alignment_requirement'].upper()}] {quest['name']}")
                output.append(f"  Step {quest.get('current_step', 1)}: {quest.get('current_objective', 'Unknown')}")
                exp_reward = quest['rewards'].get('experience', 0)
                output.append(f"  Reward: {exp_reward:,} experience + bonuses")
                output.append("")
        else:
            output.append("ACTIVE QUESTS: None")
            output.append("")
        
        # Completed quests
        if journal['completed']:
            output.append("COMPLETED QUESTS:")
            for quest in journal['completed']:
                output.append(f"✓ {quest['name']} ({quest['experience']:,} exp)")
        else:
            output.append("COMPLETED QUESTS: None")
        
        output.append("")
        
        # Available quests
        if journal['available']:
            output.append("AVAILABLE QUESTS:")
            for quest in journal['available']:
                exp_reward = quest['rewards'].get('experience', 0)
                output.append(f"○ [{quest['alignment_requirement'].upper()}] {quest['name']}")
                output.append(f"  Requirement: Level {quest['level_requirement']}+")
                output.append(f"  Reward: {exp_reward:,} experience + bonuses")
        else:
            output.append("AVAILABLE QUESTS: None")
        
        output.append("")
        
        # Failed quests
        if journal['failed']:
            output.append("FAILED QUESTS:")
            for quest in journal['failed']:
                output.append(f"✗ {quest['name']} - {quest['reason']}")
        
        output.append("")
        output.append("Commands: quest, accept <quest>, abandon <quest>, quest info <quest>")
        
        return '\n'.join(output)
    
    def _format_quest_info(self, quest_manager, quest_name: str) -> str:
        """Format detailed quest information."""
        # Find quest by name
        all_quests = []
        all_quests.extend(quest_manager.get_available_quests())
        
        journal = quest_manager.get_journal()
        for quest_info in journal['active']:
            quest_id = quest_info['quest_id']
            if quest_id in quest_manager.quest_system.quest_definitions:
                all_quests.append(quest_manager.quest_system.quest_definitions[quest_id])
        
        target_quest = None
        for quest in all_quests:
            if quest_name in quest.name.lower():
                target_quest = quest
                break
        
        if not target_quest:
            return f"Quest '{quest_name}' not found."
        
        quest_info = quest_manager.get_quest_info(target_quest.quest_id)
        if not quest_info:
            return f"Could not get information for quest '{quest_name}'."
        
        output = []
        output.append(f"=== QUEST DETAILS: {quest_info['name'].upper()} ===")
        output.append(f"Quest Giver: {quest_info['quest_giver']}")
        output.append(f"Alignment: {quest_info['alignment_requirement'].title()} required")
        output.append(f"Level Requirement: {quest_info['level_requirement']}+")
        output.append(f"Status: {quest_info['status'].title()}")
        
        if quest_info['status'] == 'active':
            output.append(f"Current Step: {quest_info.get('current_step', 1)}")
            output.append(f"Objective: {quest_info.get('current_objective', 'Unknown')}")
        
        output.append("")
        output.append("DESCRIPTION:")
        output.append(target_quest.description)
        output.append("")
        
        # Rewards
        rewards = quest_info['rewards']
        output.append("REWARDS:")
        if 'experience' in rewards:
            output.append(f"- {rewards['experience']:,} experience points")
        if 'gold' in rewards:
            output.append(f"- {rewards['gold']} gold pieces")
        if 'items' in rewards:
            for item in rewards['items']:
                output.append(f"- {item}")
        
        # Class-specific rewards
        if 'class_specific' in rewards:
            char_class = quest_manager.character.character_class.class_name.lower()
            if char_class in rewards['class_specific']:
                output.append(f"- Class bonus ({char_class}): {rewards['class_specific'][char_class]}")
        
        if quest_info['status'] == 'locked':
            output.append("")
            output.append(f"REQUIREMENT: {quest_info.get('lock_reason', 'Unknown requirement')}")
        
        return '\n'.join(output)
    
    def _format_available_quests(self, quests: List) -> str:
        """Format available quests for display."""
        if not quests:
            return "No quests available at your current level and alignment."
        
        output = []
        output.append("=== AVAILABLE QUESTS ===")
        output.append("")
        
        for quest in quests:
            exp_reward = quest.rewards.get('experience', 0)
            output.append(f"[{quest.alignment_requirement.upper()}] {quest.name}")
            output.append(f"  Quest Giver: {quest.quest_giver}")
            output.append(f"  Level Requirement: {quest.level_requirement}+")
            output.append(f"  Reward: {exp_reward:,} experience + bonuses")
            output.append(f"  Description: {quest.description}")
            output.append("")
        
        output.append("Use 'accept <quest name>' to accept a quest.")
        return '\n'.join(output)