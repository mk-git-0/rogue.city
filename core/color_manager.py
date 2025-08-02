"""
Color Manager for Rogue City
Centralized color management using colorama for cross-platform terminal colors.
"""

try:
    from colorama import Fore, Back, Style, init
    COLORAMA_AVAILABLE = True
    init(autoreset=True)  # Auto-reset colors after each print
except ImportError:
    COLORAMA_AVAILABLE = False
    

class ColorManager:
    """
    Manages terminal colors for different game elements.
    Provides fallback when colorama is not available.
    """
    
    def __init__(self, enable_colors: bool = True):
        """
        Initialize color manager.
        
        Args:
            enable_colors: Whether to enable color output
        """
        self.colors_enabled = enable_colors and COLORAMA_AVAILABLE
        
        # Color mappings for game elements
        if self.colors_enabled:
            self.colors = {
                # Game elements
                'item': Fore.CYAN,
                'enemy': Fore.RED,
                'exit': Fore.GREEN,
                'object': Fore.YELLOW,
                
                # Message types
                'error': Fore.RED,
                'success': Fore.GREEN,
                'combat': Fore.MAGENTA,
                'system': Fore.BLUE,
                'info': Fore.WHITE,
                
                # Special effects
                'critical': Fore.YELLOW + Style.BRIGHT,
                'reset': Style.RESET_ALL
            }
        else:
            # No-color fallback
            self.colors = {key: '' for key in [
                'item', 'enemy', 'exit', 'object', 
                'error', 'success', 'combat', 'system', 'info',
                'critical', 'reset'
            ]}
    
    def colorize(self, text: str, color_type: str) -> str:
        """
        Apply color to text based on type.
        
        Args:
            text: Text to colorize
            color_type: Color type from self.colors
            
        Returns:
            Colored text string
        """
        if not self.colors_enabled:
            return text
            
        color = self.colors.get(color_type, '')
        if color:
            return f"{color}{text}{self.colors['reset']}"
        return text
    
    def colorize_item(self, item_name: str) -> str:
        """Colorize an item name."""
        return self.colorize(item_name, 'item')
    
    def colorize_enemy(self, enemy_name: str) -> str:
        """Colorize an enemy name."""
        return self.colorize(enemy_name, 'enemy')
    
    def colorize_exit(self, exit_name: str) -> str:
        """Colorize an exit/direction."""
        return self.colorize(exit_name, 'exit')
    
    def colorize_object(self, object_name: str) -> str:
        """Colorize an interactive object."""
        return self.colorize(object_name, 'object')
    
    def colorize_items_list(self, items: list) -> list:
        """Colorize a list of item names."""
        return [self.colorize_item(item) for item in items]
    
    def colorize_enemies_list(self, enemies: list) -> list:
        """Colorize a list of enemy names."""
        return [self.colorize_enemy(enemy) for enemy in enemies]
    
    def colorize_exits_list(self, exits: list) -> list:
        """Colorize a list of exit directions."""
        return [self.colorize_exit(exit) for exit in exits]
    
    def get_message_color(self, message_type: str) -> str:
        """Get color code for message type."""
        return self.colors.get(message_type, '')
    
    def format_error_message(self, message: str) -> str:
        """Format an error message with color."""
        return self.colorize(message, 'error')
    
    def format_success_message(self, message: str) -> str:
        """Format a success message with color.""" 
        return self.colorize(message, 'success')
    
    def format_combat_message(self, message: str) -> str:
        """Format a combat message with color."""
        return self.colorize(message, 'combat')
    
    def format_system_message(self, message: str) -> str:
        """Format a system message with color."""
        return self.colorize(message, 'system')
    
    def format_info_message(self, message: str) -> str:
        """Format an info message with color."""
        return self.colorize(message, 'info')
    
    def format_critical_message(self, message: str) -> str:
        """Format a critical hit or important message."""
        return self.colorize(message, 'critical')
    
    def disable_colors(self) -> None:
        """Disable color output."""
        self.colors_enabled = False
        self.colors = {key: '' for key in self.colors.keys()}
    
    def enable_colors(self) -> None:
        """Enable color output if colorama is available."""
        if COLORAMA_AVAILABLE:
            self.__init__(enable_colors=True)
    
    def is_available(self) -> bool:
        """Check if colorama is available."""
        return COLORAMA_AVAILABLE
    
    def is_enabled(self) -> bool:
        """Check if colors are currently enabled."""
        return self.colors_enabled


# Test function for color manager
def _test_color_manager():
    """Test the color manager functionality."""
    cm = ColorManager()
    
    print("=== Color Manager Test ===")
    print(f"Colorama available: {cm.is_available()}")
    print(f"Colors enabled: {cm.is_enabled()}")
    print()
    
    # Test game element colors
    print("Game Elements:")
    print(f"Items: {cm.colorize_item('rusty sword')}, {cm.colorize_item('healing potion')}")
    print(f"Enemies: {cm.colorize_enemy('goblin')}, {cm.colorize_enemy('orc warrior')}")
    print(f"Exits: {', '.join(cm.colorize_exits_list(['north', 'south', 'east', 'west']))}")
    print(f"Objects: {cm.colorize_object('wooden chest')}, {cm.colorize_object('ancient lever')}")
    print()
    
    # Test message types
    print("Message Types:")
    print(cm.format_error_message("ERROR: Invalid command"))
    print(cm.format_success_message("SUCCESS: Character saved"))
    print(cm.format_combat_message("COMBAT: You attack the goblin"))
    print(cm.format_system_message("SYSTEM: Game started"))
    print(cm.format_info_message("INFO: Type 'help' for commands"))
    print(cm.format_critical_message("CRITICAL HIT! Maximum damage!"))
    print()
    
    # Test disable/enable
    print("Testing disable/enable:")
    cm.disable_colors()
    print(f"Colors disabled: {cm.colorize_item('no color item')}")
    cm.enable_colors()
    print(f"Colors re-enabled: {cm.colorize_item('colored item')}")


if __name__ == "__main__":
    _test_color_manager()