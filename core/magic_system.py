"""
Core Magic System for Rogue City
Handles mana pools, spell learning, and magic mechanics for all spellcasting classes.
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class SpellSchool(Enum):
    """Magic spell schools with specific class associations"""
    MAGE = "mage"           # Arcane magic - Mage, Warlock, Necromancer
    PRIEST = "priest"       # Divine magic - Priest, Paladin  
    DRUID = "druid"         # Nature magic - Druid, Ranger


class MagicSystem:
    """
    Core magic system managing mana pools, spell access, and magical mechanics
    """
    
    def __init__(self):
        """Initialize the magic system"""
        # Class spell school mappings
        self.class_schools = {
            'mage': [SpellSchool.MAGE],
            'priest': [SpellSchool.PRIEST],
            'druid': [SpellSchool.DRUID],
            'warlock': [SpellSchool.MAGE],    # Combat-focused mage spells
            'necromancer': [SpellSchool.MAGE], # Death-focused mage spells
            'paladin': [SpellSchool.PRIEST],   # Limited divine spells
            'ranger': [SpellSchool.DRUID],     # Limited nature spells
            'bard': [SpellSchool.MAGE]         # Limited arcane spells
        }
        
        # Starting spells by class
        self.starting_spells = {
            'mage': ['magic_missile', 'light'],
            'priest': ['cure_light_wounds', 'bless'],
            'druid': ['goodberry', 'detect_snares'],
            'warlock': ['magic_missile'],
            'necromancer': ['magic_missile', 'detect_magic'],
            'paladin': ['cure_light_wounds'],
            'ranger': ['goodberry'],
            'bard': ['light']
        }
        
        # Mana calculation modifiers by class
        self.mana_modifiers = {
            'mage': 1.5,        # 50% bonus mana
            'priest': 1.25,     # 25% bonus mana
            'druid': 1.25,      # 25% bonus mana
            'warlock': 1.0,     # Standard mana
            'necromancer': 1.2, # 20% bonus mana
            'paladin': 0.75,    # 25% less mana
            'ranger': 0.5,      # 50% less mana
            'bard': 0.8         # 20% less mana
        }
        
    def is_spellcaster(self, character_class: str) -> bool:
        """Check if a class can cast spells"""
        return character_class.lower() in self.class_schools
        
    def get_spell_schools(self, character_class: str) -> List[SpellSchool]:
        """Get spell schools available to a class"""
        return self.class_schools.get(character_class.lower(), [])
        
    def calculate_max_mana(self, character) -> int:
        """Calculate maximum mana for a character"""
        if not self.is_spellcaster(character.character_class):
            return 0
            
        char_class = character.character_class.lower()
        
        # Base mana calculation: 6 + (INT modifier × level) + (WIS modifier × level/2)
        int_modifier = max(0, (character.stats['intelligence'] - 10) // 2)
        wis_modifier = max(0, (character.stats['wisdom'] - 10) // 2)
        level = max(1, character.level)
        
        base_mana = 6 + (int_modifier * level) + (wis_modifier * level // 2)
        
        # Apply class modifier
        class_modifier = self.mana_modifiers.get(char_class, 1.0)
        max_mana = int(base_mana * class_modifier)
        
        return max(1, max_mana)  # Minimum 1 mana
        
    def get_starting_spells(self, character_class: str) -> List[str]:
        """Get starting spells for a character class"""
        return self.starting_spells.get(character_class.lower(), [])
        
    def can_learn_spell(self, character, spell_name: str) -> Tuple[bool, str]:
        """Check if character can learn a specific spell"""
        if not self.is_spellcaster(character.character_class):
            return False, "You cannot cast spells"
            
        # Import spell system to check spell details
        try:
            from core.spell_system import SpellSystem
            spell_system = SpellSystem()
            spell_data = spell_system.get_spell_data(spell_name)
            
            if not spell_data:
                return False, f"Spell '{spell_name}' does not exist"
                
            # Check if spell school matches class schools
            spell_school = spell_data.get('school')
            class_schools = self.get_spell_schools(character.character_class)
            
            school_match = False
            for school in class_schools:
                if school.value == spell_school:
                    school_match = True
                    break
                    
            if not school_match:
                return False, f"Your class cannot learn {spell_school} spells"
                
            # Check level requirements
            spell_level = spell_data.get('level', 1)
            min_char_level = spell_level * 2 - 1  # Level 1 spells at level 1, level 2 at level 3, etc.
            
            if character.level < min_char_level:
                return False, f"You need to be level {min_char_level} to learn this spell"
                
            return True, "Spell can be learned"
            
        except ImportError:
            return False, "Spell system not available"
            
    def regenerate_mana(self, character, amount: int = None) -> int:
        """Regenerate mana for a character"""
        if not hasattr(character, 'current_mana') or not hasattr(character, 'max_mana'):
            return 0
            
        if character.current_mana >= character.max_mana:
            return 0
            
        if amount is None:
            # Base regeneration: 1 per minute + WIS modifier
            wis_modifier = (character.stats['wisdom'] - 10) // 2
            amount = max(1, 1 + wis_modifier)
            
        actual_regen = min(amount, character.max_mana - character.current_mana)
        character.current_mana += actual_regen
        return actual_regen
        
    def consume_mana(self, character, amount: int) -> bool:
        """Consume mana from character for spell casting"""
        if not hasattr(character, 'current_mana'):
            return False
            
        if character.current_mana < amount:
            return False
            
        character.current_mana -= amount
        return True
        
    def get_mana_status(self, character) -> str:
        """Get formatted mana status string"""
        if not hasattr(character, 'current_mana') or not hasattr(character, 'max_mana'):
            return "No mana"
            
        current = character.current_mana
        maximum = character.max_mana
        percentage = (current / maximum * 100) if maximum > 0 else 0
        
        return f"Mana: {current}/{maximum} ({percentage:.0f}%)"
        
    def meditate(self, character) -> Tuple[bool, str, int]:
        """Perform meditation to recover mana"""
        if not self.is_spellcaster(character.character_class):
            return False, "You don't know how to meditate", 0
            
        if character.current_mana >= character.max_mana:
            return False, "You are already at full mana", 0
            
        # Calculate meditation recovery
        base_recovery = 5
        wis_modifier = (character.stats['wisdom'] - 10) // 2
        
        # Class-specific meditation bonuses
        char_class = character.character_class.lower()
        if char_class == 'mage':
            class_bonus = 2  # Mages are better at mana recovery
        elif char_class in ['priest', 'druid']:
            class_bonus = 1  # Divine/nature casters get moderate bonus
        else:
            class_bonus = 0
            
        recovery_amount = base_recovery + wis_modifier + class_bonus
        
        # Use dice system for meditation check
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            meditation_roll = dice.roll("1d20") + wis_modifier
            
            if meditation_roll >= 12:  # DC 12 meditation check
                actual_recovery = self.regenerate_mana(character, recovery_amount)
                return True, f"You recover {actual_recovery} mana through meditation", actual_recovery
            else:
                return False, "You cannot focus your mind properly", 0
                
        except ImportError:
            # Fallback without dice system
            import random
            roll = random.randint(1, 20) + wis_modifier
            if roll >= 12:
                actual_recovery = self.regenerate_mana(character, recovery_amount)
                return True, f"You recover {actual_recovery} mana through meditation", actual_recovery
            else:
                return False, "You cannot focus your mind properly", 0