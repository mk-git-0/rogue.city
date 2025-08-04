"""
Druid Spells for Rogue City
Nature magic spells for Druid and Ranger classes.
"""

from typing import Dict, List, Optional, Any, Tuple
from .base_spell import BaseSpell, SpellTarget, SpellDuration


class Goodberry(BaseSpell):
    """Goodberry - Create food that heals 1 HP"""
    
    def __init__(self):
        super().__init__("Goodberry", 1, "druid")
        
    @property
    def description(self) -> str:
        return "Creates magical berries that provide nourishment and minor healing"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.NONE
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.HOURS
        
    @property
    def duration_value(self) -> int:
        return 24  # 24 hours
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Goodberry"""
        # Calculate number of berries created
        caster_level = getattr(caster, 'level', 1)
        num_berries = min(10, 2 + caster_level)  # 2-10 berries based on level
        
        message = f"You cause {num_berries} small berries to appear. Each berry provides nourishment and heals 1 hit point when eaten."
        
        effects_data = {
            'type': 'create_item',
            'item_type': 'goodberry',
            'quantity': num_berries,
            'healing_per_berry': 1,
            'duration': 24 * 60,  # 24 hours in minutes
            'caster': caster
        }
        
        return True, message, effects_data


class CurePoison(BaseSpell):
    """Cure Poison - Remove poison effects"""
    
    def __init__(self):
        super().__init__("Cure Poison", 2, "druid")
        
    @property
    def description(self) -> str:
        return "Neutralizes poison in the target's system"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ALLY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Cure Poison"""
        if not target:
            target = caster  # Default to self if no target
            
        if target == caster:
            target_name = "yourself"
        else:
            target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
            
        message = f"Natural energy flows through {target_name}, neutralizing all poisons."
        
        effects_data = {
            'type': 'cure_poison',
            'target': target
        }
        
        return True, message, effects_data


class Barkskin(BaseSpell):
    """Barkskin - +2 natural AC bonus"""
    
    def __init__(self):
        super().__init__("Barkskin", 2, "druid")
        
    @property
    def description(self) -> str:
        return "The target's skin becomes tough and bark-like, providing natural armor"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ALLY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.HOURS
        
    @property
    def duration_value(self) -> int:
        return 1  # 1 hour
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Barkskin"""
        if not target:
            target = caster  # Default to self if no target
            
        if target == caster:
            target_name = "Your"
        else:
            target_name = target.get('name', 'The target') if isinstance(target, dict) else getattr(target, 'name', 'The target')
            
        message = f"{target_name} skin becomes rough and bark-like, providing natural protection."
        
        effects_data = {
            'type': 'buff',
            'effect': 'barkskin',
            'ac_bonus': 2,
            'duration': 60,  # 1 hour in minutes
            'target': target
        }
        
        return True, message, effects_data


class CallLightning(BaseSpell):
    """Call Lightning - 3d6 electric damage outdoors"""
    
    def __init__(self):
        super().__init__("Call Lightning", 3, "druid")
        
    @property
    def description(self) -> str:
        return "Calls down a bolt of lightning from the sky (more powerful outdoors)"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ENEMY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Call Lightning"""
        if not target:
            return False, "You must target an enemy", {}
            
        # Calculate damage (more powerful outdoors)
        is_outdoors = True  # TODO: Check if caster is outdoors
        if is_outdoors:
            damage = self.roll_damage("3d6", caster)
            outdoor_bonus = " The outdoor setting amplifies the spell's power!"
        else:
            damage = self.roll_damage("2d6", caster)
            outdoor_bonus = ""
            
        target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
        
        message = f"You call down a bolt of lightning that strikes {target_name} for {damage} electric damage!{outdoor_bonus}"
        
        effects_data = {
            'type': 'damage',
            'damage': damage,
            'damage_type': 'electric',
            'target': target,
            'natural_spell': True
        }
        
        return True, message, effects_data


class PlantGrowth(BaseSpell):
    """Plant Growth - Entangle enemies with vines"""
    
    def __init__(self):
        super().__init__("Plant Growth", 3, "druid")
        
    @property
    def description(self) -> str:
        return "Causes plants to grow rapidly and entangle enemies in the area"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.AREA
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.MINUTES
        
    @property
    def duration_value(self) -> int:
        return 10  # 10 minutes
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Plant Growth"""
        message = "Vines and plants suddenly sprout from the ground, grasping at nearby enemies!"
        
        # Calculate entangle DC
        caster_level = getattr(caster, 'level', 1)
        spell_power = self.get_spell_power_bonus(caster)
        entangle_dc = 10 + caster_level + spell_power
        
        effects_data = {
            'type': 'area_effect',
            'effect': 'entangle',
            'save_type': 'dexterity',
            'save_dc': entangle_dc,
            'duration': 10,  # 10 minutes
            'area': 'all_enemies'
        }
        
        return True, message, effects_data


class SpeakWithAnimals(BaseSpell):
    """Speak with Animals - Communicate with creatures"""
    
    def __init__(self):
        super().__init__("Speak with Animals", 1, "druid")
        
    @property
    def description(self) -> str:
        return "Allows communication with natural animals and beasts"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.NONE
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.MINUTES
        
    @property
    def duration_value(self) -> int:
        return 30  # 30 minutes
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Speak with Animals"""
        message = "You gain the ability to communicate with natural animals and beasts."
        
        effects_data = {
            'type': 'utility',
            'effect': 'speak_with_animals',
            'duration': 30,  # 30 minutes
            'caster': caster
        }
        
        return True, message, effects_data


# List of all druid spells for registration
DRUID_SPELLS = [
    Goodberry,
    CurePoison,
    Barkskin,
    CallLightning,
    PlantGrowth,
    SpeakWithAnimals
]