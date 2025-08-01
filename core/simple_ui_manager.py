"""
Simple UI Manager for Rogue City
Traditional MajorMUD-style single-scrolling terminal interface.
"""

import sys
import threading
import time
from typing import Optional
from collections import deque


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
        self.output(message, "ERROR:")
        
    def log_success(self, message: str) -> None:
        """Log a success message."""
        self.output(message)
        
    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.output(message)
        
    def log_system(self, message: str) -> None:
        """Log a system message."""
        self.output(message, "[SYSTEM]")
        
    def log_command(self, command: str) -> None:
        """Log a command that was entered."""
        # Commands are echoed as part of input, no need to log separately
        pass
        
    def log_combat(self, message: str) -> None:
        """Log a combat message with distinctive formatting."""
        self.output(message)
        
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
            print(f"Exits: {', '.join(exits)}")
        else:
            print("No obvious exits.")
            
        if items:
            print(f"Items: {', '.join(items)}")
            
        if enemies:
            print(f"Enemies: {', '.join(enemies)}")
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
        print()
        
        for i, (class_id, class_info) in enumerate(classes.items(), 1):
            name = class_info['name']
            difficulty = class_info['difficulty']
            description = class_info['description']
            
            print(f"{i}. {name} (Difficulty: {difficulty})")
            print(f"   {description}")
            print()
            
        print("Enter the number of your choice (1-4):")
        
    def show_character_creation_class_confirmation(self, class_info: dict) -> None:
        """Show class confirmation details."""
        print("\n=== CHARACTER CREATION ===")
        print()
        print(f"Selected Class: {class_info['name']}")
        print(f"Difficulty: {class_info['difficulty']}")
        print()
        print(f"Description: {class_info['description']}")
        print()
        print("Stat Modifiers:")
        
        for stat, modifier in class_info['stat_modifiers'].items():
            sign = "+" if modifier >= 0 else ""
            print(f"  {stat.title()}: {sign}{modifier}")
            
        print()
        print(f"Hit Die: {class_info['hit_die']}")
        print(f"Attack Speed: {class_info['base_attack_speed']} seconds")
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
        print("  new  - Create a new character")
        print("  load - Load an existing character")
        print("  quit - Exit the game")
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
        
    def get_input(self) -> Optional[str]:
        """
        Get input from the user with command history support.
        
        Returns:
            Command string if input was received, None if interrupted
        """
        try:
            # Simple input with prompt
            command = input(self.input_prompt).strip()
            
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