"""
Priest Spells for Rogue City  
Divine magic spells for Priest and Paladin classes.
"""

from typing import Dict, List, Optional, Any, Tuple
from .base_spell import BaseSpell, SpellTarget, SpellDuration


class CureLightWounds(BaseSpell):
    """Cure Light Wounds - Heal 1d8+1 HP"""
    
    def __init__(self):
        super().__init__("Cure Light Wounds", 1, "priest")
        
    @property
    def description(self) -> str:
        return "Channels divine energy to heal minor wounds"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ALLY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Cure Light Wounds"""
        if not target:
            target = caster  # Default to self if no target
            
        # Calculate healing
        healing = self.roll_damage("1d8+1", caster)
        
        if target == caster:
            target_name = "yourself"
        else:
            target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
            
        message = f"Divine energy flows into {target_name}, healing {healing} hit points."
        
        effects_data = {
            'type': 'healing',
            'healing': healing,
            'target': target
        }
        
        return True, message, effects_data


class CureSeriousWounds(BaseSpell):
    """Cure Serious Wounds - Heal 2d8+2 HP"""
    
    def __init__(self):
        super().__init__("Cure Serious Wounds", 2, "priest")
        
    @property
    def description(self) -> str:
        return "Channels powerful divine energy to heal moderate wounds"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ALLY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Cure Serious Wounds"""
        if not target:
            target = caster  # Default to self if no target
            
        # Calculate healing
        healing = self.roll_damage("2d8+2", caster)
        
        if target == caster:
            target_name = "yourself"
        else:
            target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
            
        message = f"Brilliant divine energy flows into {target_name}, healing {healing} hit points."
        
        effects_data = {
            'type': 'healing',
            'healing': healing,
            'target': target
        }
        
        return True, message, effects_data


class Heal(BaseSpell):
    """Heal - Full HP restoration"""
    
    def __init__(self):
        super().__init__("Heal", 6, "priest")
        
    @property
    def description(self) -> str:
        return "Channels overwhelming divine power to completely heal all wounds"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ALLY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Heal"""
        if not target:
            target = caster  # Default to self if no target
            
        if target == caster:
            target_name = "yourself"
        else:
            target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
            
        message = f"Radiant divine energy completely restores {target_name} to full health."
        
        effects_data = {
            'type': 'healing',
            'healing': 'full',  # Special indicator for full healing
            'target': target
        }
        
        return True, message, effects_data


class Bless(BaseSpell):
    """Bless - +1 attack/damage for 10 minutes"""
    
    def __init__(self):
        super().__init__("Bless", 1, "priest")
        
    @property
    def description(self) -> str:
        return "Calls upon divine favor to enhance combat abilities"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ALLY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.MINUTES
        
    @property
    def duration_value(self) -> int:
        return 10  # 10 minutes
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Bless"""
        if not target:
            target = caster  # Default to self if no target
            
        if target == caster:
            target_name = "You"
        else:
            target_name = target.get('name', 'The target') if isinstance(target, dict) else getattr(target, 'name', 'The target')
            
        message = f"{target_name} glow{'s' if target != caster else ''} with divine favor."
        
        effects_data = {
            'type': 'buff',
            'effect': 'bless',
            'attack_bonus': 1,
            'damage_bonus': 1,
            'duration': 10,  # 10 minutes
            'target': target
        }
        
        return True, message, effects_data


class Sanctuary(BaseSpell):
    """Sanctuary - Protection from attacks"""
    
    def __init__(self):
        super().__init__("Sanctuary", 1, "priest")
        
    @property
    def description(self) -> str:
        return "Surrounds the target with divine protection that deters attacks"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ALLY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.MINUTES
        
    @property
    def duration_value(self) -> int:
        return 5  # 5 minutes
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Sanctuary"""
        if not target:
            target = caster  # Default to self if no target
            
        if target == caster:
            target_name = "You"
        else:
            target_name = target.get('name', 'The target') if isinstance(target, dict) else getattr(target, 'name', 'The target')
            
        message = f"{target_name} become{'s' if target != caster else ''} surrounded by a peaceful divine aura."
        
        effects_data = {
            'type': 'buff',
            'effect': 'sanctuary',
            'protection': True,
            'duration': 5,  # 5 minutes
            'target': target
        }
        
        return True, message, effects_data


class TurnUndead(BaseSpell):
    """Turn Undead - Repel/destroy undead creatures"""
    
    def __init__(self):
        super().__init__("Turn Undead", 2, "priest")
        
    @property
    def description(self) -> str:
        return "Channels divine power to repel or destroy undead creatures"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.ALL_ENEMIES
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Turn Undead"""
        # Calculate turning power
        caster_level = getattr(caster, 'level', 1)
        spell_power = self.get_spell_power_bonus(caster)
        turning_dc = 10 + caster_level + spell_power
        
        message = "You raise your holy symbol and channel divine power against the undead!"
        
        effects_data = {
            'type': 'turn_undead',
            'turning_dc': turning_dc,
            'caster_level': caster_level,
            'target': 'all_undead'
        }
        
        return True, message, effects_data


class SpiritualHammer(BaseSpell):
    """Spiritual Hammer - Magical weapon attack"""
    
    def __init__(self):
        super().__init__("Spiritual Hammer", 2, "priest")
        
    @property
    def description(self) -> str:
        return "Creates a spectral hammer that strikes enemies with divine force"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ENEMY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Spiritual Hammer"""
        if not target:
            return False, "You must target an enemy", {}
            
        # Calculate damage
        base_damage = self.roll_damage("1d8", caster)
        
        target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
        
        message = f"A spectral hammer materializes and strikes {target_name} for {base_damage} divine damage!"
        
        effects_data = {
            'type': 'damage',
            'damage': base_damage,
            'damage_type': 'divine',
            'target': target,
            'magical_weapon': True
        }
        
        return True, message, effects_data


# List of all priest spells for registration
PRIEST_SPELLS = [
    CureLightWounds,
    CureSeriousWounds,
    Heal,
    Bless,
    Sanctuary,
    TurnUndead,
    SpiritualHammer
]