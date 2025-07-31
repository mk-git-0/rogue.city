"""
Game Engine for Rogue City
Central game state management and main game loop coordination.
"""

import time
import signal
import sys
from typing import Dict, Any, Optional, List
from enum import Enum

from .simple_ui_manager import SimpleUIManager
from .dice_system import DiceSystem
from .timer_system import TimerSystem
from .save_manager import SaveManager


class GameState(Enum):
    """Enumeration of possible game states."""
    MENU = "menu"
    CHARACTER_CREATION = "character_creation"
    CHARACTER_SELECTION = "character_selection"
    PLAYING = "playing"
    PAUSED = "paused"
    COMBAT = "combat"
    INVENTORY = "inventory"
    CHARACTER_SHEET = "character_sheet"
    QUIT = "quit"


class GameEngine:
    """
    Central game engine that manages all game systems and coordinates the main game loop.
    Runs at 60 FPS for smooth timer processing and UI updates.
    """
    
    def __init__(self):
        """Initialize the game engine and all subsystems."""
        self.running = False
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps
        
        # Game state
        self.current_state = GameState.MENU
        self.game_data: Dict[str, Any] = {}
        
        # Core systems
        self.ui_manager = SimpleUIManager()
        self.dice_system = DiceSystem(show_rolls=True)
        self.timer_system = TimerSystem()
        self.save_manager = SaveManager()
        
        # Character system
        self.current_character = None
        self.character_creation_state = None
        
        # Game loop timing
        self.last_frame_time = 0.0
        self.frame_count = 0
        self.fps_counter_time = 0.0
        self.actual_fps = 0.0
        
        # Signal handling for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle system signals for clean shutdown."""
        self.ui_manager.log_system("Received shutdown signal. Cleaning up...")
        self.shutdown()
        
    def initialize(self) -> bool:
        """
        Initialize all game systems.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize UI system
            self.ui_manager.initialize()
            self.ui_manager.log_system("Rogue City - Game Engine Starting...")
            self.ui_manager.log_info("Initializing systems...")
            
            # Initialize other systems
            self._initialize_game_data()
            
            # Show initial game state
            self._update_context_display()
            
            self.ui_manager.log_success("All systems initialized successfully!")
            self.ui_manager.log_info("Type 'help' for available commands.")
            
            return True
            
        except Exception as e:
            if hasattr(self.ui_manager, 'stdscr') and self.ui_manager.stdscr:
                self.ui_manager.log_error(f"Failed to initialize game: {e}")
                time.sleep(2)  # Give user time to see error
            else:
                print(f"Failed to initialize game: {e}")
            return False
            
    def _initialize_game_data(self) -> None:
        """Initialize default game data."""
        self.game_data = {
            'player': {
                'name': 'Hero',
                'level': 1,
                'health': 100,
                'max_health': 100,
                'mana': 50,
                'max_mana': 50,
                'location': 'cave_entrance'
            },
            'current_area': {
                'name': 'Cave Entrance',
                'description': 'A dark cave mouth yawns before you, leading into the unknown depths of the earth. Sunlight filters in from behind you, casting long shadows on the rocky floor.',
                'exits': ['north', 'south'],
                'items': [],
                'enemies': []
            },
            'game_stats': {
                'start_time': time.time(),
                'commands_entered': 0,
                'areas_visited': 1
            }
        }
        
    def _update_context_display(self) -> None:
        """Update the context display for current game state."""
        # In simplified UI, context is displayed on-demand rather than continuously
        # This method exists for compatibility but doesn't need to do anything
        pass
        
    def process_command(self, command: str) -> None:
        """
        Process a command entered by the player.
        
        Args:
            command: The command string to process
        """
        if not command.strip():
            return
            
        # Update game stats
        self.game_data['game_stats']['commands_entered'] += 1
        
        # Parse command
        parts = command.lower().strip().split()
        if not parts:
            return
            
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle commands based on current state
        if self.current_state == GameState.MENU:
            self._handle_menu_command(cmd, args)
        elif self.current_state == GameState.CHARACTER_CREATION:
            self._handle_character_creation_command(cmd, args)
        elif self.current_state == GameState.CHARACTER_SELECTION:
            self._handle_character_selection_command(cmd, args)
        elif self.current_state == GameState.PLAYING:
            self._handle_game_command(cmd, args)
        elif self.current_state == GameState.PAUSED:
            self._handle_pause_command(cmd, args)
        else:
            self.ui_manager.log_error(f"Unknown game state: {self.current_state}")
            
    def _handle_menu_command(self, cmd: str, args: List[str]) -> None:
        """Handle commands in menu state."""
        if cmd in ['new', 'create', 'n']:
            self.current_state = GameState.CHARACTER_CREATION
            self.character_creation_state = {'step': 'class_selection'}
            self._start_character_creation()
        elif cmd in ['load', 'l']:
            self.current_state = GameState.CHARACTER_SELECTION
            self._show_character_selection()
        elif cmd in ['quit', 'exit', 'q']:
            self.shutdown()
        else:
            self.ui_manager.log_info("Menu commands: new (create character), load (load character), quit")
            
    def _handle_game_command(self, cmd: str, args: List[str]) -> None:
        """Handle commands during gameplay."""
        if cmd in ['quit', 'exit', 'q']:
            self.shutdown()
        elif cmd == 'help':
            self._show_help()
        elif cmd in ['look', 'l']:
            self._look_command()
        elif cmd in ['north', 'n', 'south', 's', 'east', 'e', 'west', 'w']:
            self._move_command(cmd)
        elif cmd == 'status':
            self._status_command()
        elif cmd == 'pause':
            self.current_state = GameState.PAUSED
            self.timer_system.pause()
            self.ui_manager.log_system("Game paused. Type 'resume' to continue.")
            self._update_context_display()
        elif cmd == 'debug':
            self._toggle_debug()
        elif cmd == 'roll':
            self._roll_command(args)
        elif cmd == 'time':
            self._time_command()
        else:
            self.ui_manager.log_error(f"Unknown command: {cmd}. Type 'help' for available commands.")
            
    def _handle_pause_command(self, cmd: str, args: List[str]) -> None:
        """Handle commands while paused."""
        if cmd in ['resume', 'unpause', 'continue']:
            self.current_state = GameState.PLAYING
            self.timer_system.resume()
            self.ui_manager.log_system("Game resumed.")
            self._update_context_display()
        elif cmd in ['quit', 'exit', 'q']:
            self.shutdown()
        else:
            self.ui_manager.log_info("Paused. Commands: resume, quit")
            
    def _handle_character_creation_command(self, cmd: str, args: List[str]) -> None:
        """Handle commands during character creation."""
        if cmd in ['quit', 'exit', 'q']:
            self.current_state = GameState.MENU
            self.character_creation_state = None
            self.ui_manager.log_system("Character creation canceled.")
            self._show_main_menu()
            return
            
        step = self.character_creation_state.get('step')
        
        if step == 'class_selection':
            self._handle_class_selection(cmd, args)
        elif step == 'class_confirmation':
            self._handle_class_confirmation(cmd, args)
        elif step == 'name_entry':
            self._handle_name_entry(cmd, args)
        elif step == 'name_confirmation':
            self._handle_name_confirmation(cmd, args)
        elif step == 'stat_allocation':
            self._handle_stat_allocation(cmd, args)
        elif step == 'stat_confirmation':
            self._handle_stat_confirmation(cmd, args)
        else:
            self.ui_manager.log_error(f"Unknown character creation step: {step}")
            
    def _handle_character_selection_command(self, cmd: str, args: List[str]) -> None:
        """Handle commands during character selection."""
        if cmd in ['quit', 'exit', 'q', 'back']:
            self.current_state = GameState.MENU
            self._show_main_menu()
            return
            
        # Try to parse as character selection number
        try:
            choice = int(cmd)
            saved_characters = self.save_manager.list_saved_characters()
            
            if 1 <= choice <= len(saved_characters):
                character_info = saved_characters[choice - 1]
                character = self.save_manager.load_character(character_info['name'])
                
                if character:
                    self.current_character = character
                    self.current_state = GameState.PLAYING
                    self.ui_manager.log_success(f"Loaded {character.name} the {character.character_class.title()}!")
                    self._update_context_display()
                else:
                    self.ui_manager.log_error(f"Failed to load character: {character_info['name']}")
            else:
                self.ui_manager.log_error("Invalid selection. Enter a number from the list.")
                
        except ValueError:
            self.ui_manager.log_error("Enter a number to select a character, or 'back' to return to menu.")
            
    # Character Creation Implementation Methods
    
    def _show_main_menu(self) -> None:
        """Show the main menu."""
        self.ui_manager.show_main_menu()
        
    def _start_character_creation(self) -> None:
        """Start the character creation process."""
        self.ui_manager.log_system("Starting character creation...")
        self._show_class_selection()
        
    def _show_class_selection(self) -> None:
        """Show class selection interface."""
        class_data = self.save_manager.load_class_definitions()
        self.ui_manager.show_character_creation_class_selection(class_data)
        
        # Store class list for processing input
        class_list = list(class_data.keys())
        self.character_creation_state['class_list'] = class_list
        
    def _handle_class_selection(self, cmd: str, args: List[str]) -> None:
        """Handle class selection input."""
        try:
            choice = int(cmd)
            class_list = self.character_creation_state.get('class_list', [])
            
            if 1 <= choice <= len(class_list):
                selected_class = class_list[choice - 1]
                class_data = self.save_manager.load_class_definitions()
                selected_info = class_data[selected_class]
                
                # Show confirmation using simple UI
                self.ui_manager.show_character_creation_class_confirmation(selected_info)
                self.character_creation_state['selected_class'] = selected_class
                self.character_creation_state['step'] = 'class_confirmation'
                
            else:
                self.ui_manager.log_error("Invalid choice. Enter a number 1-4.")
                
        except ValueError:
            self.ui_manager.log_error("Enter a number 1-4 to select a class.")
                
    def _handle_class_confirmation(self, cmd: str, args: List[str]) -> None:
        """Handle class confirmation input."""
        if cmd.lower() in ['y', 'yes']:
            # Confirmed class selection
            self.character_creation_state['step'] = 'name_entry'
            self._show_name_entry()
        elif cmd.lower() in ['n', 'no']:
            # Go back to class selection
            self.character_creation_state['step'] = 'class_selection'
            self._show_class_selection()
        else:
            self.ui_manager.log_error("Enter 'y' for yes or 'n' for no.")
                
    def _show_name_entry(self) -> None:
        """Show name entry interface."""
        self.ui_manager.show_character_creation_name_entry()
        
    def _handle_name_entry(self, cmd: str, args: List[str]) -> None:
        """Handle name entry input."""
        name = cmd.strip()
        
        if not name:
            self.ui_manager.log_error("Name cannot be empty.")
            return
            
        if len(name) > 20:
            self.ui_manager.log_error("Name too long (max 20 characters).")
            return
            
        if self.save_manager.character_name_exists(name):
            self.ui_manager.log_error("That name is already taken. Choose another.")
            return
            
        # Name is valid, confirm it
        self.ui_manager.show_character_creation_name_confirmation(name)
        self.character_creation_state['character_name'] = name
        self.character_creation_state['step'] = 'name_confirmation'
        
    def _handle_name_confirmation(self, cmd: str, args: List[str]) -> None:
        """Handle name confirmation input."""
        if cmd.lower() in ['y', 'yes']:
            # Create character instance and apply class modifiers
            selected_class = self.character_creation_state['selected_class']
            character_name = self.character_creation_state['character_name']
            
            character = self._create_character_instance(character_name, selected_class)
            
            # Apply class modifiers
            class_data = self.save_manager.load_class_definitions()
            class_info = class_data[selected_class]
            character.apply_class_modifiers(class_info)
            character.calculate_derived_stats()
            
            self.character_creation_state['character'] = character
            self.character_creation_state['step'] = 'stat_allocation'
            self._show_stat_allocation()
            
        elif cmd.lower() in ['n', 'no']:
            # Go back to name entry
            self.character_creation_state['step'] = 'name_entry'
            self._show_name_entry()
        else:
            self.ui_manager.log_error("Enter 'y' for yes or 'n' for no.")
            
    def _handle_stat_confirmation(self, cmd: str, args: List[str]) -> None:
        """Handle stat allocation confirmation."""
        if cmd.lower() in ['y', 'yes']:
            self._finalize_character()
        elif cmd.lower() in ['n', 'no']:
            # Go back to stat allocation
            self.character_creation_state['step'] = 'stat_allocation'
            self._show_stat_allocation()
        else:
            self.ui_manager.log_error("Enter 'y' for yes or 'n' for no.")
        
    def _show_stat_allocation(self) -> None:
        """Show stat allocation interface."""
        character = self.character_creation_state['character']
        self.ui_manager.show_character_creation_stat_allocation(character)
        
    def _handle_stat_allocation(self, cmd: str, args: List[str]) -> None:
        """Handle stat allocation input."""
        character = self.character_creation_state['character']
        
        if cmd.lower() == 'done':
            if character.unallocated_stats > 0:
                self.ui_manager.log_info(f"You still have {character.unallocated_stats} points to allocate. Continue anyway? (y/n)")
                self.character_creation_state['step'] = 'stat_confirmation'
                return
            else:
                self._finalize_character()
                return
                
        # Handle stat abbreviations
        stat_mapping = {
            'str': 'strength',
            'dex': 'dexterity', 
            'con': 'constitution',
            'int': 'intelligence',
            'wis': 'wisdom',
            'cha': 'charisma'
        }
        
        full_stat = stat_mapping.get(cmd.lower(), cmd.lower())
        
        if character.allocate_stat_point(full_stat):
            self.ui_manager.log_success(f"Increased {full_stat.title()} to {character.stats[full_stat]}")
            self._show_stat_allocation()  # Refresh display
        else:
            if character.unallocated_stats <= 0:
                self.ui_manager.log_error("No stat points remaining. Type 'done' to finish.")
            else:
                self.ui_manager.log_error("Invalid stat name. Use: str, dex, con, int, wis, cha")
                
    def _create_character_instance(self, name: str, class_type: str):
        """Create appropriate character class instance."""
        if class_type == 'rogue':
            from characters.class_rogue import Rogue
            return Rogue(name)
        elif class_type == 'knight':
            from characters.class_knight import Knight
            return Knight(name)
        elif class_type == 'mage':
            from characters.class_mage import Mage
            return Mage(name)
        elif class_type == 'mystic':
            from characters.class_mystic import Mystic
            return Mystic(name)
        else:
            raise ValueError(f"Unknown class type: {class_type}")
            
    def _finalize_character(self) -> None:
        """Finalize character creation and save."""
        character = self.character_creation_state['character']
        
        # Mark character creation as complete
        character.creation_complete = True
        character.calculate_derived_stats()
        
        # Save character
        if self.save_manager.save_character(character):
            self.current_character = character
            self.current_state = GameState.PLAYING
            self.character_creation_state = None
            
            self.ui_manager.log_success(f"Character {character.name} created and saved!")
            self.ui_manager.log_success("Welcome to Rogue City! Your adventure begins...")
            self._update_context_display()
        else:
            self.ui_manager.log_error("Failed to save character. Please try again.")
            
    def _show_character_selection(self) -> None:
        """Show character selection interface."""
        saved_characters = self.save_manager.list_saved_characters()
        self.ui_manager.show_character_selection(saved_characters)
        
        if not saved_characters:
            self.ui_manager.log_info("No characters to load. Type 'back' to return to menu.")
            
    def _show_help(self) -> None:
        """Show available commands."""
        help_text = [
            "Movement: north (n), south (s), east (e), west (w)",
            "Actions: look (l), status",
            "Game: pause, help, quit",
            "Debug: debug, roll <dice>, time"
        ]
        for line in help_text:
            self.ui_manager.log_info(line)
            
    def _look_command(self) -> None:
        """Handle the look command."""
        area = self.game_data.get('current_area', {})
        
        # Show room information using the UI manager's room display method
        self.ui_manager.show_room(
            area.get('name', 'Unknown Location'),
            area.get('description', 'You see nothing special.'),
            area.get('exits', []),
            area.get('items', []),
            area.get('enemies', [])
        )
        
        # Show character status if we have a character
        if self.current_character:
            self.ui_manager.show_character_status(self.current_character)
            
    def _move_command(self, direction: str) -> None:
        """Handle movement commands."""
        # Normalize direction
        direction_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
        full_direction = direction_map.get(direction, direction)
        
        area = self.game_data.get('current_area', {})
        exits = area.get('exits', [])
        
        if full_direction in exits:
            self.ui_manager.log_success(f"You move {full_direction}.")
            # In a full implementation, this would change the current area
            # For now, just acknowledge the movement
        else:
            self.ui_manager.log_error(f"You cannot go {full_direction} from here.")
            
    def _status_command(self) -> None:
        """Show detailed player status."""
        player = self.game_data.get('player', {})
        stats = self.game_data.get('game_stats', {})
        
        status_lines = [
            f"Character: {player.get('name', 'Unknown')}",
            f"Level: {player.get('level', 1)}",
            f"Health: {player.get('health', 0)}/{player.get('max_health', 0)}",
            f"Mana: {player.get('mana', 0)}/{player.get('max_mana', 0)}",
            f"Location: {player.get('location', 'unknown')}",
            f"Commands entered: {stats.get('commands_entered', 0)}",
            f"Areas visited: {stats.get('areas_visited', 0)}"
        ]
        
        for line in status_lines:
            self.ui_manager.log_info(line)
            
    def _toggle_debug(self) -> None:
        """Toggle debug information display."""
        self._show_debug = getattr(self, '_show_debug', False)
        self._show_debug = not self._show_debug
        
        if self._show_debug:
            self.ui_manager.log_system("Debug mode enabled.")
        else:
            self.ui_manager.log_system("Debug mode disabled.")
            
        self._update_context_display()
        
    def _roll_command(self, args: List[str]) -> None:
        """Handle dice rolling command."""
        if not args:
            self.ui_manager.log_error("Usage: roll <dice notation> (e.g., roll 1d20+5)")
            return
            
        try:
            notation = args[0]
            result = self.dice_system.roll(notation)
            self.ui_manager.log_success(f"Rolled {notation}: {result}")
        except Exception as e:
            self.ui_manager.log_error(f"Invalid dice notation: {e}")
            
    def _time_command(self) -> None:
        """Show timing information."""
        current_time = self.timer_system.get_current_time()
        next_action = self.timer_system.get_time_until_next_action()
        
        self.ui_manager.log_info(f"Game time: {current_time:.2f}s")
        if next_action is not None:
            self.ui_manager.log_info(f"Next action in: {next_action:.2f}s")
        else:
            self.ui_manager.log_info("No pending actions.")
            
    def update(self, delta_time: float) -> None:
        """
        Update game systems.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Process timer system
        if not self.timer_system.is_paused():
            ready_actions = self.timer_system.process_ready_actions()
            for action in ready_actions:
                self._handle_timed_action(action)
                
        # Update context display periodically
        if self.frame_count % 60 == 0:  # Update once per second at 60 FPS
            self._update_context_display()
            
    def _handle_timed_action(self, action) -> None:
        """Handle a timed action that's ready to execute."""
        self.ui_manager.log_system(f"Timed action: {action.actor_id} performs {action.action_type}")
        
    def run(self) -> None:
        """
        Run the main game loop at 60 FPS.
        """
        if not self.initialize():
            return
            
        self.running = True
        self.current_state = GameState.MENU
        self.last_frame_time = time.time()
        
        # Show initial menu
        self._show_main_menu()
        
        try:
            while self.running:
                frame_start = time.time()
                
                # Calculate delta time
                delta_time = frame_start - self.last_frame_time
                self.last_frame_time = frame_start
                
                # Handle input
                command = self.ui_manager.get_input()
                if command:
                    self.process_command(command)
                    
                # Update game systems
                self.update(delta_time)
                
                # FPS counting
                self.frame_count += 1
                if frame_start - self.fps_counter_time >= 1.0:
                    self.actual_fps = self.frame_count / (frame_start - self.fps_counter_time)
                    self.frame_count = 0
                    self.fps_counter_time = frame_start
                    
                # Frame rate limiting
                frame_end = time.time()
                frame_duration = frame_end - frame_start
                sleep_time = self.frame_time - frame_duration
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()
            
    def shutdown(self) -> None:
        """Shutdown the game engine and clean up resources."""
        self.running = False
        
        if hasattr(self.ui_manager, 'stdscr') and self.ui_manager.stdscr:
            self.ui_manager.log_system("Shutting down game engine...")
            time.sleep(0.5)  # Brief pause to show message
            
        self.ui_manager.cleanup()
        sys.exit(0)


# Test function for the game engine
def _test_game_engine():
    """Test the game engine functionality."""
    engine = GameEngine()
    
    # Test initialization
    assert engine.current_state == GameState.MENU
    assert engine.target_fps == 60
    assert isinstance(engine.ui_manager, SimpleUIManager)
    assert isinstance(engine.dice_system, DiceSystem)
    assert isinstance(engine.timer_system, TimerSystem)
    
    print("Game engine tests passed!")


if __name__ == "__main__":
    # Run tests if called directly
    _test_game_engine()