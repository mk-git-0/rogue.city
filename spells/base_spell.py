"""
Base Spell Class for Rogue City
Abstract base class for all spells with common mechanics.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class SpellTarget(Enum):
    """Spell targeting types"""
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    SINGLE_ALLY = "single_ally" 
    SINGLE_ANY = "single_any"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"
    AREA = "area"
    NONE = "none"


class SpellDuration(Enum):
    """Spell duration types"""
    INSTANT = "instant"
    ROUNDS = "rounds"
    MINUTES = "minutes"
    HOURS = "hours"
    PERMANENT = "permanent"


class BaseSpell(ABC):
    """
    Abstract base class for all spells
    """
    
    def __init__(self, name: str, level: int, school: str):
        """Initialize base spell properties"""
        self.name = name
        self.level = level
        self.school = school
        self.mana_cost = self._calculate_base_mana_cost()
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Spell description for players"""
        pass
        
    @property
    @abstractmethod
    def target_type(self) -> SpellTarget:
        """What this spell can target"""
        pass
        
    @property
    @abstractmethod
    def duration(self) -> SpellDuration:
        """How long spell effects last"""
        pass
        
    @property
    def duration_value(self) -> int:
        """Duration in appropriate units (rounds, minutes, etc.)"""
        return 0
        
    def _calculate_base_mana_cost(self) -> int:
        """Calculate base mana cost from spell level"""
        if self.level == 0:
            return 1  # Cantrips cost 1 mana
        elif self.level == 1:
            return 2
        elif self.level == 2:
            return 4
        elif self.level == 3:
            return 6
        else:
            return 4 + (self.level * 2)  # Higher level spells
            
    def get_mana_cost(self, caster) -> int:
        """Get actual mana cost for a specific caster"""
        base_cost = self.mana_cost
        
        # Class-specific mana efficiency
        if hasattr(caster, 'character_class'):
            char_class = caster.character_class.lower()
            if char_class == 'mage' and self.school == 'mage':
                # Mages cast mage spells more efficiently
                return max(1, int(base_cost * 0.85))
            elif char_class == 'priest' and self.school == 'priest':
                # Priests cast divine spells more efficiently
                return max(1, int(base_cost * 0.9))
            elif char_class == 'druid' and self.school == 'druid':
                # Druids cast nature spells more efficiently
                return max(1, int(base_cost * 0.9))
                
        return base_cost
        
    def can_cast(self, caster, target=None) -> Tuple[bool, str]:
        """Check if caster can cast this spell"""
        # Check mana
        mana_cost = self.get_mana_cost(caster)
        if hasattr(caster, 'current_mana') and caster.current_mana < mana_cost:
            return False, f"Insufficient mana (need {mana_cost}, have {caster.current_mana})"
            
        # Check target validity
        if self.target_type == SpellTarget.SINGLE_ENEMY and not target:
            return False, "You must target an enemy"
        elif self.target_type == SpellTarget.SINGLE_ALLY and not target:
            return False, "You must target an ally"
        elif self.target_type == SpellTarget.SINGLE_ANY and not target:
            return False, "You must specify a target"
            
        return True, "Can cast spell"
        
    @abstractmethod
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Cast the spell
        
        Returns:
            Tuple of (success, message, effects_data)
            effects_data contains information about spell effects for combat system
        """
        pass
        
    def get_spell_power_bonus(self, caster) -> int:
        """Calculate spell power bonus from caster's stats"""
        base_bonus = 0
        
        # Intelligence bonus for mage spells
        if self.school == 'mage' and hasattr(caster, 'stats'):
            int_modifier = (caster.stats.get('intelligence', 10) - 10) // 2
            base_bonus += max(0, int_modifier)
            
        # Wisdom bonus for divine/nature spells
        elif self.school in ['priest', 'druid'] and hasattr(caster, 'stats'):
            wis_modifier = (caster.stats.get('wisdom', 10) - 10) // 2
            base_bonus += max(0, wis_modifier)
            
        # Level bonus
        if hasattr(caster, 'level'):
            level_bonus = caster.level // 5  # +1 per 5 levels
            base_bonus += level_bonus
            
        return base_bonus
        
    def roll_damage(self, damage_dice: str, caster, dice_system=None) -> int:
        """Roll damage dice with spell power bonus"""
        if dice_system:
            base_damage = dice_system.roll(damage_dice)
        else:
            # Fallback damage calculation
            import random
            if 'd' in damage_dice:
                parts = damage_dice.split('d')
                if len(parts) == 2:
                    num_dice = int(parts[0]) if parts[0] else 1
                    die_size = int(parts[1].split('+')[0])
                    base_damage = sum(random.randint(1, die_size) for _ in range(num_dice))
                    if '+' in damage_dice:
                        bonus = int(damage_dice.split('+')[1])
                        base_damage += bonus
                else:
                    base_damage = 1
            else:
                base_damage = int(damage_dice) if damage_dice.isdigit() else 1
                
        # Add spell power bonus
        spell_power = self.get_spell_power_bonus(caster)
        return base_damage + spell_power
        
    def get_display_info(self) -> Dict[str, Any]:
        """Get spell information for display"""
        return {
            'name': self.name,
            'level': self.level,
            'school': self.school,
            'mana_cost': self.mana_cost,
            'description': self.description,
            'target_type': self.target_type.value,
            'duration': self.duration.value
        }