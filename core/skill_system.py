"""
Skill System for Rogue City
Manages skill-based commands like lockpicking, trap detection, searching, and tracking.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class SkillType(Enum):
    """Types of skills available."""
    LOCKPICKING = "lockpicking"
    TRAP_DETECTION = "trap_detection"
    TRAP_DISARMAMENT = "trap_disarmament"
    SEARCH = "search"
    TRACKING = "tracking"
    PICKPOCKETING = "pickpocketing"
    CLIMBING = "climbing"
    SWIMMING = "swimming"
    LISTENING = "listening"
    FORAGING = "foraging"


class DifficultyLevel(Enum):
    """Difficulty levels for skill checks."""
    TRIVIAL = 10
    EASY = 25
    MODERATE = 50
    HARD = 75
    EXTREME = 90
    LEGENDARY = 95


class SkillSystem:
    """
    Manages skill checks and skill-based interactions for various character classes.
    """
    
    def __init__(self, dice_system, ui_manager):
        """Initialize the skill system."""
        self.dice_system = dice_system
        self.ui_manager = ui_manager
        
        # Class skill bonuses - which classes get bonuses to which skills
        self.class_skills = {
            'thief': {
                SkillType.LOCKPICKING: 10,
                SkillType.TRAP_DETECTION: 8,
                SkillType.TRAP_DISARMAMENT: 10,
                SkillType.PICKPOCKETING: 12,
                SkillType.SEARCH: 6,
                SkillType.CLIMBING: 8,
                SkillType.LISTENING: 6
            },
            'rogue': {
                SkillType.LOCKPICKING: 8,
                SkillType.TRAP_DETECTION: 6,
                SkillType.TRAP_DISARMAMENT: 8,
                SkillType.PICKPOCKETING: 10,
                SkillType.SEARCH: 8,
                SkillType.CLIMBING: 6,
                SkillType.LISTENING: 8
            },
            'ninja': {
                SkillType.LOCKPICKING: 6,
                SkillType.TRAP_DETECTION: 10,
                SkillType.TRAP_DISARMAMENT: 12,
                SkillType.CLIMBING: 12,
                SkillType.LISTENING: 10,
                SkillType.SEARCH: 8
            },
            'ranger': {
                SkillType.TRACKING: 15,
                SkillType.SEARCH: 10,
                SkillType.FORAGING: 12,
                SkillType.CLIMBING: 8,
                SkillType.SWIMMING: 10,
                SkillType.LISTENING: 12
            },
            'bard': {
                SkillType.LOCKPICKING: 4,
                SkillType.PICKPOCKETING: 6,
                SkillType.SEARCH: 8,
                SkillType.LISTENING: 8
            },
            'gypsy': {
                SkillType.LOCKPICKING: 6,
                SkillType.PICKPOCKETING: 8,
                SkillType.SEARCH: 6,
                SkillType.LISTENING: 6
            }
        }
        
        # Track character skill attempts (for learning/improvement)
        self.skill_attempts: Dict[str, Dict[SkillType, int]] = {}
        
        # Special items that provide skill bonuses
        self.skill_tools = {
            'lockpicks': {SkillType.LOCKPICKING: 10},
            'thieves tools': {SkillType.LOCKPICKING: 10, SkillType.TRAP_DISARMAMENT: 10},
            'climbing gear': {SkillType.CLIMBING: 15},
            'rope': {SkillType.CLIMBING: 5}
        }
    
    def can_use_skill(self, character, skill_type: SkillType) -> bool:
        """Check if character can attempt to use a skill."""
        if not hasattr(character, 'character_class'):
            return False
        
        char_class = character.character_class.lower()
        
        # Some skills available to all classes at reduced effectiveness
        universal_skills = [SkillType.SEARCH, SkillType.CLIMBING, SkillType.SWIMMING, SkillType.LISTENING]
        
        if skill_type in universal_skills:
            return True
        
        # Check if class has skill
        return char_class in self.class_skills and skill_type in self.class_skills[char_class]
    
    def attempt_lockpicking(self, character, target_name: str = "lock", difficulty: DifficultyLevel = DifficultyLevel.MODERATE) -> bool:
        """
        Attempt to pick a lock.
        
        Returns:
            True if lockpicking was successful
        """
        if not self.can_use_skill(character, SkillType.LOCKPICKING):
            self.ui_manager.log_error("You don't know how to pick locks.")
            return False
        
        self.ui_manager.log_info(f"You examine the {target_name} carefully...")
        
        # Calculate skill bonus
        skill_bonus = self._get_skill_bonus(character, SkillType.LOCKPICKING)
        tool_bonus = self._get_tool_bonus(character, SkillType.LOCKPICKING)
        
        # Make skill check
        success_chance = max(5, skill_bonus + tool_bonus - difficulty.value)
        roll = random.randint(1, 100)
        
        # Track attempt for experience
        self._track_skill_attempt(character, SkillType.LOCKPICKING)
        
        if roll <= success_chance:
            self.ui_manager.log_success(f"The {target_name} clicks open quietly.")
            return True
        elif roll >= 95:  # Critical failure
            self.ui_manager.log_error("You break your lockpick!")
            self._break_lockpicks(character)
            return False
        else:
            self.ui_manager.log_error(f"You cannot figure out this {target_name}.")
            return False
    
    def attempt_trap_detection(self, character, area=None) -> List[str]:
        """
        Attempt to detect traps in the area.
        
        Returns:
            List of detected trap descriptions
        """
        if not self.can_use_skill(character, SkillType.TRAP_DETECTION):
            # Anyone can try to detect obvious traps, but with penalties
            skill_bonus = -20
        else:
            skill_bonus = self._get_skill_bonus(character, SkillType.TRAP_DETECTION)
        
        self.ui_manager.log_info("You carefully examine the area for traps...")
        
        detected_traps = []
        
        # Check for traps (this would be expanded with actual trap data)
        # For now, simulate trap detection
        if area and hasattr(area, 'traps'):
            for trap in area.traps:
                detection_chance = max(10, 60 + skill_bonus - trap.get('concealment', 50))
                roll = random.randint(1, 100)
                
                if roll <= detection_chance:
                    detected_traps.append(trap['description'])
                    self.ui_manager.log_error(f"*** TRAP DETECTED: {trap['description']} ***")
        
        # Track attempt
        self._track_skill_attempt(character, SkillType.TRAP_DETECTION)
        
        if not detected_traps:
            self.ui_manager.log_info("You don't detect any traps here.")
        
        return detected_traps
    
    def attempt_trap_disarmament(self, character, trap_name: str) -> bool:
        """
        Attempt to disarm a detected trap.
        
        Returns:
            True if trap was successfully disarmed
        """
        if not self.can_use_skill(character, SkillType.TRAP_DISARMAMENT):
            self.ui_manager.log_error("You don't know how to safely disarm traps.")
            return False
        
        self.ui_manager.log_info(f"You carefully work on disarming the {trap_name}...")
        
        # Calculate skill bonus
        skill_bonus = self._get_skill_bonus(character, SkillType.TRAP_DISARMAMENT)
        tool_bonus = self._get_tool_bonus(character, SkillType.TRAP_DISARMAMENT)
        
        # Make skill check (traps are generally harder than locks)
        base_difficulty = 70  # Base trap difficulty
        success_chance = max(5, skill_bonus + tool_bonus - base_difficulty)
        roll = random.randint(1, 100)
        
        # Track attempt
        self._track_skill_attempt(character, SkillType.TRAP_DISARMAMENT)
        
        if roll <= success_chance:
            self.ui_manager.log_success(f"You successfully disarm the {trap_name}.")
            return True
        elif roll >= 90:  # Critical failure - trigger trap
            self.ui_manager.log_critical(f"You accidentally trigger the {trap_name}!")
            # TODO: Apply trap effects to character
            return False
        else:
            self.ui_manager.log_error(f"You cannot figure out how to safely disarm the {trap_name}.")
            return False
    
    def attempt_search(self, character, area=None, target: str = None) -> List[str]:
        """
        Search for hidden items, doors, or secrets.
        
        Returns:
            List of found items/secrets
        """
        search_bonus = self._get_skill_bonus(character, SkillType.SEARCH)
        
        if target:
            self.ui_manager.log_info(f"You search the {target} carefully...")
        else:
            self.ui_manager.log_info("You carefully search the area...")
        
        found_items = []
        
        # Make search check
        base_chance = 40 + search_bonus
        roll = random.randint(1, 100)
        
        # Track attempt
        self._track_skill_attempt(character, SkillType.SEARCH)
        
        if roll <= base_chance:
            # Simulate finding things (this would be expanded with actual hidden content)
            possible_finds = [
                "You find a hidden lever behind the tapestry!",
                "You notice loose stones that might conceal something.",
                "You discover a small cache of coins hidden in the wall.",
                "You find a secret compartment in the floor.",
                "You notice suspicious scratches on the wall.",
                "You discover a hidden passage behind the bookshelf!"
            ]
            
            if random.randint(1, 100) <= 30:  # 30% chance to find something
                found = random.choice(possible_finds)
                found_items.append(found)
                self.ui_manager.log_success(found)
            else:
                self.ui_manager.log_info("Your search reveals nothing unusual.")
        else:
            self.ui_manager.log_info("You don't find anything unusual here.")
        
        return found_items
    
    def attempt_tracking(self, character, creature_name: str) -> bool:
        """
        Attempt to track a specific creature.
        
        Returns:
            True if tracks were found
        """
        if not self.can_use_skill(character, SkillType.TRACKING):
            self.ui_manager.log_error("You don't know how to track creatures.")
            return False
        
        self.ui_manager.log_info(f"You search for signs of {creature_name}...")
        
        # Calculate tracking bonus
        tracking_bonus = self._get_skill_bonus(character, SkillType.TRACKING)
        wisdom_bonus = character.get_stat_modifier('wisdom') * 2 if hasattr(character, 'get_stat_modifier') else 0
        
        # Make tracking check
        base_chance = 50 + tracking_bonus + wisdom_bonus
        roll = random.randint(1, 100)
        
        # Track attempt
        self._track_skill_attempt(character, SkillType.TRACKING)
        
        if roll <= base_chance:
            direction = random.choice(['north', 'south', 'east', 'west'])
            self.ui_manager.log_success(f"You find fresh tracks of a {creature_name} leading {direction}.")
            return True
        else:
            self.ui_manager.log_info(f"You cannot find any tracks of a {creature_name} here.")
            return False
    
    def attempt_pickpocketing(self, character, target_name: str) -> bool:
        """
        Attempt to pickpocket from an NPC.
        
        Returns:
            True if pickpocketing was successful
        """
        if not self.can_use_skill(character, SkillType.PICKPOCKETING):
            self.ui_manager.log_error("You don't know how to pickpocket.")
            return False
        
        # Calculate pickpocket bonus
        skill_bonus = self._get_skill_bonus(character, SkillType.PICKPOCKETING)
        dex_bonus = character.get_stat_modifier('dexterity') * 3 if hasattr(character, 'get_stat_modifier') else 0
        
        # Make pickpocket check (very difficult)
        base_chance = 30 + skill_bonus + dex_bonus
        roll = random.randint(1, 100)
        
        # Track attempt
        self._track_skill_attempt(character, SkillType.PICKPOCKETING)
        
        if roll <= base_chance:
            self.ui_manager.log_success(f"You successfully pickpocket something from {target_name}.")
            return True
        elif roll >= 85:  # High chance of getting caught
            self.ui_manager.log_critical(f"{target_name} notices your attempt!")
            return False
        else:
            self.ui_manager.log_info(f"You cannot find an opportunity to pickpocket {target_name}.")
            return False
    
    def attempt_listening(self, character, area=None) -> List[str]:
        """
        Listen for sounds and movements.
        
        Returns:
            List of heard sounds/information
        """
        listening_bonus = self._get_skill_bonus(character, SkillType.LISTENING)
        wisdom_bonus = character.get_stat_modifier('wisdom') * 2 if hasattr(character, 'get_stat_modifier') else 0
        
        self.ui_manager.log_info("You listen carefully...")
        
        # Make listening check
        base_chance = 60 + listening_bonus + wisdom_bonus
        roll = random.randint(1, 100)
        
        # Track attempt
        self._track_skill_attempt(character, SkillType.LISTENING)
        
        heard_sounds = []
        
        if roll <= base_chance:
            # Simulate hearing things
            possible_sounds = [
                "You hear footsteps echoing from the north.",
                "You detect the sound of running water nearby.",
                "You hear faint voices coming from beyond the wall.",
                "You notice the subtle sound of metal scraping stone.",
                "You hear the distant sound of combat.",
                "You detect heavy breathing coming from the shadows."
            ]
            
            if random.randint(1, 100) <= 40:  # 40% chance to hear something
                sound = random.choice(possible_sounds)
                heard_sounds.append(sound)
                self.ui_manager.log_success(sound)
            else:
                self.ui_manager.log_info("You hear only normal ambient sounds.")
        else:
            self.ui_manager.log_info("You don't hear anything unusual.")
        
        return heard_sounds
    
    def _get_skill_bonus(self, character, skill_type: SkillType) -> int:
        """Calculate character's bonus for a specific skill."""
        total_bonus = 0
        
        # Class skill bonus
        if hasattr(character, 'character_class'):
            char_class = character.character_class.lower()
            if char_class in self.class_skills and skill_type in self.class_skills[char_class]:
                total_bonus += self.class_skills[char_class][skill_type]
        
        # Attribute bonuses based on skill type
        if hasattr(character, 'get_stat_modifier'):
            if skill_type in [SkillType.LOCKPICKING, SkillType.TRAP_DISARMAMENT, SkillType.PICKPOCKETING]:
                total_bonus += character.get_stat_modifier('dexterity') * 2
            elif skill_type in [SkillType.SEARCH, SkillType.TRAP_DETECTION]:
                total_bonus += character.get_stat_modifier('intelligence') * 2
            elif skill_type in [SkillType.TRACKING, SkillType.LISTENING]:
                total_bonus += character.get_stat_modifier('wisdom') * 2
            elif skill_type in [SkillType.CLIMBING, SkillType.SWIMMING]:
                total_bonus += character.get_stat_modifier('strength') + character.get_stat_modifier('dexterity')
        
        # Level bonus (small)
        if hasattr(character, 'level'):
            total_bonus += character.level // 3
        
        # Experience bonus (characters get better with practice)
        char_id = self._get_character_id(character)
        if char_id in self.skill_attempts and skill_type in self.skill_attempts[char_id]:
            attempts = self.skill_attempts[char_id][skill_type]
            experience_bonus = min(10, attempts // 5)  # +1 bonus per 5 attempts, max +10
            total_bonus += experience_bonus
        
        return total_bonus
    
    def _get_tool_bonus(self, character, skill_type: SkillType) -> int:
        """Calculate bonus from tools/equipment for a skill."""
        if not hasattr(character, 'inventory_system'):
            return 0
        
        bonus = 0
        
        # Check inventory for useful tools
        for item in character.inventory_system.items:
            item_name = item.name.lower()
            for tool_name, tool_bonuses in self.skill_tools.items():
                if tool_name in item_name and skill_type in tool_bonuses:
                    bonus += tool_bonuses[skill_type]
                    break
        
        return bonus
    
    def _track_skill_attempt(self, character, skill_type: SkillType) -> None:
        """Track skill attempts for experience/learning."""
        char_id = self._get_character_id(character)
        
        if char_id not in self.skill_attempts:
            self.skill_attempts[char_id] = {}
        
        if skill_type not in self.skill_attempts[char_id]:
            self.skill_attempts[char_id][skill_type] = 0
        
        self.skill_attempts[char_id][skill_type] += 1
    
    def _break_lockpicks(self, character) -> None:
        """Handle breaking lockpicks on critical failure."""
        if not hasattr(character, 'inventory_system'):
            return
        
        # Find and remove lockpicks
        for item in character.inventory_system.items:
            if 'lockpick' in item.name.lower():
                character.inventory_system.remove_item(item)
                break
    
    def _get_character_id(self, character) -> str:
        """Get unique identifier for character."""
        if hasattr(character, 'name'):
            return character.name
        return str(id(character))
    
    def get_skill_summary(self, character) -> Dict[str, int]:
        """Get summary of character's skill bonuses."""
        skills = {}
        
        for skill_type in SkillType:
            if self.can_use_skill(character, skill_type):
                bonus = self._get_skill_bonus(character, skill_type)
                if bonus > 0:
                    skills[skill_type.value] = bonus
        
        return skills


# Test function for skill system
def _test_skill_system():
    """Test skill system functionality."""
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
    lockpick_bonus = skill_system._get_skill_bonus(thief, SkillType.LOCKPICKING)
    assert lockpick_bonus > 0
    
    print("Skill system tests passed!")


if __name__ == "__main__":
    _test_skill_system()