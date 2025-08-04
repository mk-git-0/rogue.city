"""
Mage Spells for Rogue City
Arcane magic spells for Mage, Warlock, and Necromancer classes.
"""

from typing import Dict, List, Optional, Any, Tuple
from .base_spell import BaseSpell, SpellTarget, SpellDuration


class MagicMissile(BaseSpell):
    """Magic Missile - 1d4+1 auto-hit force damage"""
    
    def __init__(self):
        super().__init__("Magic Missile", 1, "mage")
        
    @property
    def description(self) -> str:
        return "Launches unerring darts of magical force that automatically hit their target"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ENEMY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Magic Missile"""
        if not target:
            return False, "You must target an enemy", {}
            
        # Calculate number of missiles based on caster level
        caster_level = getattr(caster, 'level', 1)
        num_missiles = min(5, 1 + (caster_level - 1) // 2)  # 1 at level 1, up to 5 at level 9
        
        total_damage = 0
        damage_rolls = []
        
        for i in range(num_missiles):
            # Each missile does 1d4+1 damage
            if hasattr(self, 'dice_system') and self.dice_system:
                damage = self.dice_system.roll("1d4+1")
            else:
                damage = self.roll_damage("1d4+1", caster)
            total_damage += damage
            damage_rolls.append(damage)
            
        # Add spell power bonus
        spell_power = self.get_spell_power_bonus(caster)
        total_damage += spell_power
        
        target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
        
        missile_text = f"{num_missiles} glowing dart{'s' if num_missiles > 1 else ''}"
        hit_text = f"hit{'s' if num_missiles == 1 else ''}"
        
        message = f"You launch {missile_text} at {target_name}! The magic missile{'s' if num_missiles > 1 else ''} {hit_text} for {total_damage} force damage!"
        
        effects_data = {
            'type': 'damage',
            'damage': total_damage,
            'damage_type': 'force',
            'target': target,
            'auto_hit': True  # Magic missile always hits
        }
        
        return True, message, effects_data


class Light(BaseSpell):
    """Light - Illuminates dark areas"""
    
    def __init__(self):
        super().__init__("Light", 0, "mage")
        
    @property
    def description(self) -> str:
        return "Creates a bright light that illuminates the surrounding area"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.NONE
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.HOURS
        
    @property
    def duration_value(self) -> int:
        return 1  # 1 hour
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Light"""
        message = "A bright magical light surrounds you, illuminating the area."
        
        effects_data = {
            'type': 'utility',
            'effect': 'light',
            'duration': 60,  # 1 hour in minutes
            'caster': caster
        }
        
        return True, message, effects_data


class Fireball(BaseSpell):
    """Fireball - 8d6 fire damage area effect"""
    
    def __init__(self):
        super().__init__("Fireball", 3, "mage")
        
    @property
    def description(self) -> str:
        return "Hurls a blazing sphere that explodes in a fiery blast"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ENEMY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Fireball"""
        if not target:
            return False, "You must target an enemy", {}
            
        # Calculate damage
        base_damage = self.roll_damage("8d6", caster)
        
        target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
        
        message = f"You hurl a blazing sphere of fire at {target_name}! The fireball explodes for {base_damage} fire damage!"
        
        effects_data = {
            'type': 'damage',
            'damage': base_damage,
            'damage_type': 'fire',
            'target': target,
            'area_effect': True,
            'save_type': 'dexterity',
            'save_dc': 8 + caster.level + self.get_spell_power_bonus(caster)
        }
        
        return True, message, effects_data


class LightningBolt(BaseSpell):
    """Lightning Bolt - 8d6 electric damage in a line"""
    
    def __init__(self):
        super().__init__("Lightning Bolt", 3, "mage")
        
    @property
    def description(self) -> str:
        return "Unleashes a powerful bolt of electricity that strikes in a line"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SINGLE_ENEMY
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.INSTANT
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Lightning Bolt"""
        if not target:
            return False, "You must target an enemy", {}
            
        # Calculate damage
        base_damage = self.roll_damage("8d6", caster)
        
        target_name = target.get('name', 'the target') if isinstance(target, dict) else getattr(target, 'name', 'the target')
        
        message = f"You unleash a brilliant bolt of lightning at {target_name}! The lightning strikes for {base_damage} electric damage!"
        
        effects_data = {
            'type': 'damage',
            'damage': base_damage,
            'damage_type': 'electric',
            'target': target,
            'line_effect': True,
            'save_type': 'dexterity',
            'save_dc': 8 + caster.level + self.get_spell_power_bonus(caster)
        }
        
        return True, message, effects_data


class Shield(BaseSpell):
    """Shield - +4 AC bonus for 10 minutes"""
    
    def __init__(self):
        super().__init__("Shield", 1, "mage")
        
    @property
    def description(self) -> str:
        return "Creates an invisible barrier that deflects attacks"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SELF
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.MINUTES
        
    @property
    def duration_value(self) -> int:
        return 10  # 10 minutes
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Shield"""
        message = "A shimmering magical barrier surrounds you, deflecting incoming attacks."
        
        effects_data = {
            'type': 'buff',
            'effect': 'shield',
            'ac_bonus': 4,
            'duration': 10,  # 10 minutes
            'target': caster
        }
        
        return True, message, effects_data


class MageArmor(BaseSpell):
    """Mage Armor - +2 AC bonus for 1 hour"""
    
    def __init__(self):
        super().__init__("Mage Armor", 1, "mage")
        
    @property
    def description(self) -> str:
        return "Surrounds the caster with protective magical force"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.SELF
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.HOURS
        
    @property
    def duration_value(self) -> int:
        return 1  # 1 hour
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Mage Armor"""
        message = "Magical energy coalesces around you, forming a protective barrier."
        
        effects_data = {
            'type': 'buff',
            'effect': 'mage_armor',
            'ac_bonus': 2,
            'duration': 60,  # 1 hour in minutes
            'target': caster
        }
        
        return True, message, effects_data


class DetectMagic(BaseSpell):
    """Detect Magic - Reveals magical auras"""
    
    def __init__(self):
        super().__init__("Detect Magic", 0, "mage")
        
    @property
    def description(self) -> str:
        return "Reveals the presence of magical auras within the area"
        
    @property
    def target_type(self) -> SpellTarget:
        return SpellTarget.NONE
        
    @property
    def duration(self) -> SpellDuration:
        return SpellDuration.MINUTES
        
    @property
    def duration_value(self) -> int:
        return 10  # 10 minutes
        
    def cast(self, caster, target=None, combat_system=None, ui_manager=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast Detect Magic"""
        message = "Your eyes glow briefly as you sense the magical auras around you."
        
        effects_data = {
            'type': 'utility',
            'effect': 'detect_magic',
            'duration': 10,  # 10 minutes
            'caster': caster
        }
        
        return True, message, effects_data


# List of all mage spells for registration
MAGE_SPELLS = [
    MagicMissile,
    Light,
    Fireball,
    LightningBolt,
    Shield,
    MageArmor,
    DetectMagic
]