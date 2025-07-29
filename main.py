#!/usr/bin/env python3
"""
Rogue City - Main Entry Point
A MajorMUD-style text RPG built for hackathon demo.

This is the main entry point for the game. It initializes the game engine
and handles any startup errors gracefully.
"""

import sys
import os
import traceback

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from core.game_engine import GameEngine
except ImportError as e:
    print(f"Error importing game engine: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


def main():
    """
    Main entry point for Rogue City.
    
    Initializes the game engine and starts the main game loop.
    Handles errors gracefully and ensures clean shutdown.
    """
    engine = None
    
    try:
        # Create and run the game engine
        engine = GameEngine()
        engine.run()
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        if engine:
            engine.shutdown()
        else:
            print("\nGame interrupted by user.")
            
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"Unexpected error occurred: {e}"
        
        if engine and hasattr(engine.ui_manager, 'stdscr') and engine.ui_manager.stdscr:
            # If UI is initialized, show error through UI
            engine.ui_manager.log_error(error_msg)
            engine.ui_manager.log_error("Please report this bug to the developers.")
            import time
            time.sleep(3)  # Give user time to read error
            engine.shutdown()
        else:
            # If UI not initialized, print to console
            print(f"\n{error_msg}")
            print("Please report this bug to the developers.")
            print("\nFull error traceback:")
            traceback.print_exc()
            
        sys.exit(1)
        
    finally:
        # Ensure clean shutdown
        if engine:
            try:
                engine.shutdown()
            except:
                pass  # Ignore errors during shutdown


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 6):
        print("Error: Rogue City requires Python 3.6 or higher.")
        print(f"You are running Python {sys.version}")
        sys.exit(1)


def check_terminal_support():
    """Check if terminal supports the features we need."""
    import curses
    
    try:
        # Test basic curses functionality
        stdscr = curses.initscr()
        height, width = stdscr.getmaxyx()
        curses.endwin()
        
        # Check minimum terminal size
        if height < 20 or width < 60:
            print(f"Warning: Terminal size ({width}x{height}) is small.")
            print("For best experience, use a terminal at least 60x20.")
            print("Press Enter to continue anyway, or Ctrl+C to exit.")
            input()
            
    except Exception as e:
        print(f"Error: Terminal does not support required features: {e}")
        print("Make sure you're running in a proper terminal (not an IDE console).")
        sys.exit(1)


def show_welcome_message():
    """Show welcome message and game info."""
    print("=" * 60)
    print("    ROGUE CITY - A MajorMUD-Style Text RPG")
    print("=" * 60)
    print()
    print("Welcome to Rogue City, a classic text-based RPG inspired by")
    print("the legendary MajorMUD BBS game from the 1990s.")
    print()
    print("Game Features:")
    print("  • Four character classes with unique combat styles")
    print("  • Timer-based combat system with weapon speed differences")
    print("  • Split-screen terminal interface")
    print("  • Classic dungeon crawling adventure")
    print()
    print("Controls:")
    print("  • Use arrow keys to navigate command history")
    print("  • Type 'help' in-game for available commands")
    print("  • Press Ctrl+C to quit at any time")
    print()
    print("Starting game in 3 seconds...")
    print("(Press Ctrl+C now to cancel)")
    print()
    
    try:
        import time
        for i in range(3, 0, -1):
            print(f"  {i}...", end='', flush=True)
            time.sleep(1)
        print(" GO!")
        print()
    except KeyboardInterrupt:
        print("\nGame cancelled by user.")
        sys.exit(0)


if __name__ == "__main__":
    # Perform pre-flight checks
    check_python_version()
    
    # Show welcome message
    show_welcome_message()
    
    # Check terminal compatibility
    check_terminal_support()
    
    # Run the game
    main()