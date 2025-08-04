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
from .combat_system import CombatSystem
from .tutorial_system import TutorialSystem
from .command_parser import CommandParser
from .help_system import HelpSystem
from .game_completion import GameCompletion
from .alignment_system import Alignment, AlignmentSystem


class GameState(Enum):
    """Enumeration of possible game states."""
    MENU = "menu"
    CHARACTER_CREATION = "character_creation"
    CHARACTER_SELECTION = "character_selection"
    CHARACTER_DELETION = "character_deletion"
    CHARACTER_DELETION_CONFIRMATION = "character_deletion_confirmation"
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
        self.combat_system = CombatSystem(self.timer_system, self.dice_system, self.ui_manager, self)
        
        # Enhanced systems
        self.command_parser = CommandParser(self)
        self.help_system = HelpSystem(self.ui_manager)
        self.game_completion = GameCompletion(self)
        self.alignment_system = AlignmentSystem()
        
        # Reference for systems
        self.ui = self.ui_manager  # Convenience reference
        
        # Enemy system
        from enemies.enemy_factory import EnemyFactory
        self.enemy_factory = EnemyFactory()
        
        # World system
        self.tutorial_system = TutorialSystem(self.ui_manager)
        self.current_area = None
        self.current_room = None
        self.world_areas = {}
        
        # Character system
        self.current_character = None
        self.current_player = None  # Alias for current_character
        self.character_creation_state = None
        self.character_deletion_state = None
        
        # Game loop timing
        self.last_frame_time = 0.0
        self.frame_count = 0
        self.fps_counter_time = 0.0
        self.actual_fps = 0.0
        self.start_time = time.time()
        
        # Game settings
        self.game_settings = self._load_game_settings()
        
        # State tracking
        self.GameState = GameState  # Make available to command parser
        self.state = self.current_state  # Alias for compatibility
        
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
            self._initialize_world_areas()
            
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
    
    def _load_game_settings(self) -> Dict[str, Any]:
        """Load game settings from configuration file."""
        try:
            import json
            with open('data/config/game_settings.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load game settings: {e}")
            return {"game": {"frame_rate": 60}, "combat": {"timer_based": True}}
            
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
            
        # Track command for statistics
        self.game_completion.track_command_entered()
        
        # Update legacy game stats
        if 'game_stats' in self.game_data:
            self.game_data['game_stats']['commands_entered'] += 1
        
        # Handle commands based on current state
        if self.current_state == GameState.MENU:
            self._handle_menu_command_legacy(command)
        elif self.current_state == GameState.CHARACTER_CREATION:
            self._handle_character_creation_command_legacy(command)
        elif self.current_state == GameState.CHARACTER_SELECTION:
            self._handle_character_selection_command_legacy(command)
        elif self.current_state == GameState.CHARACTER_DELETION:
            self._handle_character_deletion_command_legacy(command)
        elif self.current_state == GameState.CHARACTER_DELETION_CONFIRMATION:
            self._handle_character_deletion_confirmation_command_legacy(command)
        elif self.current_state == GameState.PLAYING:
            # Use new command parser for gameplay
            continue_game = self.command_parser.parse_command(command)
            if not continue_game:
                self.shutdown()
        elif self.current_state == GameState.COMBAT:
            # Use command parser for combat commands too
            continue_game = self.command_parser.parse_command(command)
            if not continue_game:
                self.shutdown()
        elif self.current_state == GameState.PAUSED:
            self._handle_pause_command_legacy(command)
        else:
            self.ui_manager.log_error(f"Unknown game state: {self.current_state}")
            
    def _handle_menu_command_legacy(self, command: str) -> None:
        """Handle commands in menu state (legacy method)."""
        parts = command.lower().strip().split()
        if not parts:
            return
        cmd = parts[0]
        
        if cmd in ['new', 'create', 'n']:
            self.current_state = GameState.CHARACTER_CREATION
            self.character_creation_state = {'step': 'race_selection'}
            self._start_character_creation()
        elif cmd in ['load', 'l']:
            self.current_state = GameState.CHARACTER_SELECTION
            self._show_character_selection()
        elif cmd in ['delete', 'del', 'd']:
            self.current_state = GameState.CHARACTER_DELETION
            self._show_character_deletion()
        elif cmd in ['quit', 'exit', 'q']:
            self.shutdown()
        else:
            self.ui_manager.log_info("Menu commands: new (create character), load (load character), delete (delete character), quit")
    
    def _handle_menu_command(self, cmd: str, args: List[str]) -> None:
        """Handle commands in menu state."""
        if cmd in ['new', 'create', 'n']:
            self.current_state = GameState.CHARACTER_CREATION
            self.character_creation_state = {'step': 'race_selection'}
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
        elif cmd in ['attack', 'a']:
            self._attack_command(args)
        elif cmd == 'auto':
            self._auto_combat_command()
        elif cmd == 'flee':
            self._flee_command()
        elif cmd in ['spawn', 'summon']:  # Debug command for testing
            self._spawn_enemy_command(args)
        elif cmd == 'map':
            self._map_command()
        elif cmd == 'exits':
            self._exits_command()
        elif cmd in ['get', 'take']:
            self._get_command(args)
        elif cmd in ['inventory', 'i']:
            self._inventory_command()
        elif cmd in ['equip', 'wear', 'wield']:
            self._equip_command(args)
        elif cmd in ['unequip', 'remove']:
            self._unequip_command(args)
        elif cmd in ['use', 'drink']:
            self._use_command(args)
        elif cmd in ['drop']:
            self._drop_command(args)
        elif cmd in ['equipment', 'eq']:
            self._equipment_command()
        elif cmd in ['tutorial']:
            self._tutorial_command(args)
        else:
            self.ui_manager.log_error(f"Unknown command: {cmd}. Type 'help' for available commands.")
            
    def _handle_pause_command_legacy(self, command: str) -> None:
        """Handle commands while paused (legacy method)."""
        parts = command.lower().strip().split()
        if not parts:
            return
        cmd = parts[0]
        
        if cmd in ['resume', 'unpause', 'continue']:
            self.current_state = GameState.PLAYING
            self.timer_system.resume()
            self.ui_manager.log_system("Game resumed.")
            self._update_context_display()
        elif cmd in ['quit', 'exit', 'q']:
            self.shutdown()
        else:
            self.ui_manager.log_info("Paused. Commands: resume, quit")
    
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
            
    def _handle_character_creation_command_legacy(self, command: str) -> None:
        """Handle commands during character creation (legacy method)."""
        parts = command.lower().strip().split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in ['quit', 'exit', 'q']:
            self.current_state = GameState.MENU
            self.character_creation_state = None
            self.ui_manager.log_system("Character creation canceled.")
            self._show_main_menu()
            return
            
        step = self.character_creation_state.get('step')
        
        if step == 'race_selection':
            self._handle_race_selection(cmd, args)
        elif step == 'race_confirmation':
            self._handle_race_confirmation(cmd, args)
        elif step == 'alignment_selection':
            self._handle_alignment_selection(cmd, args)
        elif step == 'alignment_confirmation':
            self._handle_alignment_confirmation(cmd, args)
        elif step == 'class_selection':
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
    
    def _handle_character_creation_command(self, cmd: str, args: List[str]) -> None:
        """Handle commands during character creation."""
        if cmd in ['quit', 'exit', 'q']:
            self.current_state = GameState.MENU
            self.character_creation_state = None
            self.ui_manager.log_system("Character creation canceled.")
            self._show_main_menu()
            return
            
        step = self.character_creation_state.get('step')
        
        if step == 'race_selection':
            self._handle_race_selection(cmd, args)
        elif step == 'race_confirmation':
            self._handle_race_confirmation(cmd, args)
        elif step == 'alignment_selection':
            self._handle_alignment_selection(cmd, args)
        elif step == 'alignment_confirmation':
            self._handle_alignment_confirmation(cmd, args)
        elif step == 'class_selection':
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
            
    def _handle_character_selection_command_legacy(self, command: str) -> None:
        """Handle commands during character selection (legacy method)."""
        parts = command.lower().strip().split()
        if not parts:
            return
        cmd = parts[0]
        
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
                    self.current_player = character  # Set alias
                    
                    # Set character for status line display
                    self.ui_manager.set_current_character(character)
                    
                    self.current_state = GameState.PLAYING
                    self.ui_manager.log_success(f"Loaded {character.name} the {character.character_class.title()}!")
                    
                    # Load game statistics
                    character_data = self.save_manager._load_character_data(character.name)
                    if character_data:
                        self.game_completion.load_statistics(character_data)
                    
                    # Start world exploration
                    self.start_world_exploration(character)
                    
                    self._update_context_display()
                else:
                    self.ui_manager.log_error(f"Failed to load character: {character_info['name']}")
            else:
                self.ui_manager.log_error("Invalid selection. Enter a number from the list.")
                
        except ValueError:
            self.ui_manager.log_error("Enter a number to select a character, or 'back' to return to menu.")
    
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
                    self.current_player = character  # Set alias
                    
                    # Set character for status line display
                    self.ui_manager.set_current_character(character)
                    
                    self.current_state = GameState.PLAYING
                    self.ui_manager.log_success(f"Loaded {character.name} the {character.character_class.title()}!")
                    
                    # Load game statistics
                    character_data = self.save_manager._load_character_data(character.name)
                    if character_data:
                        self.game_completion.load_statistics(character_data)
                    
                    # Start world exploration
                    self.start_world_exploration(character)
                    
                    self._update_context_display()
                else:
                    self.ui_manager.log_error(f"Failed to load character: {character_info['name']}")
            else:
                self.ui_manager.log_error("Invalid selection. Enter a number from the list.")
                
        except ValueError:
            self.ui_manager.log_error("Enter a number to select a character, or 'back' to return to menu.")
    
    def _handle_character_deletion_command_legacy(self, command: str) -> None:
        """Handle commands during character deletion (legacy method)."""
        parts = command.lower().strip().split()
        if not parts:
            return
        cmd = parts[0]
        
        if cmd in ['quit', 'exit', 'q', 'back']:
            self.current_state = GameState.MENU
            self._show_main_menu()
            return
            
        # Try to parse as character deletion number
        try:
            choice = int(cmd)
            saved_characters = self.save_manager.list_saved_characters()
            
            if 1 <= choice <= len(saved_characters):
                character_info = saved_characters[choice - 1]
                
                # Store character info for confirmation
                self.character_deletion_state = character_info
                self.current_state = GameState.CHARACTER_DELETION_CONFIRMATION
                self.ui_manager.show_deletion_confirmation(character_info)
            else:
                self.ui_manager.log_error("Invalid selection. Enter a number from the list.")
                
        except ValueError:
            self.ui_manager.log_error("Enter a number to select a character to delete, or 'back' to return to menu.")
    
    def _handle_character_deletion_confirmation_command_legacy(self, command: str) -> None:
        """Handle commands during deletion confirmation (legacy method)."""
        command = command.strip()
        
        if command == "DELETE":
            # Perform the deletion
            character_info = self.character_deletion_state
            character_name = character_info['name']
            
            if self.save_manager.delete_character(character_name):
                self.ui_manager.log_success(f"Character '{character_name}' has been permanently deleted.")
            else:
                self.ui_manager.log_error(f"Failed to delete character '{character_name}'.")
                
            # Reset state and return to menu
            self.character_deletion_state = None
            self.current_state = GameState.MENU
            self._show_main_menu()
        else:
            # Any other input cancels the deletion
            self.ui_manager.log_info("Character deletion cancelled.")
            self.character_deletion_state = None
            self.current_state = GameState.MENU
            self._show_main_menu()
            
    # Character Creation Implementation Methods
    
    def _show_main_menu(self) -> None:
        """Show the main menu."""
        self.ui_manager.show_main_menu()
        
    def _start_character_creation(self) -> None:
        """Start the character creation process."""
        self.ui_manager.log_system("Starting character creation...")
        self._show_race_selection()
    
    def _show_race_selection(self) -> None:
        """Show race selection interface."""
        try:
            import json
            with open('/Users/knight/workspace/github.com/mk-git-0/rogue.city/data/races/race_definitions.json', 'r') as f:
                race_data = json.load(f)
        except Exception as e:
            self.ui_manager.log_error(f"Error loading race data: {e}")
            return
        
        self.ui_manager.log_system("\n=== CHARACTER RACE SELECTION ===\n")
        self.ui_manager.log_system("Choose your character's race:\n")
        
        race_list = []
        for i, (race_id, race_info) in enumerate(race_data.items(), 1):
            race_name = race_info['name']
            exp_mod = race_info['experience_modifier']
            exp_text = f"+{exp_mod}%" if exp_mod >= 0 else f"{exp_mod}%"
            description = race_info['description']
            
            self.ui_manager.log_system(f"{i:2d}. {race_name:<12} - {description} ({exp_text} experience)")
            race_list.append(race_id)
        
        self.ui_manager.log_system(f"\nEnter choice (1-{len(race_list)}): ")
        
        # Store race list for processing input
        self.character_creation_state['race_list'] = race_list
        
    def _handle_race_selection(self, cmd: str, args: List[str]) -> None:
        """Handle race selection input."""
        try:
            choice = int(cmd)
            race_list = self.character_creation_state.get('race_list', [])
            
            if 1 <= choice <= len(race_list):
                selected_race = race_list[choice - 1]
                
                # Load race data for confirmation display
                try:
                    import json
                    with open('/Users/knight/workspace/github.com/mk-git-0/rogue.city/data/races/race_definitions.json', 'r') as f:
                        race_data = json.load(f)
                    
                    selected_info = race_data[selected_race]
                    
                    # Show race confirmation
                    self._show_race_confirmation(selected_info)
                    self.character_creation_state['selected_race'] = selected_race
                    self.character_creation_state['step'] = 'race_confirmation'
                    
                except Exception as e:
                    self.ui_manager.log_error(f"Error loading race details: {e}")
                    
            else:
                self.ui_manager.log_error(f"Invalid choice. Enter a number 1-{len(race_list)}.")
                
        except ValueError:
            race_list = self.character_creation_state.get('race_list', [])
            self.ui_manager.log_error(f"Enter a number 1-{len(race_list)} to select a race.")
    
    def _show_race_confirmation(self, race_info: Dict[str, Any]) -> None:
        """Show race confirmation with detailed stats."""
        name = race_info['name']
        description = race_info['description']
        stat_mods = race_info['stat_modifiers']
        abilities = race_info['special_abilities']
        exp_mod = race_info['experience_modifier']
        
        self.ui_manager.log_system(f"\nSelected: {name}")
        self.ui_manager.log_system(f"{description}")
        
        # Show stat modifiers
        mod_text = []
        for stat, mod in stat_mods.items():
            if mod != 0:
                stat_abbrev = stat[:3].upper()
                sign = "+" if mod > 0 else ""
                mod_text.append(f"{sign}{mod} {stat_abbrev}")
        
        if mod_text:
            self.ui_manager.log_system(f"Stat Modifiers: {', '.join(mod_text)}")
        else:
            self.ui_manager.log_system("Stat Modifiers: None")
        
        # Show special abilities
        if abilities:
            ability_names = list(abilities.keys())
            self.ui_manager.log_system(f"Special Abilities: {', '.join(ability_names)}")
        else:
            self.ui_manager.log_system("Special Abilities: None")
        
        exp_text = f"+{exp_mod}%" if exp_mod >= 0 else f"{exp_mod}%"
        self.ui_manager.log_system(f"Experience Cost: {exp_text}")
        
        self.ui_manager.log_system("\nConfirm this race? (y/n): ")
    
    def _handle_race_confirmation(self, cmd: str, args: List[str]) -> None:
        """Handle race confirmation input."""
        if cmd.lower() in ['y', 'yes']:
            # Confirmed race selection, move to alignment selection
            self.character_creation_state['step'] = 'alignment_selection'
            self._show_alignment_selection()
        elif cmd.lower() in ['n', 'no']:
            # Go back to race selection
            self.character_creation_state['step'] = 'race_selection'
            self._show_race_selection()
        else:
            self.ui_manager.log_error("Enter 'y' for yes or 'n' for no.")
        
    def _show_alignment_selection(self) -> None:
        """Show alignment selection interface."""
        selected_race = self.character_creation_state.get('selected_race')
        
        self.ui_manager.log_system("\n" + "="*50)
        self.ui_manager.log_system("=== CHARACTER ALIGNMENT SELECTION ===")
        self.ui_manager.log_system("="*50)
        self.ui_manager.log_system("")
        self.ui_manager.log_system("Your character's moral outlook shapes their entire adventure.")
        self.ui_manager.log_system("Choose your alignment carefully - it affects abilities, equipment, and NPC reactions.")
        self.ui_manager.log_system("")
        
        # Load alignment data
        alignment_data = self.alignment_system.alignment_data
        
        # Display alignment options
        alignments = ['good', 'neutral', 'evil']
        alignment_displays = {
            'good': 'GOOD - "Protector of the Innocent"',
            'neutral': 'NEUTRAL - "Seeker of Balance"',
            'evil': 'EVIL - "Pursuer of Power"'
        }
        
        for i, alignment_key in enumerate(alignments, 1):
            data = alignment_data.get(alignment_key, {})
            philosophy = data.get('philosophy', 'Unknown philosophy')
            benefits = data.get('benefits', [])
            restrictions = data.get('restrictions', [])
            
            self.ui_manager.log_system(f"{i}. {alignment_displays[alignment_key]}")
            self.ui_manager.log_system(f"   Philosophy: {philosophy}")
            self.ui_manager.log_system(f"   Benefits: {', '.join([b.get('name', b) if isinstance(b, dict) else str(b) for b in benefits[:3]])}")
            self.ui_manager.log_system(f"   Restrictions: {', '.join([r.get('name', r) if isinstance(r, dict) else str(r) for r in restrictions[:2]])}")
            self.ui_manager.log_system("")
        
        # Show race compatibility note
        if selected_race:
            race_suggestions = {
                'dark_elf': 'Recommended: Neutral or Evil (Dark-Elves rarely choose Good)',
                'elf': 'Recommended: Good or Neutral (Elves tend toward good)',
                'half_ogre': 'Recommended: Neutral or Evil (Half-Ogres value strength)',
                'goblin': 'Recommended: Neutral or Evil (Goblins are naturally cunning)',
                'gaunt_one': 'Recommended: Any alignment (Gaunt Ones are mysterious)',
                'human': 'Recommended: Any alignment (Humans are versatile)'
            }
            suggestion = race_suggestions.get(selected_race, 'Any alignment is suitable')
            race_name = selected_race.replace('_', '-').title()
            self.ui_manager.log_system(f"Current Character: {race_name}")
            self.ui_manager.log_system(f"{suggestion}")
            self.ui_manager.log_system("")
        
        self.ui_manager.log_system("Enter choice (1-3): ")
        
        # Store alignment list for processing input
        self.character_creation_state['alignment_list'] = alignments
        
    def _handle_alignment_selection(self, cmd: str, args: List[str]) -> None:
        """Handle alignment selection input."""
        try:
            choice = int(cmd)
            alignment_list = self.character_creation_state.get('alignment_list', [])
            
            if 1 <= choice <= len(alignment_list):
                selected_alignment_key = alignment_list[choice - 1]
                alignment_enum = {
                    'good': Alignment.GOOD,
                    'neutral': Alignment.NEUTRAL,
                    'evil': Alignment.EVIL
                }.get(selected_alignment_key, Alignment.NEUTRAL)
                
                # Show alignment confirmation
                self._show_alignment_confirmation(selected_alignment_key, alignment_enum)
                self.character_creation_state['selected_alignment'] = alignment_enum
                self.character_creation_state['step'] = 'alignment_confirmation'
                
            else:
                self.ui_manager.log_error(f"Invalid choice. Enter a number 1-{len(alignment_list)}.")
                
        except ValueError:
            alignment_list = self.character_creation_state.get('alignment_list', [])
            self.ui_manager.log_error(f"Enter a number 1-{len(alignment_list)} to select an alignment.")
    
    def _show_alignment_confirmation(self, alignment_key: str, alignment_enum: Alignment) -> None:
        """Show alignment confirmation with detailed information."""
        alignment_data = self.alignment_system.alignment_data.get(alignment_key, {})
        
        name = alignment_data.get('name', alignment_key.title())
        display_name = alignment_data.get('display_name', name)
        philosophy = alignment_data.get('philosophy', 'Unknown philosophy')
        benefits = alignment_data.get('benefits', [])
        restrictions = alignment_data.get('restrictions', [])
        
        self.ui_manager.log_system(f"\nSelected: {name} Alignment")
        self.ui_manager.log_system(f'"{philosophy}"')
        self.ui_manager.log_system("")
        self.ui_manager.log_system("This alignment will:")
        
        # Show benefits
        for benefit in benefits[:4]:  # Show first 4 benefits
            if isinstance(benefit, dict):
                name_text = benefit.get('name', 'Unknown')
                desc_text = benefit.get('description', '')
                self.ui_manager.log_system(f"+ {name_text}: {desc_text}")
            else:
                self.ui_manager.log_system(f"+ {benefit}")
        
        # Show restrictions
        for restriction in restrictions[:3]:  # Show first 3 restrictions
            if isinstance(restriction, dict):
                name_text = restriction.get('name', 'Unknown')
                desc_text = restriction.get('description', '')
                self.ui_manager.log_system(f"- {name_text}: {desc_text}")
            else:
                self.ui_manager.log_system(f"- {restriction}")
        
        self.ui_manager.log_system("")
        self.ui_manager.log_system(f"Confirm {name} alignment? (y/n): ")
    
    def _handle_alignment_confirmation(self, cmd: str, args: List[str]) -> None:
        """Handle alignment confirmation input."""
        if cmd.lower() in ['y', 'yes']:
            # Confirmed alignment selection, move to class selection
            self.character_creation_state['step'] = 'class_selection'
            self._show_class_selection()
        elif cmd.lower() in ['n', 'no']:
            # Go back to alignment selection
            self.character_creation_state['step'] = 'alignment_selection'
            self._show_alignment_selection()
        else:
            self.ui_manager.log_error("Enter 'y' for yes or 'n' for no.")
        
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
                self.ui_manager.log_error(f"Invalid choice. Enter a number 1-{len(class_list)}.")
                
        except ValueError:
            class_list = self.character_creation_state.get('class_list', [])
            self.ui_manager.log_error(f"Enter a number 1-{len(class_list)} to select a class.")
                
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
            selected_race = self.character_creation_state['selected_race']
            selected_alignment = self.character_creation_state['selected_alignment']
            character_name = self.character_creation_state['character_name']
            
            character = self._create_character_instance(character_name, selected_class, selected_race, selected_alignment)
            
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
                
    def _create_character_instance(self, name: str, class_type: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Create appropriate character class instance."""
        if class_type == 'rogue':
            from characters.class_rogue import Rogue
            return Rogue(name, race_id, alignment)
        elif class_type == 'knight':
            from characters.class_knight import Knight
            return Knight(name, race_id, alignment)
        elif class_type == 'mage':
            from characters.class_mage import Mage
            return Mage(name, race_id, alignment)
        elif class_type == 'mystic':
            from characters.class_mystic import Mystic
            return Mystic(name, race_id, alignment)
        else:
            raise ValueError(f"Unknown class type: {class_type}")
            
    def _finalize_character(self) -> None:
        """Finalize character creation and save."""
        character = self.character_creation_state['character']
        
        # Mark character creation as complete
        character.creation_complete = True
        character.calculate_derived_stats()
        
        # Initialize game completion tracking
        self.game_completion.track_game_start()
        
        # Save character
        if self.save_manager.save_character(character):
            self.current_character = character
            self.current_player = character  # Set alias
            
            # Set character for status line display
            self.ui_manager.set_current_character(character)
            
            self.current_state = GameState.PLAYING
            self.character_creation_state = None
            
            self.ui_manager.log_success(f"Character {character.name} created and saved!")
            self.ui_manager.log_success("Welcome to Rogue City! Your adventure begins...")
            
            # Start world exploration
            self.start_world_exploration(character)
            
            self._update_context_display()
        else:
            self.ui_manager.log_error("Failed to save character. Please try again.")
            
    def _show_character_selection(self) -> None:
        """Show character selection interface."""
        saved_characters = self.save_manager.list_saved_characters()
        self.ui_manager.show_character_selection(saved_characters)
        
        if not saved_characters:
            self.ui_manager.log_info("No characters to load. Type 'back' to return to menu.")
    
    def _show_character_deletion(self) -> None:
        """Show character deletion interface."""
        saved_characters = self.save_manager.list_saved_characters()
        self.ui_manager.show_character_deletion(saved_characters)
        
        if not saved_characters:
            self.ui_manager.log_info("No characters to delete. Type 'back' to return to menu.")
            
    def _show_help(self) -> None:
        """Show available commands using help system."""
        self.help_system.show_general_help()
            
    def _look_command(self) -> None:
        """Handle the look command."""
        if not self.current_area or not self.current_room:
            # Fallback to old system if world not loaded
            area = self.game_data.get('current_area', {})
            self.ui_manager.show_room(
                area.get('name', 'Unknown Location'),
                area.get('description', 'You see nothing special.'),
                area.get('exits', []),
                area.get('items', []),
                area.get('enemies', [])
            )
            return
            
        room = self.current_area.get_room(self.current_room)
        if not room:
            self.ui_manager.log_error("Current room not found.")
            return
            
        # Show full room description
        description = room.get_full_description()
        self.ui_manager.log_info(description)
        
        # Trigger tutorial
        self.tutorial_system.on_player_action('look', 
            items_in_room=len(room.get_visible_items()),
            enemies_in_room=len(room.get_active_enemies())
        )
        
        # Update tutorial system
        self.tutorial_system.update()
            
    def _move_command(self, direction: str) -> None:
        """Handle movement commands."""
        if not self.current_area or not self.current_room:
            self.ui_manager.log_error("No current location.")
            return
            
        # Parse direction
        from areas.base_area import parse_direction
        direction_enum = parse_direction(direction)
        if not direction_enum:
            self.ui_manager.log_error(f"Invalid direction: {direction}")
            return
            
        room = self.current_area.get_room(self.current_room)
        if not room:
            self.ui_manager.log_error("Current room not found.")
            return
            
        # Check if exit exists
        exit_obj = room.get_exit(direction_enum)
        if not exit_obj:
            self.ui_manager.log_error(f"You cannot go {direction} from here.")
            return
            
        if exit_obj.is_locked:
            self.ui_manager.log_error(exit_obj.lock_message)
            return
            
        # Handle inter-area movement
        if exit_obj.destination_area:
            target_area = self.world_areas.get(exit_obj.destination_area)
            if not target_area:
                self.ui_manager.log_error(f"Cannot access area: {exit_obj.destination_area}")
                return
                
            # Change area
            self.current_area = target_area
            self.current_area_id = exit_obj.destination_area
            self.current_room = exit_obj.destination_room
            
            # Update character location
            if self.current_character:
                self.current_character.current_area = self.current_area_id
                self.current_character.current_room = self.current_room
                
        else:
            # Same area movement
            self.current_room = exit_obj.destination_room
            
            # Update character location
            if self.current_character:
                self.current_character.current_room = self.current_room
                
        # Handle room entry events
        new_room = self.current_area.get_room(self.current_room)
        if new_room:
            # Mark as visited
            self.current_area.visit_room(self.current_room)
            
            # Trigger area events
            if hasattr(self.current_area, 'on_room_enter'):
                messages = self.current_area.on_room_enter(self.current_room, self.current_character)
                for message in messages:
                    self.ui_manager.log_info(message)
                    
            # Show new room
            self._look_command()
            
            # Trigger tutorial
            self.tutorial_system.on_player_action('move')
            self.tutorial_system.on_player_action('enter_room', 
                room_name=new_room.name,
                items_in_room=len(new_room.get_visible_items()),
                enemies_in_room=len(new_room.get_active_enemies())
            )
            
            # Check for combat encounters
            active_enemies = new_room.get_active_enemies()
            if active_enemies and not new_room.is_safe:
                # Create enemies for combat
                combat_enemies = []
                for room_enemy in active_enemies:
                    for _ in range(room_enemy.quantity):
                        enemy = self.enemy_factory.create_enemy(room_enemy.enemy_type)
                        if enemy:
                            combat_enemies.append(enemy)
                            
                if combat_enemies:
                    # Start combat
                    if self.combat_system.start_combat(self.current_character, combat_enemies):
                        # Mark encounter as triggered
                        for room_enemy in active_enemies:
                            room_enemy.triggered = True
                            
        else:
            self.ui_manager.log_error("Destination room not found.")
            
    def _status_command(self) -> None:
        """Show detailed player status."""
        if self.current_character:
            # Show character status
            self.ui_manager.show_character_status(self.current_character)
            
            # Show combat status if in combat
            if self.combat_system.is_active():
                combat_status = self.combat_system.get_combat_status()
                self.ui_manager.log_info("--- Combat Status ---")
                self.ui_manager.log_info(f"Round: {combat_status['round']}")
                self.ui_manager.log_info(f"Auto-combat: {'On' if combat_status['auto_combat'] else 'Off'}")
                self.ui_manager.log_info(f"Enemies remaining: {combat_status['living_enemies']}")
                
                for enemy_info in combat_status['enemies']:
                    status = "alive" if enemy_info['alive'] else "dead"
                    self.ui_manager.log_info(f"  {enemy_info['name']}: {enemy_info['hp']} ({status})")
        else:
            # Fallback to old system
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
            
    def _attack_command(self, args: List[str]) -> None:
        """Handle attack command."""
        if not self.current_character:
            self.ui_manager.log_error("No character loaded.")
            return
            
        # Parse target from arguments
        target_name = None
        if args:
            target_name = ' '.join(args).lower()
            
        # If not in combat, check for enemies in current room and start combat
        if not self.combat_system.is_active():
            room = self.current_area.get_room(self.current_room)
            if not room:
                self.ui_manager.log_error("You are not in combat. Use 'spawn <enemy>' to start a test fight.")
                return
                
            active_enemies = room.get_active_enemies()
            if not active_enemies:
                self.ui_manager.log_error("There are no enemies here to attack.")
                return
                
            # Find the target enemy
            target_room_enemy = None
            if target_name:
                # Look for enemy by name
                for room_enemy in active_enemies:
                    enemy_name = room_enemy.get_display_name().lower()
                    if target_name in enemy_name or enemy_name in target_name:
                        target_room_enemy = room_enemy
                        break
                if not target_room_enemy:
                    self.ui_manager.log_error(f"No enemy named '{target_name}' found here.")
                    return
            else:
                # Use first available enemy
                target_room_enemy = active_enemies[0]
                
            # Create enemy instance(s) and start combat
            # Try as encounter first, then as single enemy
            enemies = self.enemy_factory.create_encounter(target_room_enemy.enemy_type)
            if not enemies:
                # Try as single enemy
                enemy = self.enemy_factory.create_enemy(target_room_enemy.enemy_type)
                if enemy:
                    enemies = [enemy]
                else:
                    self.ui_manager.log_error(f"Failed to create enemy: {target_room_enemy.enemy_type}")
                    return
                
            # Start combat
            if self.combat_system.start_combat(self.current_character, enemies):
                self.current_state = GameState.COMBAT
                self.state = self.current_state
                self.ui_manager.log_success("Combat started!")
                # Mark the room enemy as triggered
                for enemy_id, room_enemy in room.enemies.items():
                    if room_enemy == target_room_enemy:
                        room_enemy.triggered = True
                        break
            else:
                self.ui_manager.log_error("Failed to start combat.")
                return
            
        # Now attack the enemy
        success = self.combat_system.attack_enemy(target_name)
        if not success:
            # Error message already displayed by combat system
            pass
            
    def _auto_combat_command(self) -> None:
        """Handle auto-combat toggle command."""
        if not self.current_character:
            self.ui_manager.log_error("No character loaded.")
            return
            
        if not self.combat_system.is_active():
            self.ui_manager.log_error("You are not in combat.")
            return
            
        self.combat_system.toggle_auto_combat()
        
    def _flee_command(self) -> None:
        """Handle flee command."""
        if not self.current_character:
            self.ui_manager.log_error("No character loaded.")
            return
            
        if not self.combat_system.is_active():
            self.ui_manager.log_error("You are not in combat.")
            return
            
        self.combat_system.flee_combat()
        
    def _spawn_enemy_command(self, args: List[str]) -> None:
        """Handle spawn enemy debug command."""
        if not self.current_character:
            self.ui_manager.log_error("No character loaded.")
            return
            
        if self.combat_system.is_active():
            self.ui_manager.log_error("Already in combat. End current combat first.")
            return
            
        if not args:
            # List available enemies
            enemies = self.enemy_factory.list_available_enemies()
            encounters = self.enemy_factory.list_available_encounters()
            
            self.ui_manager.log_info("Available enemies:")
            for enemy_type in enemies[:10]:  # Show first 10
                info = self.enemy_factory.get_enemy_info(enemy_type)
                if info:
                    self.ui_manager.log_info(f"  {enemy_type} - Level {info.get('level', 1)}, HP {info.get('hp', 10)}")
                    
            self.ui_manager.log_info("Available encounters:")
            for encounter in encounters:
                self.ui_manager.log_info(f"  {encounter}")
                
            return
            
        enemy_or_encounter = args[0].lower()
        
        # Try as encounter first
        enemies = self.enemy_factory.create_encounter(enemy_or_encounter)
        if not enemies:
            # Try as single enemy
            enemy = self.enemy_factory.create_enemy(enemy_or_encounter)
            if enemy:
                enemies = [enemy]
            else:
                self.ui_manager.log_error(f"Unknown enemy or encounter: {enemy_or_encounter}")
                return
                
        # Start combat
        if self.combat_system.start_combat(self.current_character, enemies):
            self.ui_manager.log_success("Combat started! Use 'attack' to fight or 'auto' for auto-combat.")
        else:
            self.ui_manager.log_error("Failed to start combat.")
            
    def _initialize_world_areas(self) -> None:
        """Initialize world areas."""
        try:
            # Import area classes
            from areas.area_tutorial_cave import TutorialCaveArea
            from areas.area_forest_path import ForestPathArea
            
            # Create area instances
            tutorial_cave = TutorialCaveArea()
            forest_path = ForestPathArea()
            
            # Store areas
            self.world_areas = {
                'tutorial_cave': tutorial_cave,
                'forest_path': forest_path
            }
            
            self.ui_manager.log_info("World areas loaded successfully.")
            
        except Exception as e:
            self.ui_manager.log_error(f"Failed to load world areas: {e}")
            
    def start_world_exploration(self, character) -> None:
        """Start world exploration with a character."""
        if not character:
            return
            
        # Set character location or start in tutorial cave
        start_area_id = "tutorial_cave"
        start_room_id = "cave_entrance"
        
        # Check character's saved location
        if hasattr(character, 'current_area') and character.current_area:
            start_area_id = character.current_area
            start_room_id = character.current_room or self.world_areas[start_area_id].get_starting_room()
        else:
            # New character starts in tutorial cave
            character.current_area = start_area_id
            character.current_room = start_room_id
            
        # Set current location
        self.current_area_id = start_area_id
        self.current_area = self.world_areas.get(start_area_id)
        self.current_room = start_room_id
        
        if self.current_area:
            # Mark room as visited and trigger events
            room = self.current_area.get_room(start_room_id)
            if room:
                self.current_area.visit_room(start_room_id)
                
            # Start tutorial if needed
            if start_area_id == "tutorial_cave" and not room.visited:
                self.tutorial_system.start_tutorial()
                
            # Track area discovery
            self.game_completion.track_area_discovery(self.current_area.name)
                
            # Show current room
            self._look_command()
        else:
            self.ui_manager.log_error(f"Could not load area: {start_area_id}")
            
    def _map_command(self) -> None:
        """Show ASCII map of current area."""
        if not self.current_area:
            self.ui_manager.log_error("No area loaded.")
            return
            
        map_display = self.current_area.get_map_display(self.current_room)
        self.ui_manager.log_info(map_display)
        
    def _exits_command(self) -> None:
        """Show available exits from current room."""
        if not self.current_area or not self.current_room:
            self.ui_manager.log_error("No current location.")
            return
            
        room = self.current_area.get_room(self.current_room)
        if not room:
            self.ui_manager.log_error("Current room not found.")
            return
            
        available_exits = room.get_available_exits()
        if not available_exits:
            self.ui_manager.log_info("There are no obvious exits.")
            return
            
        self.ui_manager.log_info("Available exits:")
        for direction, exit_obj in available_exits.items():
            dest_desc = exit_obj.destination_room.replace('_', ' ').title()
            self.ui_manager.log_info(f"  {direction.value} - {dest_desc}")
            
    def _get_command(self, args: List[str]) -> None:
        """Handle get/take item command."""
        if not args:
            self.ui_manager.log_error("Get what? Usage: get <item>")
            return
            
        if not self.current_area or not self.current_room:
            self.ui_manager.log_error("No current location.")
            return
            
        room = self.current_area.get_room(self.current_room)
        if not room:
            self.ui_manager.log_error("Current room not found.")
            return
            
        item_name = ' '.join(args).lower()
        
        # Find matching item
        for item_id, item in room.items.items():
            if item_name in item.name.lower() and item.quantity > 0:
                if not item.can_take:
                    self.ui_manager.log_error(f"You cannot take the {item.name}.")
                    return
                    
                # Initialize inventory system if not done
                if not self.current_character.inventory_system:
                    self.current_character.initialize_item_systems()
                
                # Check if character can carry the item
                from core.item_factory import ItemFactory
                item_factory = ItemFactory()
                actual_item = item_factory.create_item(item_id)
                
                if actual_item and self.current_character.inventory_system.can_add_item(actual_item):
                    # Remove item from room
                    taken_item = room.remove_item(item_id)
                    if taken_item:
                        # Add to character inventory
                        self.current_character.inventory_system.add_item(actual_item)
                        self.ui_manager.log_success(f"You take the {taken_item.name}.")
                        
                        # Trigger tutorial and area events
                        self.tutorial_system.on_player_action('take_item', item_name=taken_item.name)
                        
                        if hasattr(self.current_area, 'on_item_taken'):
                            messages = self.current_area.on_item_taken(item_id, self.current_room)
                            for message in messages:
                                self.ui_manager.log_info(message)
                                
                        return
                else:
                    self.ui_manager.log_error("You can't carry that much weight.")
                    return
                    
        self.ui_manager.log_error(f"There is no {item_name} here to take.")
        
    def _tutorial_command(self, args: List[str]) -> None:
        """Handle tutorial commands."""
        if not args:
            progress = self.tutorial_system.get_tutorial_progress()
            self.ui_manager.log_info(f"Tutorial: {'Enabled' if progress['enabled'] else 'Disabled'}")
            self.ui_manager.log_info(f"Messages shown: {progress['messages_shown']}/{progress['total_messages']}")
            return
            
        command = args[0].lower()
        
        if command in ['on', 'enable']:
            self.tutorial_system.enable_tutorial()
        elif command in ['off', 'disable']:
            self.tutorial_system.disable_tutorial()
        elif command == 'toggle':
            self.tutorial_system.toggle_tutorial()
        else:
            self.ui_manager.log_error("Usage: tutorial [on/off/toggle]")
    
    def _inventory_command(self) -> None:
        """Display character inventory."""
        if not self.current_character:
            self.ui_manager.log_error("No character selected.")
            return
            
        # Initialize inventory system if not done
        if not self.current_character.inventory_system:
            self.current_character.initialize_item_systems()
            
        inventory_display = self.current_character.inventory_system.get_inventory_display()
        self.ui_manager.log_info(inventory_display)
    
    def _equipment_command(self) -> None:
        """Display equipped items."""
        if not self.current_character:
            self.ui_manager.log_error("No character selected.")
            return
            
        # Initialize equipment system if not done
        if not self.current_character.equipment_system:
            self.current_character.initialize_item_systems()
            
        equipment_display = self.current_character.equipment_system.get_equipment_display()
        self.ui_manager.log_info(equipment_display)
    
    def _equip_command(self, args: List[str]) -> None:
        """Equip an item from inventory."""
        if not self.current_character:
            self.ui_manager.log_error("No character selected.")
            return
            
        if not args:
            self.ui_manager.log_error("Equip what? Usage: equip <item>")
            return
            
        # Initialize systems if not done
        if not self.current_character.equipment_system:
            self.current_character.initialize_item_systems()
            
        item_name = ' '.join(args).lower()
        
        # Find item by name
        item_id = self.current_character.inventory_system.find_item_by_name(item_name)
        if not item_id:
            self.ui_manager.log_error(f"You don't have '{item_name}' in your inventory.")
            return
            
        # Try to equip the item
        result = self.current_character.equipment_system.equip_item(item_id)
        self.ui_manager.log_info(result)
    
    def _unequip_command(self, args: List[str]) -> None:
        """Unequip an item to inventory."""
        if not self.current_character:
            self.ui_manager.log_error("No character selected.")
            return
            
        if not args:
            self.ui_manager.log_error("Unequip what? Usage: unequip <slot> (weapon/armor/accessory)")
            return
            
        # Initialize systems if not done
        if not self.current_character.equipment_system:
            self.current_character.initialize_item_systems()
            
        slot_name = args[0].lower()
        result = self.current_character.equipment_system.unequip_item(slot_name)
        self.ui_manager.log_info(result)
    
    def _use_command(self, args: List[str]) -> None:
        """Use a consumable item."""
        if not self.current_character:
            self.ui_manager.log_error("No character selected.")
            return
            
        if not args:
            self.ui_manager.log_error("Use what? Usage: use <item>")
            return
            
        # Initialize systems if not done
        if not self.current_character.inventory_system:
            self.current_character.initialize_item_systems()
            
        item_name = ' '.join(args).lower()
        
        # Find item by name
        item_id = self.current_character.inventory_system.find_item_by_name(item_name)
        if not item_id:
            self.ui_manager.log_error(f"You don't have '{item_name}' in your inventory.")
            return
            
        inv_item = self.current_character.inventory_system.get_item(item_id)
        if not inv_item:
            self.ui_manager.log_error(f"You don't have '{item_name}' in your inventory.")   
            return
            
        # Check if it's a consumable
        from items.base_item import ItemType
        from items.consumables import Consumable
        
        if inv_item.item.item_type != ItemType.CONSUMABLE:
            self.ui_manager.log_error(f"You can't use {inv_item.item.name}.")
            return
            
        # Use the item
        if isinstance(inv_item.item, Consumable):
            result = inv_item.item.use(self.current_character)
            self.ui_manager.log_info(result)
            
            # Remove one from inventory
            self.current_character.inventory_system.remove_item(item_id, 1)
        else:
            self.ui_manager.log_error(f"You can't use {inv_item.item.name}.")
    
    def _drop_command(self, args: List[str]) -> None:
        """Drop an item from inventory."""
        if not self.current_character:
            self.ui_manager.log_error("No character selected.")
            return
            
        if not args:
            self.ui_manager.log_error("Drop what? Usage: drop <item>")
            return
            
        # Initialize systems if not done
        if not self.current_character.inventory_system:
            self.current_character.initialize_item_systems()
            
        item_name = ' '.join(args).lower()
        
        # Find item by name
        item_id = self.current_character.inventory_system.find_item_by_name(item_name)
        if not item_id:
            self.ui_manager.log_error(f"You don't have '{item_name}' in your inventory.")
            return
            
        inv_item = self.current_character.inventory_system.get_item(item_id)
        if not inv_item:
            self.ui_manager.log_error(f"You don't have '{item_name}' in your inventory.")
            return
            
        # Check if item is equipped
        if inv_item.equipped:
            self.ui_manager.log_error(f"You must unequip {inv_item.item.name} before dropping it.")
            return
            
        # Remove from inventory and add to room
        self.current_character.inventory_system.remove_item(item_id, 1)
        
        # Add item to current room
        if self.current_area and hasattr(self.current_area, 'add_item_to_room'):
            self.current_area.add_item_to_room(self.current_room, inv_item.item)
            
        self.ui_manager.log_info(f"You drop the {inv_item.item.name}.")
            
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
                
        # Process combat system
        if self.combat_system.is_active():
            self.combat_system.process_combat_update()
            
        # Process tutorial system
        if self.tutorial_system.enabled:
            self.tutorial_system.update()
            
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
            
    def start_combat(self, enemy) -> None:
        """Start combat with an enemy."""
        if self.combat_system.start_combat(self.current_character, [enemy]):
            self.current_state = GameState.COMBAT
            self.state = self.current_state
            self.ui_manager.log_success("Combat started! Use 'attack' to fight or 'auto' for auto-combat.")
    
    def end_combat(self, victory: bool = True) -> None:
        """End combat and return to normal gameplay."""
        self.current_state = GameState.PLAYING
        self.state = self.current_state
        
        if victory:
            # Track combat victory for statistics
            self.ui_manager.log_success("Combat victorious!")
        else:
            # Player was defeated - restore to 1 HP and show defeat message
            if self.current_character and not self.current_character.is_alive():
                self.current_character.current_hp = 1
                self.ui_manager.log_error("You have been defeated and barely escape with your life!")
                self.ui_manager.log_info("You recover consciousness with 1 hit point remaining.")
    
    def complete_game(self) -> None:
        """Complete the game and show completion screen."""
        if not self.game_completion.game_completed:
            self.game_completion.complete_game()
            
            # Save final character state with completion data
            if self.current_character:
                character_data = self.save_manager._create_character_data(self.current_character)
                completion_data = self.game_completion.save_statistics()
                character_data.update(completion_data)
                self.save_manager._save_character_data(self.current_character.name, character_data)
    
    def shutdown(self) -> None:
        """Shutdown the game engine and clean up resources."""
        self.running = False
        
        # Save character if one is loaded
        if self.current_character:
            character_data = self.save_manager._create_character_data(self.current_character)
            completion_data = self.game_completion.save_statistics()
            character_data.update(completion_data)
            self.save_manager._save_character_data(self.current_character.name, character_data)
        
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