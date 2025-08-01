#!/usr/bin/env python3
"""
Rogue City - Main Entry Point
A MajorMUD-style text RPG built for hackathon demo.

Version: 1.0.0
Development Phase: 6 (Final Polish)

This is the main entry point for the game. It initializes the game engine,
performs system checks, and handles startup/shutdown gracefully.

Features:
- Four character classes with unique abilities and combat styles
- Timer-based combat system with weapon speed differences  
- Complete inventory and equipment management
- Tutorial system for new players
- Achievement and statistics tracking
- Traditional MajorMUD-style command interface
- Cross-platform terminal compatibility
"""

import sys
import os
import traceback
import time
import json
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Game constants
GAME_VERSION = "1.0.0"
GAME_TITLE = "Rogue City"
MIN_PYTHON_VERSION = (3, 6)
MIN_TERMINAL_SIZE = (60, 20)  # width, height
REQUIRED_DIRS = ['data', 'core', 'characters', 'items', 'areas', 'enemies']
REQUIRED_FILES = [
    'data/config/game_settings.json',
    'data/classes/class_definitions.json',
    'data/items/weapons.json',
    'data/items/armor.json',
    'data/areas/tutorial_cave.json'
]

try:
    from core.game_engine import GameEngine
except ImportError as e:
    print("❌ Error importing game engine:")
    print(f"   {e}")
    print()
    print("🔧 Troubleshooting:")
    print("   • Make sure you're running this from the project root directory")
    print("   • Verify all required Python files are present")
    print("   • Check that the 'core' directory exists")
    print()
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📁 Expected files: {', '.join(REQUIRED_FILES[:3])}...")
    sys.exit(1)


def main():
    """
    Main entry point for Rogue City.
    
    Performs comprehensive startup sequence:
    1. System compatibility checks
    2. File integrity verification
    3. Game engine initialization
    4. Main game loop execution
    5. Graceful shutdown handling
    """
    engine = None
    
    try:
        # Show professional startup sequence
        show_startup_sequence()
        
        # Perform comprehensive system checks
        if not perform_system_checks():
            print("System checks failed. Cannot start game.")
            sys.exit(1)
        
        print("\n🎮 Initializing Rogue City game engine...")
        
        # Create and initialize game engine
        engine = GameEngine()
        
        if not engine.initialize():
            print("❌ Failed to initialize game engine.")
            sys.exit(1)
        
        print("✅ Game engine initialized successfully!")
        print("\n🚀 Starting Rogue City...")
        time.sleep(1)  # Brief pause for effect
        
        # Run the main game loop
        engine.run()
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\n🛑 Game interrupted by user.")
        if engine:
            print("💾 Saving game state...")
            engine.shutdown()
        else:
            print("👋 Thank you for playing Rogue City!")
            
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"💥 Unexpected error occurred: {e}"
        
        if engine and hasattr(engine, 'ui_manager') and hasattr(engine.ui_manager, 'stdscr') and engine.ui_manager.stdscr:
            # If UI is initialized, show error through UI system
            try:
                engine.ui_manager.log_error(error_msg)
                engine.ui_manager.log_error("🐛 Please report this bug at: https://github.com/mk-git-0/rogue.city/issues")
                engine.ui_manager.log_error("Press any key to exit...")
                engine.ui_manager.stdscr.getch()
                engine.shutdown()
            except:
                # Fallback if UI system also fails
                print(f"\n{error_msg}")
                print("🐛 Please report this bug at: https://github.com/mk-git-0/rogue.city/issues")
                show_error_details(e)
        else:
            # If UI not initialized, print to console
            print(f"\n{error_msg}")
            print("🐛 Please report this bug at: https://github.com/mk-git-0/rogue.city/issues")
            show_error_details(e)
            
        sys.exit(1)
        
    finally:
        # Ensure clean shutdown
        if engine:
            try:
                engine.shutdown()
            except Exception as shutdown_error:
                print(f"⚠️  Warning: Error during shutdown: {shutdown_error}")
                
        print("\n👋 Thank you for playing Rogue City!")
        print("🌟 Please consider starring the project on GitHub!")


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    print(f"🐍 Checking Python version... ", end="")
    
    if sys.version_info < MIN_PYTHON_VERSION:
        print("❌")
        print(f"\n❌ Error: Rogue City requires Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher.")
        print(f"   You are running Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print("\n🔧 Please upgrade Python and try again.")
        return False
    
    print(f"✅ (Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})")
    return True


def check_terminal_support() -> bool:
    """Check if terminal supports the features we need."""
    print(f"🖥️  Checking terminal compatibility... ", end="")
    
    # Skip curses check since we're using SimpleUIManager
    print("✅ (Using SimpleUI - no curses required)")
    return True


def show_startup_sequence():
    """Show professional startup sequence and game information."""
    print()
    print("🏰" + "=" * 58 + "🏰")
    print(f"    {GAME_TITLE.upper()} v{GAME_VERSION} - MajorMUD-Style Text RPG")
    print("🏰" + "=" * 58 + "🏰")
    print()
    print("🎯 Welcome, adventurer! You're about to enter Rogue City,")
    print("   a classic text-based RPG inspired by the legendary")
    print("   MajorMUD BBS games from the 1990s.")
    print()
    print("✨ Game Features:")
    print("   🗡️  Four character classes with unique combat styles")
    print("   ⚔️  Timer-based combat with weapon speed differences")
    print("   🎒 Complete inventory and equipment management")
    print("   🏆 Achievement system with statistics tracking")
    print("   📚 Built-in tutorial for new players")
    print("   🗺️  Explore tutorial caves and dangerous forests")
    print("   💾 Automatic save/load system")
    print()
    print("🎮 Controls:")
    print("   • Type commands like 'north', 'attack goblin', 'inventory'")
    print("   • Use 'help' for complete command reference")
    print("   • Press Ctrl+C to quit safely at any time")
    print()
    print("🚀 Expected playtime: 45-60 minutes for full experience")
    print()
    
def show_professional_welcome():
    """Show final welcome message before game starts."""
    print("\n🎊 All systems ready! Launching Rogue City...")
    print("\n⭐ Pro tip: New players should start with the Knight class (easiest)")
    print("   or try Rogue for a challenge (hardest but most rewarding)!")
    print()
    
    try:
        print("🎬 Starting in: ", end="")
        for i in range(3, 0, -1):
            print(f"{i}... ", end="", flush=True)
            time.sleep(0.8)
        print("GO! 🚀")
        print()
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\n👋 Game cancelled by user. Goodbye!")
        sys.exit(0)


def check_file_integrity() -> bool:
    """Check if all required game files exist."""
    print(f"📁 Checking game files... ", end="")
    
    missing_dirs = []
    missing_files = []
    
    # Check required directories
    for dir_path in REQUIRED_DIRS:
        if not os.path.isdir(dir_path):
            missing_dirs.append(dir_path)
    
    # Check required files
    for file_path in REQUIRED_FILES:
        if not os.path.isfile(file_path):
            missing_files.append(file_path)
    
    if missing_dirs or missing_files:
        print("❌")
        print("\n❌ Missing required game files:")
        for missing_dir in missing_dirs:
            print(f"   📁 Directory: {missing_dir}")
        for missing_file in missing_files:
            print(f"   📄 File: {missing_file}")
        print("\n🔧 Please ensure you have the complete game installation.")
        return False
    
    print("✅")
    return True

def check_game_data_validity() -> bool:
    """Validate critical game data files."""
    print(f"🔍 Validating game data... ", end="")
    
    try:
        # Test loading critical JSON files
        with open('data/config/game_settings.json', 'r') as f:
            settings = json.load(f)
            if 'game' not in settings or 'combat' not in settings:
                raise ValueError("Invalid game settings structure")
        
        with open('data/classes/class_definitions.json', 'r') as f:
            classes = json.load(f)
            required_classes = ['rogue', 'knight', 'mage', 'mystic']
            for cls in required_classes:
                if cls not in classes:
                    raise ValueError(f"Missing character class: {cls}")
        
        print("✅")
        return True
        
    except Exception as e:
        print("❌")
        print(f"\n❌ Game data validation failed: {e}")
        print("🔧 Game files may be corrupted. Please reinstall.")
        return False

def perform_system_checks() -> bool:
    """Perform comprehensive system compatibility checks."""
    print("🔧 Performing system checks...")
    print()
    
    checks = [
        check_python_version,
        check_terminal_support,
        check_file_integrity,
        check_game_data_validity
    ]
    
    for check in checks:
        if not check():
            return False
    
    print()
    print("✅ All system checks passed!")
    return True

def show_error_details(error: Exception):
    """Show detailed error information for debugging."""
    print("\n📋 Error Details:")
    print(f"   Type: {type(error).__name__}")
    print(f"   Message: {str(error)}")
    print(f"   Python Version: {sys.version}")
    print(f"   Platform: {sys.platform}")
    print()
    print("📄 Full traceback:")
    traceback.print_exc()
    print()
    print("🆘 If this error persists, please:")
    print("   1. Check that your terminal supports curses")
    print("   2. Try running from a different terminal")
    print("   3. Report the issue with the full error above")


if __name__ == "__main__":
    # Run the complete startup sequence
    main()