"""
UI Manager for Rogue City
Manages the split-screen terminal interface using Python's curses library.
"""

import curses
import textwrap
from typing import List, Optional, Tuple
from collections import deque


class UIManager:
    """
    Manages the terminal user interface with split-screen layout.
    Top window (60%): Context display (room descriptions, maps, character info)
    Bottom window (40%): Scrolling command log and input
    """
    
    def __init__(self):
        """Initialize the UI manager."""
        self.stdscr = None
        self.context_win = None
        self.log_win = None
        self.input_win = None
        
        # Window dimensions
        self.total_height = 0
        self.total_width = 0
        self.context_height = 0
        self.log_height = 0
        
        # Content storage
        self.context_content: List[str] = []
        self.log_messages: deque = deque(maxlen=1000)  # Keep last 1000 messages
        self.command_history: deque = deque(maxlen=100)  # Keep last 100 commands
        self.history_index = 0
        
        # UI state
        self.current_input = ""
        self.cursor_pos = 0
        self.scroll_offset = 0
        self.max_log_display = 0
        
    def initialize(self) -> None:
        """Initialize the curses interface."""
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(1)  # Show cursor
        
        # Try to enable colors if available
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            # Define some basic color pairs
            curses.init_pair(1, curses.COLOR_WHITE, -1)    # Normal text
            curses.init_pair(2, curses.COLOR_GREEN, -1)    # Success/positive
            curses.init_pair(3, curses.COLOR_RED, -1)      # Error/danger
            curses.init_pair(4, curses.COLOR_YELLOW, -1)   # Warning/info
            curses.init_pair(5, curses.COLOR_BLUE, -1)     # System messages
            curses.init_pair(6, curses.COLOR_MAGENTA, -1)  # Special/magic
            curses.init_pair(7, curses.COLOR_CYAN, -1)     # UI elements
            
        self._setup_windows()
        self._draw_borders()
        self.refresh_all()
        
    def cleanup(self) -> None:
        """Clean up the curses interface."""
        if self.stdscr:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()
            
    def _setup_windows(self) -> None:
        """Set up the window layout."""
        self.total_height, self.total_width = self.stdscr.getmaxyx()
        
        # Calculate window sizes (60% context, 40% log+input)
        self.context_height = int(self.total_height * 0.6) - 1  # -1 for border
        self.log_height = self.total_height - self.context_height - 3  # -3 for borders and input
        
        # Create windows
        self.context_win = curses.newwin(self.context_height, self.total_width - 2, 1, 1)
        self.log_win = curses.newwin(self.log_height, self.total_width - 2, 
                                   self.context_height + 2, 1)
        self.input_win = curses.newwin(1, self.total_width - 4, 
                                     self.total_height - 2, 2)
        
        # Enable scrolling for windows
        self.context_win.scrollok(True)
        self.log_win.scrollok(True)
        
        # Calculate max log messages that can be displayed
        self.max_log_display = self.log_height
        
    def _draw_borders(self) -> None:
        """Draw borders around the windows."""
        # Main border
        self.stdscr.border()
        
        # Horizontal separator between context and log
        separator_y = self.context_height + 1
        for x in range(1, self.total_width - 1):
            self.stdscr.addch(separator_y, x, curses.ACS_HLINE)
        self.stdscr.addch(separator_y, 0, curses.ACS_LTEE)
        self.stdscr.addch(separator_y, self.total_width - 1, curses.ACS_RTEE)
        
        # Input line separator
        input_separator_y = self.total_height - 3
        for x in range(1, self.total_width - 1):
            self.stdscr.addch(input_separator_y, x, curses.ACS_HLINE)
        self.stdscr.addch(input_separator_y, 0, curses.ACS_LTEE)
        self.stdscr.addch(input_separator_y, self.total_width - 1, curses.ACS_RTEE)
        
        # Add labels
        context_label = " CONTEXT "
        log_label = " LOG "
        input_label = "> "
        
        self.stdscr.addstr(0, 2, context_label, curses.color_pair(7))
        self.stdscr.addstr(separator_y, 2, log_label, curses.color_pair(7))
        self.stdscr.addstr(self.total_height - 2, 1, input_label, curses.color_pair(7))
        
    def handle_resize(self) -> None:
        """Handle terminal resize events."""
        self.stdscr.clear()
        self._setup_windows()
        self._draw_borders()
        self.refresh_context()
        self.refresh_log()
        self.refresh_input()
        self.stdscr.refresh()
        
    def set_context(self, content: List[str]) -> None:
        """
        Set the content for the context window.
        
        Args:
            content: List of strings to display in the context window
        """
        self.context_content = content[:]
        self.refresh_context()
        
    def add_context_line(self, line: str) -> None:
        """
        Add a single line to the context window.
        
        Args:
            line: Line to add to the context
        """
        self.context_content.append(line)
        self.refresh_context()
        
    def clear_context(self) -> None:
        """Clear the context window."""
        self.context_content.clear()
        self.refresh_context()
        
    def log_message(self, message: str, color_pair: int = 1) -> None:
        """
        Add a message to the log window.
        
        Args:
            message: Message to log
            color_pair: Color pair number for the message
        """
        # Wrap long messages
        wrapped_lines = textwrap.wrap(message, self.total_width - 4)
        if not wrapped_lines:
            wrapped_lines = [""]
            
        for line in wrapped_lines:
            self.log_messages.append((line, color_pair))
            
        self.refresh_log()
        
    def log_command(self, command: str) -> None:
        """Log a command that was entered by the player."""
        self.log_message(f"> {command}", curses.color_pair(7))
        
    def log_error(self, message: str) -> None:
        """Log an error message."""
        self.log_message(f"ERROR: {message}", curses.color_pair(3))
        
    def log_success(self, message: str) -> None:
        """Log a success message."""
        self.log_message(message, curses.color_pair(2))
        
    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.log_message(message, curses.color_pair(4))
        
    def log_system(self, message: str) -> None:
        """Log a system message."""
        self.log_message(message, curses.color_pair(5))
        
    def refresh_context(self) -> None:
        """Refresh the context window display."""
        if not self.context_win:
            return
            
        self.context_win.clear()
        
        for i, line in enumerate(self.context_content):
            if i >= self.context_height:
                break
                
            # Wrap long lines
            wrapped_lines = textwrap.wrap(line, self.total_width - 4)
            if not wrapped_lines:
                wrapped_lines = [""]
                
            for j, wrapped_line in enumerate(wrapped_lines):
                if i + j >= self.context_height:
                    break
                try:
                    self.context_win.addstr(i + j, 0, wrapped_line)
                except curses.error:
                    pass  # Ignore errors from writing at edge of window
                    
        self.context_win.refresh()
        
    def refresh_log(self) -> None:
        """Refresh the log window display."""
        if not self.log_win:
            return
            
        self.log_win.clear()
        
        # Show the most recent messages that fit in the window
        messages_to_show = list(self.log_messages)[-self.max_log_display:]
        
        for i, (message, color_pair) in enumerate(messages_to_show):
            if i >= self.log_height:
                break
                
            try:
                self.log_win.addstr(i, 0, message, color_pair)
            except curses.error:
                pass  # Ignore errors from writing at edge of window
                
        self.log_win.refresh()
        
    def refresh_input(self) -> None:
        """Refresh the input window display."""
        if not self.input_win:
            return
            
        self.input_win.clear()
        
        # Display current input, handling overflow
        display_width = self.total_width - 6  # Account for borders and prompt
        display_start = max(0, self.cursor_pos - display_width + 1)
        display_text = self.current_input[display_start:display_start + display_width]
        display_cursor = self.cursor_pos - display_start
        
        try:
            self.input_win.addstr(0, 0, display_text)
            self.input_win.move(0, display_cursor)
        except curses.error:
            pass
            
        self.input_win.refresh()
        
    def refresh_all(self) -> None:
        """Refresh all windows."""
        self.stdscr.refresh()
        self.refresh_context()
        self.refresh_log()
        self.refresh_input()
        
    def get_input(self) -> Optional[str]:
        """
        Get input from the user.
        
        Returns:
            Command string if Enter was pressed, None otherwise
        """
        if not self.input_win:
            return None
            
        try:
            key = self.stdscr.getch()
        except KeyboardInterrupt:
            return "quit"
            
        if key == curses.KEY_RESIZE:
            self.handle_resize()
            return None
            
        elif key == ord('\n') or key == ord('\r'):
            # Enter pressed - return the command
            command = self.current_input.strip()
            if command:
                self.command_history.append(command)
                self.log_command(command)
                
            self.current_input = ""
            self.cursor_pos = 0
            self.history_index = len(self.command_history)
            self.refresh_input()
            return command
            
        elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
            # Backspace
            if self.cursor_pos > 0:
                self.current_input = (self.current_input[:self.cursor_pos-1] + 
                                    self.current_input[self.cursor_pos:])
                self.cursor_pos -= 1
                self.refresh_input()
                
        elif key == curses.KEY_DC:
            # Delete key
            if self.cursor_pos < len(self.current_input):
                self.current_input = (self.current_input[:self.cursor_pos] + 
                                    self.current_input[self.cursor_pos+1:])
                self.refresh_input()
                
        elif key == curses.KEY_LEFT:
            # Left arrow
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                self.refresh_input()
                
        elif key == curses.KEY_RIGHT:
            # Right arrow
            if self.cursor_pos < len(self.current_input):
                self.cursor_pos += 1
                self.refresh_input()
                
        elif key == curses.KEY_UP:
            # Up arrow - previous command in history
            if self.command_history and self.history_index > 0:
                self.history_index -= 1
                self.current_input = self.command_history[self.history_index]
                self.cursor_pos = len(self.current_input)
                self.refresh_input()
                
        elif key == curses.KEY_DOWN:
            # Down arrow - next command in history
            if self.command_history and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.current_input = self.command_history[self.history_index]
                self.cursor_pos = len(self.current_input)
                self.refresh_input()
            elif self.history_index == len(self.command_history) - 1:
                self.history_index = len(self.command_history)
                self.current_input = ""
                self.cursor_pos = 0
                self.refresh_input()
                
        elif key == curses.KEY_HOME or key == 1:  # Ctrl+A
            # Home - move to beginning
            self.cursor_pos = 0
            self.refresh_input()
            
        elif key == curses.KEY_END or key == 5:   # Ctrl+E
            # End - move to end
            self.cursor_pos = len(self.current_input)
            self.refresh_input()
            
        elif 32 <= key <= 126:  # Printable ASCII characters
            # Regular character input
            char = chr(key)
            self.current_input = (self.current_input[:self.cursor_pos] + 
                                char + self.current_input[self.cursor_pos:])
            self.cursor_pos += 1
            self.refresh_input()
            
        return None


# Test function for the UI manager
def _test_ui_manager():
    """Test the UI manager functionality."""
    ui = UIManager()
    
    try:
        ui.initialize()
        
        # Set some test content
        ui.set_context([
            "Welcome to Rogue City!",
            "",
            "You stand in a dark cave entrance.",
            "To the north, you see a faint light.",
            "To the south, the cave extends deeper into darkness.",
            "",
            "Health: 100/100",
            "Mana: 50/50"
        ])
        
        ui.log_system("Game initialized.")
        ui.log_info("Type 'help' for available commands.")
        ui.log_message("You can move with: north, south, east, west")
        
        # Main input loop
        while True:
            command = ui.get_input()
            if command:
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    ui.log_info("Available commands: look, north, south, quit")
                elif command.lower() == 'look':
                    ui.log_message("The cave entrance is dimly lit by sunlight from outside.")
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
    _test_ui_manager()