"""
Game Engine for Rogue City
Central game state management and main game loop coordination.
"""

import time
import signal
import sys
from typing import Dict, Any, Optional, List
from enum import Enum

from .ui_manager import UIManager
from .dice_system import DiceSystem
from .timer_system import TimerSystem


class GameState(Enum):
    """Enumeration of possible game states."""
    MENU = "menu"
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
        self.ui_manager = UIManager()
        self.dice_system = DiceSystem(show_rolls=True)
        self.timer_system = TimerSystem()
        
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
        """Update the context window with current game state."""
        context_lines = []
        
        # Game title
        context_lines.append("=== ROGUE CITY ===")
        context_lines.append("")
        
        # Current area
        area = self.game_data.get('current_area', {})
        context_lines.append(f"Location: {area.get('name', 'Unknown')}")
        context_lines.append("")
        context_lines.append(area.get('description', 'You see nothing special.'))
        context_lines.append("")
        
        # Exits
        exits = area.get('exits', [])
        if exits:
            context_lines.append(f"Exits: {', '.join(exits)}")
        else:
            context_lines.append("No obvious exits.")
        context_lines.append("")
        
        # Player status
        player = self.game_data.get('player', {})
        context_lines.append("=== CHARACTER STATUS ===")
        context_lines.append(f"Name: {player.get('name', 'Unknown')}")
        context_lines.append(f"Level: {player.get('level', 1)}")
        context_lines.append(f"Health: {player.get('health', 0)}/{player.get('max_health', 0)}")
        context_lines.append(f"Mana: {player.get('mana', 0)}/{player.get('max_mana', 0)}")
        context_lines.append("")
        
        # Game state info
        if self.current_state != GameState.PLAYING:
            context_lines.append(f"State: {self.current_state.value.upper()}")
            
        # Debug info (if needed)
        if hasattr(self, '_show_debug') and self._show_debug:
            context_lines.append("=== DEBUG INFO ===")
            context_lines.append(f"FPS: {self.actual_fps:.1f}")
            context_lines.append(f"Timer Queue: {self.timer_system.get_queue_size()}")
            context_lines.append(f"Frame: {self.frame_count}")
            
        self.ui_manager.set_context(context_lines)
        
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
        elif self.current_state == GameState.PLAYING:
            self._handle_game_command(cmd, args)
        elif self.current_state == GameState.PAUSED:
            self._handle_pause_command(cmd, args)
        else:
            self.ui_manager.log_error(f"Unknown game state: {self.current_state}")
            
    def _handle_menu_command(self, cmd: str, args: List[str]) -> None:
        """Handle commands in menu state."""
        if cmd in ['start', 'play', 'begin']:
            self.current_state = GameState.PLAYING
            self.ui_manager.log_success("Game started! Adventure awaits...")
            self._update_context_display()
        elif cmd in ['quit', 'exit', 'q']:
            self.shutdown()
        else:
            self.ui_manager.log_info("Menu commands: start, quit")
            
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
        self.ui_manager.log_message(area.get('description', 'You see nothing special.'))
        
        exits = area.get('exits', [])
        if exits:
            self.ui_manager.log_message(f"Exits: {', '.join(exits)}")
            
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
        self.ui_manager.log_system("Welcome to Rogue City!")
        self.ui_manager.log_info("Type 'start' to begin your adventure, or 'quit' to exit.")
        
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
    assert isinstance(engine.ui_manager, UIManager)
    assert isinstance(engine.dice_system, DiceSystem)
    assert isinstance(engine.timer_system, TimerSystem)
    
    print("Game engine tests passed!")


if __name__ == "__main__":
    # Run tests if called directly
    _test_game_engine()