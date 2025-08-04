"""
Stealth System for Rogue City
Manages stealth mode, hiding, backstab attacks, and stealth detection mechanics.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class StealthState(Enum):
    """Stealth state enumeration."""
    VISIBLE = "visible"
    SNEAKING = "sneaking"
    HIDDEN = "hidden"
    DETECTED = "detected"


class StealthSystem:
    """
    Manages stealth mechanics including:
    - Stealth mode for movement
    - Hiding in rooms
    - Backstab attacks with multipliers
    - Stealth detection and breaking
    """
    
    def __init__(self, dice_system, ui_manager):
        """Initialize the stealth system."""
        self.dice_system = dice_system
        self.ui_manager = ui_manager
        
        # Stealth state tracking
        self.character_stealth_states: Dict[str, StealthState] = {}
        self.stealth_bonuses: Dict[str, int] = {}
        
        # Class-specific stealth abilities
        self.stealth_classes = {
            'rogue': {'skill_bonus': 8, 'backstab_base': 3, 'backstab_max': 5},
            'thief': {'skill_bonus': 6, 'backstab_base': 2, 'backstab_max': 5},
            'ninja': {'skill_bonus': 10, 'backstab_base': 3, 'backstab_max': 5},
            'ranger': {'skill_bonus': 4, 'backstab_base': 0, 'backstab_max': 0}  # Limited stealth
        }
        
    def can_use_stealth(self, character) -> bool:
        """Check if character can use stealth abilities."""
        if not hasattr(character, 'character_class'):
            return False
        return character.character_class.lower() in self.stealth_classes
    
    def get_stealth_state(self, character) -> StealthState:
        """Get character's current stealth state."""
        char_id = self._get_character_id(character)
        return self.character_stealth_states.get(char_id, StealthState.VISIBLE)
    
    def enter_stealth_mode(self, character) -> bool:
        """
        Attempt to enter stealth mode for movement.
        
        Returns:
            True if stealth mode activated successfully
        """
        if not self.can_use_stealth(character):
            self.ui_manager.log_error("You don't know how to move stealthily.")
            return False
        
        char_id = self._get_character_id(character)
        current_state = self.get_stealth_state(character)
        
        if current_state == StealthState.SNEAKING:
            self.ui_manager.log_info("You are already moving stealthily.")
            return True
        
        # Check for heavy armor penalty
        stealth_penalty = self._get_stealth_penalty(character)
        if stealth_penalty >= 50:  # Heavy armor makes stealth nearly impossible
            self.ui_manager.log_error("Your heavy armor makes it impossible to move stealthily.")
            return False
        
        # Calculate stealth skill check
        stealth_bonus = self._get_stealth_skill_bonus(character)
        base_chance = 60 + stealth_bonus - stealth_penalty
        
        # Roll for stealth success
        roll = random.randint(1, 100)
        if roll <= base_chance:
            self.character_stealth_states[char_id] = StealthState.SNEAKING
            self.ui_manager.log_success("You attempt to move stealthily.")
            self.ui_manager.log_system("[Stealth mode activated - movement uses stealth checks]")
            return True
        else:
            self.ui_manager.log_error("You fail to move quietly.")
            return False
    
    def exit_stealth_mode(self, character) -> bool:
        """Exit stealth mode."""
        char_id = self._get_character_id(character)
        current_state = self.get_stealth_state(character)
        
        if current_state == StealthState.VISIBLE:
            self.ui_manager.log_info("You are not in stealth mode.")
            return False
        
        self.character_stealth_states[char_id] = StealthState.VISIBLE
        self.ui_manager.log_success("You stop trying to move stealthily.")
        self.ui_manager.log_system("[Normal movement resumed]")
        return True
    
    def attempt_hide(self, character, area=None) -> bool:
        """
        Attempt to hide in current location.
        
        Returns:
            True if hiding was successful
        """
        if not self.can_use_stealth(character):
            self.ui_manager.log_error("You don't know how to hide effectively.")
            return False
        
        char_id = self._get_character_id(character)
        current_state = self.get_stealth_state(character)
        
        if current_state == StealthState.HIDDEN:
            self.ui_manager.log_info("You are already hiding.")
            return True
        
        # Calculate hide skill check
        stealth_bonus = self._get_stealth_skill_bonus(character)
        stealth_penalty = self._get_stealth_penalty(character)
        
        # Area-based hiding bonuses/penalties
        area_bonus = 0
        if area and hasattr(area, 'description'):
            description = area.description.lower()
            if any(word in description for word in ['shadow', 'dark', 'corner', 'alcove']):
                area_bonus = 10
            elif any(word in description for word in ['bright', 'open', 'lit', 'exposed']):
                area_bonus = -10
        
        base_chance = 70 + stealth_bonus - stealth_penalty + area_bonus
        
        # Roll for hide success
        roll = random.randint(1, 100)
        if roll <= base_chance:
            self.character_stealth_states[char_id] = StealthState.HIDDEN
            self.ui_manager.log_success("You find a good hiding spot and conceal yourself.")
            return True
        else:
            self.ui_manager.log_error("You cannot find a suitable place to hide here.")
            return False
    
    def attempt_backstab(self, attacker, target, combat_system=None) -> Tuple[bool, int]:
        """
        Attempt a backstab attack with damage multiplier.
        
        Returns:
            Tuple of (success, damage_multiplier)
        """
        if not self.can_use_stealth(attacker):
            return False, 1
        
        attacker_class = attacker.character_class.lower()
        if attacker_class not in self.stealth_classes:
            return False, 1
        
        stealth_info = self.stealth_classes[attacker_class]
        if stealth_info['backstab_base'] == 0:
            return False, 1  # Rangers can't backstab
        
        # Must be in stealth mode or hidden
        current_state = self.get_stealth_state(attacker)
        if current_state not in [StealthState.SNEAKING, StealthState.HIDDEN]:
            self.ui_manager.log_error("You must be in stealth mode to backstab!")
            return False, 1
        
        # Calculate backstab multiplier based on class and level
        level = getattr(attacker, 'level', 1)
        base_multiplier = stealth_info['backstab_base']
        max_multiplier = stealth_info['backstab_max']
        
        # Multiplier progression by class
        if attacker_class == 'thief':
            if level <= 3:
                multiplier = 2
            elif level <= 7:
                multiplier = 3
            elif level <= 12:
                multiplier = 4
            else:
                multiplier = 5
        elif attacker_class == 'rogue':
            if level <= 5:
                multiplier = 3
            elif level <= 10:
                multiplier = 4
            else:
                multiplier = 5
        elif attacker_class == 'ninja':
            if level <= 4:
                multiplier = 3
            elif level <= 9:
                multiplier = 4
            else:
                multiplier = 5
        else:
            multiplier = base_multiplier
        
        # Stealth is broken after backstab
        char_id = self._get_character_id(attacker)
        self.character_stealth_states[char_id] = StealthState.DETECTED
        
        return True, multiplier
    
    def break_stealth(self, character, reason: str = "action") -> None:
        """
        Break character's stealth state.
        
        Args:
            character: Character whose stealth is broken
            reason: Reason for breaking stealth (action, detected, combat, etc.)
        """
        char_id = self._get_character_id(character)
        current_state = self.get_stealth_state(character)
        
        if current_state == StealthState.VISIBLE:
            return  # Already visible
        
        self.character_stealth_states[char_id] = StealthState.VISIBLE
        
        # Show appropriate message based on reason
        if reason == "backstab":
            self.ui_manager.log_system("Your stealth is broken after the attack.")
        elif reason == "combat":
            self.ui_manager.log_system("Combat breaks your stealth.")
        elif reason == "detected":
            self.ui_manager.log_error("You have been detected!")
        elif reason == "movement":
            self.ui_manager.log_system("Your movement breaks your stealth.")
        else:
            self.ui_manager.log_system("Your stealth is broken.")
    
    def check_stealth_movement(self, character, from_area=None, to_area=None) -> bool:
        """
        Check if stealthy movement is successful.
        
        Returns:
            True if movement remains stealthy
        """
        current_state = self.get_stealth_state(character)
        if current_state != StealthState.SNEAKING:
            return True  # Not trying to be stealthy
        
        # Calculate stealth movement check
        stealth_bonus = self._get_stealth_skill_bonus(character)
        stealth_penalty = self._get_stealth_penalty(character)
        
        base_chance = 80 + stealth_bonus - stealth_penalty
        
        # Roll for stealth success
        roll = random.randint(1, 100)
        if roll <= base_chance:
            return True  # Successful stealthy movement
        else:
            self.break_stealth(character, "movement")
            return False
    
    def _get_character_id(self, character) -> str:
        """Get unique identifier for character."""
        if hasattr(character, 'name'):
            return character.name
        return str(id(character))
    
    def _get_stealth_skill_bonus(self, character) -> int:
        """Calculate character's stealth skill bonus."""
        if not hasattr(character, 'character_class'):
            return 0
        
        char_class = character.character_class.lower()
        if char_class not in self.stealth_classes:
            return 0
        
        # Base class bonus
        class_bonus = self.stealth_classes[char_class]['skill_bonus']
        
        # DEX modifier
        dex_bonus = character.get_stat_modifier('dexterity') * 2 if hasattr(character, 'get_stat_modifier') else 0
        
        # Level bonus (small)
        level_bonus = getattr(character, 'level', 1) // 2
        
        return class_bonus + dex_bonus + level_bonus
    
    def _get_stealth_penalty(self, character) -> int:
        """Calculate stealth penalties from armor and encumbrance."""
        penalty = 0
        
        # Check for armor penalties
        if hasattr(character, 'equipment_system') and character.equipment_system:
            armor = character.equipment_system.get_equipped_armor()
            if armor and hasattr(armor, 'armor_type'):
                armor_type = armor.armor_type.lower()
                if 'heavy' in armor_type or 'plate' in armor_type:
                    penalty += 40
                elif 'medium' in armor_type or 'chain' in armor_type:
                    penalty += 20
                elif 'light' in armor_type or 'leather' in armor_type:
                    penalty += 5
        
        # TODO: Add encumbrance penalty based on carrying capacity
        
        return penalty
    
    def get_stealth_status_display(self, character) -> str:
        """Get display text for character's stealth status."""
        state = self.get_stealth_state(character)
        
        if state == StealthState.SNEAKING:
            return "[SNEAKING]"
        elif state == StealthState.HIDDEN:
            return "[HIDDEN]"
        elif state == StealthState.DETECTED:
            return "[DETECTED]"
        else:
            return ""


# Test function for stealth system
def _test_stealth_system():
    """Test stealth system functionality."""
    from .dice_system import DiceSystem
    
    class MockUIManager:
        def log_success(self, msg): print(f"SUCCESS: {msg}")
        def log_error(self, msg): print(f"ERROR: {msg}")
        def log_info(self, msg): print(f"INFO: {msg}")
        def log_system(self, msg): print(f"SYSTEM: {msg}")
    
    class MockCharacter:
        def __init__(self, char_class="rogue", level=5):
            self.name = "TestRogue"
            self.character_class = char_class
            self.level = level
            self.dexterity = 16
            
        def get_stat_modifier(self, stat):
            if stat == 'dexterity':
                return 3  # 16 DEX = +3 modifier
            return 0
    
    # Create test instances
    dice_system = DiceSystem(show_rolls=False)
    ui_manager = MockUIManager()
    stealth_system = StealthSystem(dice_system, ui_manager)
    
    rogue = MockCharacter("rogue", 5)
    warrior = MockCharacter("warrior", 5)
    
    # Test stealth abilities
    assert stealth_system.can_use_stealth(rogue)
    assert not stealth_system.can_use_stealth(warrior)
    
    # Test entering stealth mode
    assert stealth_system.enter_stealth_mode(rogue)
    assert stealth_system.get_stealth_state(rogue) == StealthState.SNEAKING
    
    # Test backstab multiplier
    success, multiplier = stealth_system.attempt_backstab(rogue, None)
    assert success
    assert multiplier >= 3  # Level 5 rogue should get 3x or 4x
    
    print("Stealth system tests passed!")


if __name__ == "__main__":
    _test_stealth_system()