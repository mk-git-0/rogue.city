"""
Comprehensive MajorMUD Skill System for Rogue City
Manages all skill-based mechanics with D20-style checks and authentic MajorMUD progression.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class SkillType(Enum):
    """Core MajorMUD skills with stat dependencies."""
    # Stealth-based skills
    STEALTH = "stealth"
    HIDING = "hiding"
    
    # Thievery skills  
    LOCKPICKING = "lockpicking"
    THIEVERY = "thievery"
    PICKPOCKETING = "pickpocketing"
    
    # Detection skills
    TRAP_DETECTION = "trap_detection"
    TRAP_DISARMAMENT = "trap_disarmament"
    SEARCH = "search"
    PERCEPTION = "perception"
    LISTENING = "listening"
    
    # Movement skills
    TRACKING = "tracking"
    FORAGING = "foraging"
    CLIMBING = "climbing"
    SWIMMING = "swimming"
    
    # Combat skills
    DODGING = "dodging"
    BLOCKING = "blocking"
    PARRYING = "parrying"
    
    # Magic skills
    SPELL_CASTING = "spell_casting"
    MEDITATION = "meditation"


class SkillDifficulty(Enum):
    """D20-style skill check difficulties."""
    TRIVIAL = 5      # DC 5 - Very easy tasks
    EASY = 10        # DC 10 - Simple tasks
    MODERATE = 15    # DC 15 - Average difficulty
    HARD = 20        # DC 20 - Challenging tasks
    VERY_HARD = 25   # DC 25 - Expert level
    EXTREME = 30     # DC 30 - Master level
    LEGENDARY = 35   # DC 35 - Legendary difficulty


class SkillSystem:
    """
    Comprehensive MajorMUD skill system with D20-style checks and authentic progression.
    
    Features:
    - Stat-based skill calculations (Primary stat x3 + Secondary stat x1)
    - Class restrictions and bonuses
    - Practice-based improvement
    - Equipment bonuses
    - Environmental modifiers
    - Critical success/failure on natural 1/20
    """
    
    def __init__(self, dice_system, ui_manager):
        """Initialize the comprehensive skill system."""
        self.dice_system = dice_system
        self.ui_manager = ui_manager
        
        # Core skill definitions with primary and secondary stats
        self.skill_definitions = {
            SkillType.STEALTH: {'primary': 'dexterity', 'secondary': 'wisdom'},
            SkillType.HIDING: {'primary': 'dexterity', 'secondary': 'wisdom'},
            SkillType.THIEVERY: {'primary': 'dexterity', 'secondary': 'intelligence'},
            SkillType.LOCKPICKING: {'primary': 'dexterity', 'secondary': 'intelligence'},
            SkillType.PICKPOCKETING: {'primary': 'dexterity', 'secondary': 'intelligence'},
            SkillType.TRAP_DETECTION: {'primary': 'intelligence', 'secondary': 'wisdom'},
            SkillType.TRAP_DISARMAMENT: {'primary': 'intelligence', 'secondary': 'dexterity'},
            SkillType.SEARCH: {'primary': 'wisdom', 'secondary': 'intelligence'},
            SkillType.PERCEPTION: {'primary': 'wisdom', 'secondary': 'intelligence'},
            SkillType.LISTENING: {'primary': 'wisdom', 'secondary': 'dexterity'},
            SkillType.TRACKING: {'primary': 'wisdom', 'secondary': 'intelligence'},
            SkillType.FORAGING: {'primary': 'wisdom', 'secondary': 'intelligence'},
            SkillType.CLIMBING: {'primary': 'strength', 'secondary': 'dexterity'},
            SkillType.SWIMMING: {'primary': 'strength', 'secondary': 'constitution'},
            SkillType.DODGING: {'primary': 'dexterity', 'secondary': 'constitution'},
            SkillType.BLOCKING: {'primary': 'strength', 'secondary': 'dexterity'},
            SkillType.PARRYING: {'primary': 'dexterity', 'secondary': 'strength'},
            SkillType.SPELL_CASTING: {'primary': 'intelligence', 'secondary': 'wisdom'},
            SkillType.MEDITATION: {'primary': 'wisdom', 'secondary': 'constitution'}
        }
        
        # Class skill access and bonuses (which skills each class can learn)
        self.class_skill_access = {
            'thief': {
                SkillType.STEALTH: 8, SkillType.HIDING: 8,
                SkillType.THIEVERY: 10, SkillType.LOCKPICKING: 10, 
                SkillType.PICKPOCKETING: 12, SkillType.TRAP_DETECTION: 8,
                SkillType.TRAP_DISARMAMENT: 10, SkillType.SEARCH: 6,
                SkillType.PERCEPTION: 6, SkillType.LISTENING: 6,
                SkillType.CLIMBING: 8, SkillType.DODGING: 4
            },
            'rogue': {
                SkillType.STEALTH: 6, SkillType.HIDING: 6,
                SkillType.LOCKPICKING: 8, SkillType.PICKPOCKETING: 10,
                SkillType.TRAP_DETECTION: 6, SkillType.TRAP_DISARMAMENT: 8,
                SkillType.SEARCH: 8, SkillType.PERCEPTION: 8,
                SkillType.LISTENING: 8, SkillType.CLIMBING: 6,
                SkillType.DODGING: 6, SkillType.PARRYING: 4
            },
            'ninja': {
                SkillType.STEALTH: 10, SkillType.HIDING: 10,
                SkillType.LOCKPICKING: 6, SkillType.TRAP_DETECTION: 10,
                SkillType.TRAP_DISARMAMENT: 12, SkillType.CLIMBING: 12,
                SkillType.LISTENING: 10, SkillType.SEARCH: 8,
                SkillType.DODGING: 8, SkillType.MEDITATION: 6
            },
            'ranger': {
                SkillType.STEALTH: 4, SkillType.HIDING: 4,
                SkillType.TRACKING: 15, SkillType.SEARCH: 10,
                SkillType.FORAGING: 12, SkillType.CLIMBING: 8,
                SkillType.SWIMMING: 10, SkillType.LISTENING: 12,
                SkillType.PERCEPTION: 8, SkillType.DODGING: 4
            },
            'knight': {
                SkillType.BLOCKING: 8, SkillType.PARRYING: 6,
                SkillType.CLIMBING: 4, SkillType.SWIMMING: 4,
                SkillType.PERCEPTION: 4
            },
            'warrior': {
                SkillType.BLOCKING: 6, SkillType.PARRYING: 8,
                SkillType.CLIMBING: 6, SkillType.SWIMMING: 6,
                SkillType.PERCEPTION: 4, SkillType.DODGING: 4
            },
            'paladin': {
                SkillType.BLOCKING: 6, SkillType.PARRYING: 4,
                SkillType.SPELL_CASTING: 4, SkillType.MEDITATION: 6,
                SkillType.PERCEPTION: 6, SkillType.SEARCH: 4
            },
            'barbarian': {
                SkillType.CLIMBING: 8, SkillType.SWIMMING: 8,
                SkillType.TRACKING: 6, SkillType.FORAGING: 6,
                SkillType.LISTENING: 6, SkillType.PERCEPTION: 4
            },
            'mage': {
                SkillType.SPELL_CASTING: 12, SkillType.MEDITATION: 10,
                SkillType.SEARCH: 6, SkillType.PERCEPTION: 8
            },
            'priest': {
                SkillType.SPELL_CASTING: 10, SkillType.MEDITATION: 12,
                SkillType.PERCEPTION: 8, SkillType.SEARCH: 6
            },
            'mystic': {
                SkillType.MEDITATION: 10, SkillType.DODGING: 8,
                SkillType.PERCEPTION: 10, SkillType.CLIMBING: 6,
                SkillType.SWIMMING: 6
            },
            'spellsword': {
                SkillType.SPELL_CASTING: 8, SkillType.PARRYING: 6,
                SkillType.DODGING: 4, SkillType.PERCEPTION: 6
            },
            'necromancer': {
                SkillType.SPELL_CASTING: 12, SkillType.MEDITATION: 8,
                SkillType.SEARCH: 8, SkillType.PERCEPTION: 6
            },
            'warlock': {
                SkillType.SPELL_CASTING: 10, SkillType.MEDITATION: 6,
                SkillType.PARRYING: 4, SkillType.PERCEPTION: 6
            },
            'witchhunter': {
                SkillType.SEARCH: 10, SkillType.PERCEPTION: 12,
                SkillType.TRACKING: 8, SkillType.DODGING: 6,
                SkillType.PARRYING: 6
            }
        }
        
        # Track character skill experience (for practice-based improvement)
        self.skill_experience: Dict[str, Dict[SkillType, int]] = {}
        
        # Equipment that provides skill bonuses
        self.skill_tools = {
            'lockpicks': {SkillType.LOCKPICKING: 2},
            'masterwork lockpicks': {SkillType.LOCKPICKING: 5},
            'thieves tools': {SkillType.LOCKPICKING: 2, SkillType.TRAP_DISARMAMENT: 2},
            'masterwork thieves tools': {SkillType.LOCKPICKING: 5, SkillType.TRAP_DISARMAMENT: 5},
            'climbing gear': {SkillType.CLIMBING: 5},
            'rope': {SkillType.CLIMBING: 2},
            'magnifying glass': {SkillType.SEARCH: 2, SkillType.TRAP_DETECTION: 2},
            'spyglass': {SkillType.PERCEPTION: 3}
        }
    
    def can_use_skill(self, character, skill_type: SkillType) -> bool:
        """Check if character can attempt to use a skill."""
        if not hasattr(character, 'character_class'):
            return False
        
        char_class = character.character_class.lower()
        
        # Universal skills available to all classes (but with penalties if not trained)
        universal_skills = [SkillType.SEARCH, SkillType.PERCEPTION, SkillType.CLIMBING, 
                          SkillType.SWIMMING, SkillType.LISTENING]
        
        if skill_type in universal_skills:
            return True
        
        # Check if class has access to specific skill
        return (char_class in self.class_skill_access and 
                skill_type in self.class_skill_access[char_class])
    
    def make_skill_check(self, character, skill_type: SkillType, 
                        difficulty: SkillDifficulty = SkillDifficulty.MODERATE,
                        circumstance_bonus: int = 0) -> Tuple[bool, int, str]:
        """
        Make a comprehensive D20-style skill check.
        
        Args:
            character: Character attempting the skill
            skill_type: Type of skill being attempted
            difficulty: Difficulty class for the check
            circumstance_bonus: Situational bonus/penalty
            
        Returns:
            Tuple of (success, total_roll, result_description)
        """
        # Calculate skill bonus
        skill_bonus = self.get_skill_bonus(character, skill_type)
        
        # Roll d20
        roll = self.dice_system.roll_single_die(20)
        total = roll + skill_bonus + circumstance_bonus
        
        # Track skill usage for experience
        self._track_skill_usage(character, skill_type)
        
        # Check for critical success/failure
        if roll == 20:
            return True, total, "Critical Success!"
        elif roll == 1:
            return False, total, "Critical Failure!"
        
        # Standard success/failure
        success = total >= difficulty.value
        if success:
            if total >= difficulty.value + 10:
                return True, total, "Exceptional Success!"
            else:
                return True, total, "Success"
        else:
            return False, total, "Failure"
    
    def get_skill_bonus(self, character, skill_type: SkillType) -> int:
        """
        Calculate total skill bonus using MajorMUD formula:
        (Primary stat modifier × 3) + (Secondary stat modifier × 1) + Class bonus + Level bonus + Experience bonus + Equipment bonus
        """
        if skill_type not in self.skill_definitions:
            return 0
            
        total_bonus = 0
        skill_def = self.skill_definitions[skill_type]
        
        # Stat-based bonuses (Primary × 3 + Secondary × 1)
        if hasattr(character, 'get_stat_modifier'):
            primary_mod = character.get_stat_modifier(skill_def['primary'])
            secondary_mod = character.get_stat_modifier(skill_def['secondary'])
            total_bonus += (primary_mod * 3) + (secondary_mod * 1)
        
        # Class skill bonus
        if hasattr(character, 'character_class'):
            char_class = character.character_class.lower()
            if (char_class in self.class_skill_access and 
                skill_type in self.class_skill_access[char_class]):
                total_bonus += self.class_skill_access[char_class][skill_type]
        
        # Level bonus (small steady improvement)
        if hasattr(character, 'level'):
            total_bonus += character.level // 2  # +1 per 2 levels
        
        # Experience bonus from practice
        if hasattr(character, 'get_skill_experience'):
            experience = character.get_skill_experience(skill_type.value)
            # Experience bonus: +1 per 10 uses, max +5
            total_bonus += min(5, experience // 10)
        else:
            # Fallback to system tracking
            char_id = self._get_character_id(character)
            if (char_id in self.skill_experience and 
                skill_type in self.skill_experience[char_id]):
                experience = self.skill_experience[char_id][skill_type]
                total_bonus += min(5, experience // 10)
        
        # Equipment bonus
        total_bonus += self._get_equipment_bonus(character, skill_type)
        
        return total_bonus
    
    def _get_equipment_bonus(self, character, skill_type: SkillType) -> int:
        """Calculate bonus from equipment for a skill."""
        if not hasattr(character, 'inventory_system') or character.inventory_system is None:
            return 0
        
        bonus = 0
        
        # Check inventory for skill-enhancing tools
        if hasattr(character.inventory_system, 'items'):
            for item in character.inventory_system.items:
                item_name = item.name.lower()
                for tool_name, tool_bonuses in self.skill_tools.items():
                    if tool_name in item_name and skill_type in tool_bonuses:
                        bonus += tool_bonuses[skill_type]
                        break
        
        return bonus
    
    def _track_skill_usage(self, character, skill_type: SkillType) -> None:
        """Track skill usage for practice-based improvement."""
        # Use character's built-in tracking if available
        if hasattr(character, 'track_skill_usage'):
            character.track_skill_usage(skill_type.value)
        else:
            # Fallback to system tracking
            char_id = self._get_character_id(character)
            
            if char_id not in self.skill_experience:
                self.skill_experience[char_id] = {}
            
            if skill_type not in self.skill_experience[char_id]:
                self.skill_experience[char_id][skill_type] = 0
            
            self.skill_experience[char_id][skill_type] += 1
    
    def _get_character_id(self, character) -> str:
        """Get unique identifier for character."""
        if hasattr(character, 'name'):
            return character.name
        return str(id(character))
    
    # High-level skill attempt methods that use the new skill check system
    
    def attempt_lockpicking(self, character, target_name: str = "lock", 
                           difficulty: SkillDifficulty = SkillDifficulty.MODERATE) -> bool:
        """Attempt to pick a lock using the comprehensive skill system."""
        if not self.can_use_skill(character, SkillType.LOCKPICKING):
            self.ui_manager.log_error("You don't know how to pick locks.")
            return False
        
        self.ui_manager.log_info(f"You examine the {target_name} carefully...")
        
        # Make skill check using new system
        success, total_roll, result_desc = self.make_skill_check(
            character, SkillType.LOCKPICKING, difficulty)
        
        if success:
            if result_desc == "Critical Success!":
                self.ui_manager.log_success(f"The {target_name} clicks open instantly! Perfect technique!")
            elif result_desc == "Exceptional Success!":
                self.ui_manager.log_success(f"The {target_name} opens smoothly under your skilled touch.")
            else:
                self.ui_manager.log_success(f"The {target_name} clicks open quietly.")
            return True
        else:
            if result_desc == "Critical Failure!":
                self.ui_manager.log_error("You break your lockpick!")
                self._break_lockpicks(character)
            else:
                self.ui_manager.log_error(f"You cannot figure out this {target_name}.")
            return False
    
    def attempt_trap_detection(self, character, area=None) -> List[str]:
        """Attempt to detect traps using the new skill system."""
        self.ui_manager.log_info("You carefully examine the area for traps...")
        
        # Make perception/trap detection check
        success, total_roll, result_desc = self.make_skill_check(
            character, SkillType.TRAP_DETECTION, SkillDifficulty.MODERATE)
        
        detected_traps = []
        
        if success:
            # Simulate finding traps based on area (this would integrate with actual area trap data)
            if area and hasattr(area, 'traps'):
                for trap in area.traps:
                    detected_traps.append(trap['description'])
                    self.ui_manager.log_error(f"*** TRAP DETECTED: {trap['description']} ***")
            elif result_desc == "Critical Success!":
                self.ui_manager.log_success("You detect an extremely well-hidden pressure plate!")
                detected_traps.append("hidden pressure plate")
        
        if not detected_traps:
            self.ui_manager.log_info("You don't detect any traps here.")
        
        return detected_traps
    
    def attempt_search(self, character, area=None, target: str = None) -> List[str]:
        """Search for hidden items, examinables, or exits using the new skill system."""
        if target:
            self.ui_manager.log_info(f"You search the {target} carefully...")
        else:
            self.ui_manager.log_info("You carefully search the area...")
        
        # Make search check
        success, total_roll, result_desc = self.make_skill_check(
            character, SkillType.SEARCH, SkillDifficulty.MODERATE)
        
        found_items = []
        
        if success:
            # Reveal hidden exits in current room if present
            try:
                room = area.get_room(character.current_room)
            except Exception:
                room = None
            if room:
                hidden_revealed = []
                for dir_enum, exit_obj in room.exits.items():
                    if getattr(exit_obj, 'hidden', False):
                        # On non-critical success, reveal but keep it present; on crit, also unlock if previously locked
                        exit_obj.hidden = False
                        hidden_revealed.append(dir_enum.value)
                if hidden_revealed:
                    self.ui_manager.log_success(f"You discover a hidden passage: {', '.join(hidden_revealed)}.")
                    found_items.extend([f"hidden exit {d}" for d in hidden_revealed])
                    # Early return if we found hard content
                    return found_items

            # Flavor finds
            if result_desc == "Critical Success!":
                found = "You discover a secret compartment behind a loose stone!"
                found_items.append(found)
                self.ui_manager.log_success(found)
            elif result_desc == "Exceptional Success!":
                found = "You find a hidden lever concealed behind the tapestry!"
                found_items.append(found)
                self.ui_manager.log_success(found)
            else:
                self.ui_manager.log_info("Your search reveals nothing unusual.")
        else:
            self.ui_manager.log_info("You don't find anything unusual here.")
        
        return found_items
    
    def attempt_tracking(self, character, creature_name: str) -> bool:
        """Attempt to track a creature using the new skill system."""
        if not self.can_use_skill(character, SkillType.TRACKING):
            self.ui_manager.log_error("You don't know how to track creatures.")
            return False
        
        self.ui_manager.log_info(f"You search for signs of {creature_name}...")
        
        # Make tracking check
        success, total_roll, result_desc = self.make_skill_check(
            character, SkillType.TRACKING, SkillDifficulty.MODERATE)
        
        if success:
            direction = random.choice(['north', 'south', 'east', 'west'])
            if result_desc == "Critical Success!":
                self.ui_manager.log_success(f"You find very fresh tracks of a {creature_name} leading {direction}. They passed here recently!")
            else:
                self.ui_manager.log_success(f"You find tracks of a {creature_name} leading {direction}.")
            return True
        else:
            self.ui_manager.log_info(f"You cannot find any tracks of a {creature_name} here.")
            return False
    
    def attempt_pickpocketing(self, character, target_name: str) -> bool:
        """Attempt to pickpocket using the new skill system."""
        if not self.can_use_skill(character, SkillType.PICKPOCKETING):
            self.ui_manager.log_error("You don't know how to pickpocket.")
            return False
        
        # Pickpocketing is very difficult
        success, total_roll, result_desc = self.make_skill_check(
            character, SkillType.PICKPOCKETING, SkillDifficulty.HARD)
        
        if success:
            self.ui_manager.log_success(f"You successfully pickpocket something from {target_name}.")
            return True
        else:
            if result_desc == "Critical Failure!":
                self.ui_manager.log_critical(f"{target_name} notices your attempt!")
            else:
                self.ui_manager.log_info(f"You cannot find an opportunity to pickpocket {target_name}.")
            return False
    
    def _break_lockpicks(self, character) -> None:
        """Handle breaking lockpicks on critical failure."""
        if not hasattr(character, 'inventory_system'):
            return
        
        # Find and remove lockpicks
        for item in character.inventory_system.items:
            if 'lockpick' in item.name.lower():
                character.inventory_system.remove_item(item)
                break
    
    def get_skill_summary(self, character) -> Dict[str, int]:
        """Get summary of character's skill bonuses for display."""
        skills = {}
        
        for skill_type in SkillType:
            if self.can_use_skill(character, skill_type):
                bonus = self.get_skill_bonus(character, skill_type)
                if bonus > 0:
                    skills[skill_type.value] = bonus
        
        return skills
    
    def display_character_skills(self, character) -> None:
        """Display character's skills in a formatted way."""
        skills = self.get_skill_summary(character)
        
        if not skills:
            self.ui_manager.log_info("You have no trained skills.")
            return
        
        self.ui_manager.log_info("=== YOUR SKILLS ===")
        for skill_name, bonus in sorted(skills.items()):
            skill_display = skill_name.replace('_', ' ').title()
            self.ui_manager.log_info(f"{skill_display}: +{bonus}")


# Test function for skill system
def _test_skill_system():
    """Test the comprehensive skill system."""
    from .dice_system import DiceSystem
    
    class MockUIManager:
        def log_success(self, msg): print(f"SUCCESS: {msg}")
        def log_error(self, msg): print(f"ERROR: {msg}")
        def log_info(self, msg): print(f"INFO: {msg}")
        def log_critical(self, msg): print(f"CRITICAL: {msg}")
    
    class MockCharacter:
        def __init__(self, char_class="thief", level=5):
            self.name = "TestThief"
            self.character_class = char_class
            self.level = level
            self.dexterity = 16
            self.intelligence = 14
            self.wisdom = 12
            
        def get_stat_modifier(self, stat):
            if stat == 'dexterity':
                return 3
            elif stat == 'intelligence':
                return 2
            elif stat == 'wisdom':
                return 1
            return 0
    
    # Create test instances
    dice_system = DiceSystem(show_rolls=False)
    ui_manager = MockUIManager()
    skill_system = SkillSystem(dice_system, ui_manager)
    
    thief = MockCharacter("thief", 5)
    warrior = MockCharacter("warrior", 5)
    
    # Test skill abilities
    assert skill_system.can_use_skill(thief, SkillType.LOCKPICKING)
    assert not skill_system.can_use_skill(warrior, SkillType.LOCKPICKING)
    assert skill_system.can_use_skill(warrior, SkillType.SEARCH)  # Universal skill
    
    # Test skill bonus calculation
    lockpick_bonus = skill_system.get_skill_bonus(thief, SkillType.LOCKPICKING)
    assert lockpick_bonus > 0
    
    # Test skill check
    success, total, desc = skill_system.make_skill_check(thief, SkillType.LOCKPICKING)
    assert isinstance(success, bool)
    assert isinstance(total, int)
    assert isinstance(desc, str)
    
    print("Comprehensive skill system tests passed!")


if __name__ == "__main__":
    _test_skill_system()