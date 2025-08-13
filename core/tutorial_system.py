"""
Tutorial System for Rogue City
Context-sensitive guidance and progressive skill introduction.
"""

import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


class TutorialPhase(Enum):
    """Tutorial progression phases."""
    WELCOME = "welcome"
    MOVEMENT = "movement"
    EXAMINATION = "examination"
    ITEMS = "items"
    COMBAT = "combat"
    AUTO_COMBAT = "auto_combat"
    EXPLORATION = "exploration"
    COMPLETION = "completion"


@dataclass
class TutorialMessage:
    """Represents a tutorial message."""
    message_id: str
    phase: TutorialPhase
    content: str
    delay: float = 0.0  # Delay before showing message
    show_once: bool = True  # Only show once per session
    conditions: List[str] = None  # Conditions that must be met
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []


class TutorialSystem:
    """
    Manages tutorial messages and guided learning experience.
    Provides context-sensitive help and tracks player progress.
    """
    
    def __init__(self, ui_manager):
        """Initialize tutorial system."""
        self.ui_manager = ui_manager
        
        # Tutorial state
        self.current_phase = TutorialPhase.WELCOME
        self.enabled = True
        self.messages_shown: set = set()
        self.phase_completion: Dict[TutorialPhase, bool] = {}
        
        # Timing
        self.last_message_time = 0.0
        self.message_queue: List[TutorialMessage] = []
        
        # Player progress tracking
        self.player_actions: Dict[str, int] = {
            'looks': 0,
            'moves': 0,
            'items_taken': 0,
            'attacks': 0,
            'rooms_visited': 0,
            'enemies_defeated': 0
        }
        
        # Callback system for external events
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Initialize tutorial messages
        self._initialize_messages()
        
    def _initialize_messages(self) -> None:
        """Initialize all tutorial messages."""
        self.tutorial_messages: Dict[str, TutorialMessage] = {
            
            # Welcome Phase
            'welcome_message': TutorialMessage(
                'welcome_message',
                TutorialPhase.WELCOME,
                "Welcome to Rogue City! This tutorial will guide you through the basics.\n"
                "You can disable tutorial messages at any time by typing 'tutorial off'."
            ),
            
            'first_look': TutorialMessage(
                'first_look',
                TutorialPhase.EXAMINATION,
                "Great! The 'look' command (or just 'l') shows your surroundings.\n"
                "You can examine specific things by typing 'look <item>' or 'examine <item>'.",
                conditions=['looked_once']
            ),
            
            # Movement Phase
            'movement_intro': TutorialMessage(
                'movement_intro',
                TutorialPhase.MOVEMENT,
                "To move around, use direction commands: north (n), south (s), east (e), west (w).\n"
                "Try moving to explore your surroundings!"
            ),
            
            'first_move': TutorialMessage(
                'first_move',
                TutorialPhase.MOVEMENT,
                "Excellent! You can move between rooms using directional commands.\n"
                "Type 'exits' to see all available directions from your current location.",
                conditions=['moved_once']
            ),
            
            # Items Phase
            'item_discovery': TutorialMessage(
                'item_discovery',
                TutorialPhase.ITEMS,
                "You found an item! Use 'get <item name>' to pick up items.\n"
                "Items you carry can be used in combat or for other purposes.",
                conditions=['item_in_room']
            ),
            
            'first_item_taken': TutorialMessage(
                'first_item_taken',
                TutorialPhase.ITEMS,
                "Good! You picked up your first item. You can see what you're carrying\n"
                "by typing 'inventory' or 'inv'. Items may help you in combat!",
                conditions=['item_taken']
            ),
            
            # Combat Phase
            'combat_intro': TutorialMessage(
                'combat_intro',
                TutorialPhase.COMBAT,
                "An enemy appears! Combat in Rogue City is turn-based.\n"
                "Use 'attack' to fight. Some classes and weapons grant multiple attacks per turn.",
                conditions=['enemy_present']
            ),
            
            'first_attack': TutorialMessage(
                'first_attack',
                TutorialPhase.COMBAT,
                "Well done! Combat uses dice rolls - your attack bonus and the enemy's\n"
                "armor class determine if you hit. Higher numbers are better!",
                conditions=['attacked_once']
            ),
            
            'auto_combat_hint': TutorialMessage(
                'auto_combat_hint',
                TutorialPhase.AUTO_COMBAT,
                "Tip: Type 'auto' to enable auto-combat. Your character will automatically\n"
                "attack repeatedly. Use 'auto' again to turn it off.",
                delay=3.0,
                conditions=['in_combat']
            ),
            
            'combat_victory': TutorialMessage(
                'combat_victory',
                TutorialPhase.COMBAT,
                "Victory! You defeated your first enemy and gained experience.\n"
                "Experience helps you level up, making you stronger.",
                conditions=['enemy_defeated']
            ),
            
            # Resting hint (contextual)
            'rest_hint': TutorialMessage(
                'rest_hint',
                TutorialPhase.EXPLORATION,
                "Tip: You are wounded. Type 'rest' to recover health and mana over time.\n"
                "Resting is faster in safe areas like clearings and the tutorial cave.",
                show_once=True
            ),
            
            # Exploration Phase
            'map_hint': TutorialMessage(
                'map_hint',
                TutorialPhase.EXPLORATION,
                "You can type 'map' to see an ASCII map of your current area.\n"
                "This helps you navigate and track your exploration progress.",
                conditions=['multiple_rooms_visited']
            ),
            
            'exploration_progress': TutorialMessage(
                'exploration_progress',
                TutorialPhase.EXPLORATION,
                "Great exploring! You're making good progress through the area.\n"
                "Keep exploring to find more items, enemies, and secrets.",
                conditions=['good_exploration_progress']
            ),
            
            # Completion Phase
            'tutorial_complete': TutorialMessage(
                'tutorial_complete',
                TutorialPhase.COMPLETION,
                "Congratulations! You've completed the tutorial. You now know the basics:\n"
                "movement, combat, items, and exploration. Good luck on your adventure!"
            )
        }
        
    def enable_tutorial(self) -> None:
        """Enable tutorial messages."""
        self.enabled = True
        self.ui_manager.log_system("Tutorial messages enabled.")
        
    def disable_tutorial(self) -> None:
        """Disable tutorial messages."""
        self.enabled = False
        self.ui_manager.log_system("Tutorial messages disabled.")
        
    def toggle_tutorial(self) -> bool:
        """Toggle tutorial on/off."""
        if self.enabled:
            self.disable_tutorial()
        else:
            self.enable_tutorial()
        return self.enabled
        
    def trigger_tutorial(self, message_id: str, **context) -> bool:
        """
        Trigger a tutorial message if conditions are met.
        
        Args:
            message_id: ID of message to trigger
            **context: Additional context data
            
        Returns:
            True if message was queued/shown
        """
        if not self.enabled:
            return False
            
        if message_id not in self.tutorial_messages:
            return False
            
        message = self.tutorial_messages[message_id]
        
        # Check if already shown and should only show once
        if message.show_once and message_id in self.messages_shown:
            return False
            
        # Check conditions
        if not self._check_conditions(message.conditions, context):
            return False
            
        # Queue or show message
        if message.delay > 0:
            # Add to queue with delay
            message.delay = time.time() + message.delay
            self.message_queue.append(message)
        else:
            # Show immediately
            self._show_message(message)
            
        return True
        
    def _check_conditions(self, conditions: List[str], context: Dict[str, Any]) -> bool:
        """Check if message conditions are met."""
        if not conditions:
            return True
            
        for condition in conditions:
            if condition == 'looked_once' and self.player_actions['looks'] > 0:
                continue
            elif condition == 'moved_once' and self.player_actions['moves'] > 0:
                continue
            elif condition == 'item_in_room' and context.get('items_in_room', 0) > 0:
                continue
            elif condition == 'item_taken' and self.player_actions['items_taken'] > 0:
                continue
            elif condition == 'enemy_present' and context.get('enemies_in_room', 0) > 0:
                continue
            elif condition == 'attacked_once' and self.player_actions['attacks'] > 0:
                continue
            elif condition == 'in_combat' and context.get('in_combat', False):
                continue
            elif condition == 'enemy_defeated' and self.player_actions['enemies_defeated'] > 0:
                continue
            elif condition == 'multiple_rooms_visited' and self.player_actions['rooms_visited'] >= 3:
                continue
            elif condition == 'good_exploration_progress' and self.player_actions['rooms_visited'] >= 5:
                continue
            else:
                return False  # Condition not met
                
        return True  # All conditions met
        
    def _show_message(self, message: TutorialMessage) -> None:
        """Display a tutorial message."""
        self.ui_manager.log_system(f"[TUTORIAL] {message.content}")
        self.messages_shown.add(message.message_id)
        self.last_message_time = time.time()
        
    def update(self) -> None:
        """Update tutorial system, process queued messages."""
        if not self.enabled:
            return
            
        current_time = time.time()
        
        # Process queued messages
        ready_messages = []
        remaining_messages = []
        
        for message in self.message_queue:
            if current_time >= message.delay:
                ready_messages.append(message)
            else:
                remaining_messages.append(message)
                
        # Show ready messages
        for message in ready_messages:
            self._show_message(message)
            
        # Keep unready messages in queue
        self.message_queue = remaining_messages
        
    def on_player_action(self, action: str, **context) -> None:
        """
        Handle player action and trigger appropriate tutorials.
        
        Args:
            action: Action performed ('look', 'move', 'attack', etc.)
            **context: Additional context about the action
        """
        if not self.enabled:
            return
            
        # Update action counters
        if action == 'look':
            self.player_actions['looks'] += 1
            if self.player_actions['looks'] == 1:
                self.trigger_tutorial('first_look', **context)
                
        elif action == 'move':
            self.player_actions['moves'] += 1
            if self.player_actions['moves'] == 1:
                self.trigger_tutorial('first_move', **context)
            elif self.player_actions['moves'] == 3:
                self.trigger_tutorial('map_hint', **context)
                
        elif action == 'take_item':
            self.player_actions['items_taken'] += 1
            if self.player_actions['items_taken'] == 1:
                self.trigger_tutorial('first_item_taken', **context)
                
        elif action == 'attack':
            self.player_actions['attacks'] += 1
            if self.player_actions['attacks'] == 1:
                self.trigger_tutorial('first_attack', **context)
                # Queue auto-combat hint
                self.trigger_tutorial('auto_combat_hint', **context)
                
        elif action == 'defeat_enemy':
            self.player_actions['enemies_defeated'] += 1
            if self.player_actions['enemies_defeated'] == 1:
                self.trigger_tutorial('combat_victory', **context)
                
        elif action == 'enter_room':
            self.player_actions['rooms_visited'] += 1
            if self.player_actions['rooms_visited'] == 5:
                self.trigger_tutorial('exploration_progress', **context)
                
        # Check for contextual tutorials
        if context.get('items_in_room', 0) > 0:
            self.trigger_tutorial('item_discovery', **context)
            
        if context.get('enemies_in_room', 0) > 0:
            self.trigger_tutorial('combat_intro', **context)
            
    def start_tutorial(self) -> None:
        """Start the tutorial sequence."""
        if self.enabled:
            self.trigger_tutorial('welcome_message')
            # Queue movement intro
            movement_msg = self.tutorial_messages['movement_intro']
            movement_msg.delay = time.time() + 2.0
            self.message_queue.append(movement_msg)
            
    def complete_tutorial(self) -> None:
        """Mark tutorial as complete."""
        self.current_phase = TutorialPhase.COMPLETION
        self.trigger_tutorial('tutorial_complete')
        
    def get_tutorial_progress(self) -> Dict[str, Any]:
        """Get tutorial completion progress."""
        return {
            'enabled': self.enabled,
            'current_phase': self.current_phase.value,
            'messages_shown': len(self.messages_shown),
            'total_messages': len(self.tutorial_messages),
            'player_actions': self.player_actions.copy(),
            'phases_complete': {
                phase.value: self.phase_completion.get(phase, False)
                for phase in TutorialPhase
            }
        }
        
    def reset_tutorial(self) -> None:
        """Reset tutorial progress for new character."""
        self.current_phase = TutorialPhase.WELCOME
        self.messages_shown.clear()
        self.phase_completion.clear()
        self.message_queue.clear()
        self.player_actions = {key: 0 for key in self.player_actions}
        
    def add_event_callback(self, event: str, callback: Callable) -> None:
        """Add callback for tutorial events."""
        if event not in self.event_callbacks:
            self.event_callbacks[event] = []
        self.event_callbacks[event].append(callback)
        
    def trigger_event(self, event: str, **context) -> None:
        """Trigger event callbacks."""
        if event in self.event_callbacks:
            for callback in self.event_callbacks[event]:
                try:
                    callback(**context)
                except Exception as e:
                    print(f"Tutorial event callback error: {e}")
                    
    def get_contextual_help(self, context: str) -> Optional[str]:
        """Get contextual help message for current situation."""
        help_messages = {
            'lost': "Use 'map' to see where you are, and 'exits' to see where you can go.",
            'combat': "In combat, use 'attack' to fight or 'auto' for automatic combat.",  
            'inventory': "Type 'inventory' or 'inv' to see what you're carrying.",
            'stuck': "Try 'look' to examine your surroundings, or 'help' for commands.",
            'items': "Use 'get <item>' to pick up items you see in the room.",
            'navigation': "Use north (n), south (s), east (e), west (w) to move around.",
        }
        
        return help_messages.get(context)
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize tutorial state for saving."""
        return {
            'enabled': self.enabled,
            'current_phase': self.current_phase.value,
            'messages_shown': list(self.messages_shown),
            'player_actions': self.player_actions.copy(),
            'phase_completion': {
                phase.value: completed 
                for phase, completed in self.phase_completion.items()
            }
        }
        
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore tutorial state from save data."""
        self.enabled = data.get('enabled', True)
        phase_str = data.get('current_phase', TutorialPhase.WELCOME.value)
        try:
            self.current_phase = TutorialPhase(phase_str)
        except ValueError:
            self.current_phase = TutorialPhase.WELCOME
            
        self.messages_shown = set(data.get('messages_shown', []))
        self.player_actions.update(data.get('player_actions', {}))
        
        phase_data = data.get('phase_completion', {})
        for phase_str, completed in phase_data.items():
            try:
                phase = TutorialPhase(phase_str)
                self.phase_completion[phase] = completed
            except ValueError:
                continue


# Test function for tutorial system
def _test_tutorial_system():
    """Test tutorial system functionality."""
    class MockUIManager:
        def log_system(self, msg): print(f"SYSTEM: {msg}")
    
    # Create tutorial system
    ui_manager = MockUIManager()
    tutorial = TutorialSystem(ui_manager)
    
    # Test basic functionality
    assert tutorial.enabled == True
    
    # Test welcome message
    tutorial.start_tutorial()
    assert 'welcome_message' in tutorial.messages_shown
    
    # Test action tracking
    tutorial.on_player_action('look')
    assert tutorial.player_actions['looks'] == 1
    
    # Test conditional message
    tutorial.on_player_action('look')  # Should trigger first_look
    assert 'first_look' in tutorial.messages_shown
    
    # Test tutorial toggle
    tutorial.toggle_tutorial()
    assert tutorial.enabled == False
    
    tutorial.toggle_tutorial()
    assert tutorial.enabled == True
    
    print("Tutorial system tests passed!")


if __name__ == "__main__":
    _test_tutorial_system()