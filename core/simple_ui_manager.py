"""
Simple UI Manager for Rogue City
Traditional MajorMUD-style single-scrolling terminal interface.
"""

import sys
import threading
import time
from typing import Optional
from collections import deque
from .color_manager import ColorManager


class SimpleUIManager:
    """
    Simple terminal interface manager using traditional MajorMUD-style output.
    Single scrolling output with command input at bottom.
    """
    
    def __init__(self):
        """Initialize the simple UI manager."""
        self.command_history: deque = deque(maxlen=100)
        self.history_index = 0
        self.current_input = ""
        self.input_prompt = "> "
        self.color_manager = ColorManager()
        
        # Status line settings (MajorMUD style)
        self.show_status_line = True
        self.current_character = None
        
    def initialize(self) -> bool:
        """
        Initialize the simple terminal interface.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Clear screen and show welcome
            self.clear_screen()
            self.print_header()
            return True
        except Exception as e:
            print(f"Failed to initialize UI: {e}")
            return False
            
    def cleanup(self) -> None:
        """Clean up the interface."""
        print("\nThank you for playing Rogue City!")
        
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        # Cross-platform clear screen
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self) -> None:
        """Print the game header."""
        print("=" * 60)
        print("    ROGUE CITY - A MajorMUD-Style Text RPG")
        print("=" * 60)
        print()
        
    def output(self, message: str, prefix: str = "") -> None:
        """
        Output a message to the terminal.
        
        Args:
            message: The message to display
            prefix: Optional prefix (e.g., "ERROR:", "SUCCESS:")
        """
        if prefix:
            print(f"{prefix} {message}")
        else:
            print(message)
        sys.stdout.flush()
        
    def log_message(self, message: str) -> None:
        """Log a regular message."""
        self.output(message)
        
    def log_error(self, message: str) -> None:
        """Log an error message."""
        colored_message = self.color_manager.format_error_message(message)
        self.output(colored_message, "ERROR:")
        
    def log_success(self, message: str) -> None:
        """Log a success message."""
        colored_message = self.color_manager.format_success_message(message)
        self.output(colored_message)
        
    def log_info(self, message: str) -> None:
        """Log an info message."""
        colored_message = self.color_manager.format_info_message(message)
        self.output(colored_message)
        
    def log_system(self, message: str) -> None:
        """Log a system message."""
        colored_message = self.color_manager.format_system_message(message)
        self.output(colored_message, "[SYSTEM]")
        
    def log_command(self, command: str) -> None:
        """Log a command that was entered."""
        # Commands are echoed as part of input, no need to log separately
        pass
        
    def log_combat(self, message: str) -> None:
        """Log a combat message with distinctive formatting."""
        colored_message = self.color_manager.format_combat_message(message)
        self.output(colored_message)
        
    def log_critical(self, message: str) -> None:
        """Log a critical hit or important message with special formatting."""
        colored_message = self.color_manager.format_critical_message(message)
        self.output(colored_message)
        
    def colorize_enemy(self, enemy_name: str) -> str:
        """Colorize enemy name for combat messages."""
        return self.color_manager.colorize(enemy_name, 'enemy')
        
    def show_room(self, name: str, description: str, exits: list, items: list = None, enemies: list = None) -> None:
        """
        Display room information in MajorMUD style.
        
        Args:
            name: Room name
            description: Room description
            exits: List of available exits
            items: Optional list of items in room
            enemies: Optional list of enemies in room
        """
        print()
        print(name)
        print(description)
        
        if exits:
            colored_exits = self.color_manager.colorize_exits_list(exits)
            print(f"Exits: {', '.join(colored_exits)}")
        else:
            print("No obvious exits.")
            
        if items:
            colored_items = self.color_manager.colorize_items_list(items)
            print(f"Items: {', '.join(colored_items)}")
            
        if enemies:
            colored_enemies = self.color_manager.colorize_enemies_list(enemies)
            print(f"Enemies: {', '.join(colored_enemies)}")
        print()
        
    def show_character_status(self, character) -> None:
        """
        Display character status in MajorMUD style.
        
        Args:
            character: Character object to display
        """
        print()
        print(f"{character.name} the {character.character_class.title()} (Level {character.level}, HP: {character.current_hp}/{character.max_hp})")
        
        # Show mana for mages
        if hasattr(character, 'current_mana') and character.max_mana > 0:
            print(f"Mana: {character.current_mana}/{character.max_mana}")
            
        print(f"AC: {character.armor_class}  Attack Bonus: {character.base_attack_bonus:+d}")
        
        # Show stats with modifiers
        stats_line = []
        for stat, value in character.stats.items():
            modifier = character.get_stat_modifier(stat)
            mod_str = f"({modifier:+d})" if modifier != 0 else "(+0)"
            stats_line.append(f"{stat.upper()[:3]}: {value}{mod_str}")
            
        print("  ".join(stats_line))
        print()
        
    def show_character_creation_class_selection(self, classes: dict) -> None:
        """Show class selection for character creation."""
        print("\n=== CHARACTER CREATION ===")
        print("\nStep 1: Choose Your Class")
        print("\nAvailable Classes:")
        print("(Experience penalties show cost increase for leveling)")
        print()
        
        class_count = len(classes)
        
        for i, (class_id, class_info) in enumerate(classes.items(), 1):
            name = class_info['name']
            exp_penalty = class_info.get('experience_penalty', class_info.get('difficulty', 0))
            description = class_info['description']
            
            if exp_penalty > 0:
                print(f"{i:2d}. {name} (+{exp_penalty}% exp)")
            else:
                print(f"{i:2d}. {name} (Normal exp)")
            print(f"    {description}")
            print()
            
        print(f"Enter the number of your choice (1-{class_count}):")
        
    def show_character_creation_class_confirmation(self, class_info: dict) -> None:
        """Show class confirmation details."""
        print("\n=== CHARACTER CREATION ===")
        print()
        print(f"Selected Class: {class_info['name']}")
        exp_penalty = class_info.get('experience_penalty', 0)
        if exp_penalty > 0:
            print(f"Experience Penalty: +{exp_penalty}%")
        else:
            print(f"Experience Penalty: Normal leveling")
        print()
        print(f"Description: {class_info['description']}")
        print()
        print("Stat Modifiers:")
        
        for stat, modifier in class_info['stat_modifiers'].items():
            sign = "+" if modifier >= 0 else ""
            print(f"  {stat.title()}: {sign}{modifier}")
            
        print()
        print(f"Hit Die: {class_info['hit_die']}")
        print("Combat: Turn-based attacks per round")
        
        # Show core class abilities if available
        if 'special_abilities' in class_info:
            print()
            print("Core Abilities:")
            abilities = class_info['special_abilities']
            ability_descriptions = {
                'magic_resistance': 'Magic Resistance',
                'anti_magic_aura': 'Anti-Magic Aura',
                'cannot_use_magic_items': 'Cannot Use Magic Items',
                'stealth_mastery': 'Stealth Mastery',
                'backstab': 'Backstab Attacks',
                'shield_mastery': 'Shield Mastery',
                'damage_resistance': 'Damage Resistance',
                'heavy_armor_proficiency': 'Heavy Armor Proficiency',
                'defensive_stance': 'Defensive Stance',
                'guardian_protection': 'Guardian Protection',
                'mana_system': 'Mana Spellcasting',
                'spell_mastery': 'Spell Mastery',
                'ki_system': 'Ki Powers',
                'unarmed_mastery': 'Unarmed Combat',
                'evasion_training': 'Evasion Training'
            }
            
            shown_abilities = []
            for ability, enabled in abilities.items():
                if enabled and ability in ability_descriptions:
                    shown_abilities.append(ability_descriptions[ability])
            
            if shown_abilities:
                # Show up to 4 core abilities
                for ability in shown_abilities[:4]:
                    print(f"  • {ability}")
                if len(shown_abilities) > 4:
                    print(f"  • And {len(shown_abilities) - 4} more abilities...")
        
        print()
        print("Confirm this choice? (y/n):")
        
    def show_character_creation_name_entry(self) -> None:
        """Show name entry step."""
        print("\n=== CHARACTER CREATION ===")
        print()
        print("Step 2: Choose Your Name")
        print()
        print("Enter your character's name:")
        print("(Must be unique and 1-20 characters)")
        
    def show_character_creation_name_confirmation(self, name: str) -> None:
        """Show name confirmation."""
        print("\n=== CHARACTER CREATION ===")
        print()
        print(f"Character Name: {name}")
        print()
        print("Confirm this name? (y/n):")
        
    def show_character_creation_stat_allocation(self, character) -> None:
        """Show stat allocation interface."""
        print("\n=== CHARACTER CREATION ===")
        print()
        print("Step 3: Allocate Stat Points")
        print()
        print(f"Character: {character.name} the {character.character_class.title()}")
        print(f"Points Remaining: {character.unallocated_stats}")
        print()
        print("Current Stats (after class modifiers):")
        
        for stat, value in character.stats.items():
            print(f"  {stat.title()}: {value}")
            
        print()
        print("Enter stat name to increase (str/dex/con/int/wis/cha)")
        print("or 'done' when finished:")
        
    def show_main_menu(self) -> None:
        """Show the main menu."""
        print("\n=== ROGUE CITY ===")
        print()
        print("A MajorMUD-style text RPG")
        print()
        print("Commands:")
        print("  new    - Create a new character")
        print("  load   - Load an existing character")
        print("  delete - Delete a saved character")
        print("  quit   - Exit the game")
        print()
        
    def show_character_selection(self, characters: list) -> None:
        """Show character selection menu."""
        if not characters:
            print("\n=== LOAD CHARACTER ===")
            print()
            print("No saved characters found.")
            print()
            print("Create a new character first.")
            return
            
        print("\n=== LOAD CHARACTER ===")
        print()
        print("Saved Characters:")
        print()
        
        for i, char_info in enumerate(characters, 1):
            name = char_info['name']
            char_class = char_info['class'].title()
            level = char_info['level']
            print(f"{i}. {name} the {char_class} (Level {level})")
            
        print()
        print("Enter the number of the character to load:")
        print("or 'back' to return to main menu.")
        
    def show_character_deletion(self, characters: list) -> None:
        """Show character deletion menu."""
        if not characters:
            print("\n=== DELETE CHARACTER ===")
            print()
            print("No saved characters found.")
            print()
            print("Nothing to delete.")
            return
            
        print("\n=== DELETE CHARACTER ===")
        print()
        print("WARNING: Character deletion is permanent!")
        print()
        print("Saved Characters:")
        print()
        
        for i, char_info in enumerate(characters, 1):
            name = char_info['name']
            char_class = char_info['class'].title()
            level = char_info['level']
            print(f"{i}. {name} the {char_class} (Level {level})")
            
        print()
        print("Enter the number of the character to DELETE:")
        print("or 'back' to return to main menu.")
        
    def show_deletion_confirmation(self, character_info: dict) -> None:
        """Show deletion confirmation dialog."""
        print("\n=== CONFIRM DELETION ===")
        print()
        print("You are about to PERMANENTLY DELETE:")
        print(f"  {character_info['name']} the {character_info['class'].title()} (Level {character_info['level']})")
        print()
        print("This action CANNOT be undone!")
        print()
        print("Type 'DELETE' (all caps) to confirm deletion:")
        print("or anything else to cancel.")
        
    def get_input(self) -> Optional[str]:
        """
        Get input from the user with command history support.
        
        Returns:
            Command string if input was received, None if interrupted
        """
        try:
            # Generate status line prompt (MajorMUD style)
            prompt = self._generate_prompt()
            command = input(prompt).strip()
            
            if command:
                # Add to history if it's a new command
                if not self.command_history or self.command_history[-1] != command:
                    self.command_history.append(command)
                    
            return command
            
        except KeyboardInterrupt:
            return "quit"
        except EOFError:
            return "quit"
            
    def display_message(self, message: str) -> None:
        """
        Display a message to the user.
        Compatibility method for existing code that expects this method.
        """
        self.output(message)
        
    def set_context(self, content: list) -> None:
        """
        Compatibility method for existing code.
        In simple UI, context is displayed immediately rather than stored.
        """
        # In simple UI mode, we don't maintain persistent context
        # This method exists for compatibility but does nothing
        pass
    
    def toggle_colors(self) -> bool:
        """
        Toggle color output on/off.
        
        Returns:
            True if colors are now enabled, False if disabled
        """
        if self.color_manager.is_enabled():
            self.color_manager.disable_colors()
            self.log_system("Colors disabled")
            return False
        else:
            self.color_manager.enable_colors()
            if self.color_manager.is_enabled():
                self.log_system("Colors enabled")
                return True
            else:
                self.log_error("Colorama not available - colors cannot be enabled")
                return False
    
    def set_current_character(self, character) -> None:
        """Set the current character for status line display."""
        self.current_character = character
        
    def toggle_status_line(self) -> bool:
        """Toggle status line display on/off."""
        self.show_status_line = not self.show_status_line
        if self.show_status_line:
            self.log_system("Status line enabled")
        else:
            self.log_system("Status line disabled")
        return self.show_status_line
        
    def _generate_prompt(self) -> str:
        """Generate prompt with optional status line (MajorMUD style)."""
        if not self.show_status_line or not self.current_character:
            return self.input_prompt
            
        # Format: [HP: current/max] >
        hp_text = f"HP: {self.current_character.current_hp}/{self.current_character.max_hp}"
        
        # Add mana for mage classes if they have it
        status_parts = [hp_text]
        if hasattr(self.current_character, 'current_mana') and hasattr(self.current_character, 'max_mana'):
            if self.current_character.max_mana > 0:
                mana_text = f"Mana: {self.current_character.current_mana}/{self.current_character.max_mana}"
                status_parts.append(mana_text)
                
        status_line = "[" + ", ".join(status_parts) + "] "
        return status_line + self.input_prompt
        
    def show_health_status(self, character) -> None:
        """Display detailed health status (MajorMUD HEALTH command style)."""
        print()
        print(f"=== HEALTH STATUS ===")
        
        # Current health with percentage and condition
        hp_percent = int((character.current_hp / character.max_hp) * 100)
        
        # MajorMUD-style health conditions
        if hp_percent >= 90:
            condition = "excellent"
            color = "success"
        elif hp_percent >= 75:
            condition = "good"
            color = "success"
        elif hp_percent >= 50:
            condition = "fair"
            color = "info"
        elif hp_percent >= 25:
            condition = "wounded"
            color = "warning"
        elif hp_percent >= 10:
            condition = "badly wounded"
            color = "error"
        else:
            condition = "near death"
            color = "error"
            
        health_msg = f"You are in {condition} condition."
        if color == "success":
            colored_msg = self.color_manager.format_success_message(health_msg)
        elif color == "info":
            colored_msg = self.color_manager.format_info_message(health_msg)
        elif color == "warning":
            colored_msg = self.color_manager.format_system_message(health_msg)
        else:
            colored_msg = self.color_manager.format_error_message(health_msg)
            
        print(colored_msg)
        print(f"Hit Points: {character.current_hp}/{character.max_hp} ({hp_percent}%)")
        
        # Show mana for applicable classes
        if hasattr(character, 'current_mana') and hasattr(character, 'max_mana'):
            if character.max_mana > 0:
                mana_percent = int((character.current_mana / character.max_mana) * 100)
                print(f"Mana Points: {character.current_mana}/{character.max_mana} ({mana_percent}%)")
                
        # Show healing rate
        if hp_percent < 100:
            print("\nYou will heal naturally over time.")
            print("Use the REST command to increase your healing rate.")
        print()


# Test function for the simple UI manager
def _test_simple_ui():
    """Test the simple UI manager."""
    ui = SimpleUIManager()
    
    try:
        ui.initialize()
        ui.show_main_menu()
        
        # Test room display
        ui.show_room(
            "Cave Entrance",
            "A dark cave mouth yawns before you, leading into the unknown depths of the earth. Sunlight filters in from behind you, casting long shadows on the rocky floor.",
            ["north", "south"],
            ["rusty sword"],
            ["goblin"]
        )
        
        ui.log_info("Type 'help' for available commands.")
        
        # Simple input loop
        while True:
            command = ui.get_input()
            if not command:
                continue
                
            if command.lower() in ['quit', 'exit', 'q']:
                break
            elif command.lower() == 'help':
                ui.log_info("Available commands: look, north, south, status, quit")
            elif command.lower() == 'look':
                ui.show_room(
                    "Cave Entrance", 
                    "The cave entrance is dimly lit by sunlight from outside.",
                    ["north", "south"]
                )
            elif command.lower() in ['north', 'n']:
                ui.log_success("You move north toward the light.")
            elif command.lower() in ['south', 's']:
                ui.log_message("You venture deeper into the darkness.")
            else:
                ui.log_error(f"Unknown command: {command}")
                
    except KeyboardInterrupt:
        pass
    finally:
        ui.cleanup()


if __name__ == "__main__":
    _test_simple_ui()