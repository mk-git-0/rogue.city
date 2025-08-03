"""
Mage Character Class for Rogue City
High difficulty spellcaster class with mana system and powerful magic.
"""

from .base_character import BaseCharacter
from typing import Dict, Any


class Mage(BaseCharacter):
    """
    Mage class - Wielders of arcane power with devastating magical abilities
    
    Difficulty: 9 (High)
    Stat Modifiers: +3 INT, +2 WIS, -2 STR, -3 CON
    Hit Die: d4
    Attack Speed: 6.0 seconds (slow fire bolt casting)
    Critical Range: 20 (standard critical chance)
    Special: Mana system for spellcasting
    """
    
    def __init__(self, name: str, race_id: str = "human"):
        """Initialize Mage character"""
        # Initialize mana attributes before calling parent __init__
        self.max_mana = 0
        self.current_mana = 0
        super().__init__(name, 'mage', race_id)
        
    def get_hit_die_value(self) -> int:
        """Mages use d4 hit die (lowest HP per level)"""
        return 4
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d4"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Mages attack every 6 seconds unarmed"""
        return 6.0
        
    def get_critical_range(self) -> int:
        """Mages crit only on natural 20 (standard)"""
        return 20
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Mage-specific special abilities"""
        return {
            'mana_system': True,
            'spell_power_bonus': 2,
            'mana_regeneration': 5,
            'arcane_knowledge': True,
            'spell_critical': True,
            'robes_only': True
        }
        
    def calculate_derived_stats(self):
        """Override to include mana calculation"""
        super().calculate_derived_stats()
        
        # Mana calculation: 6 + (2 * INT modifier * level)
        int_modifier = max(0, (self.stats['intelligence'] - 10) // 2)
        level_for_mana = max(1, self.level)  # Minimum level 1 for mana calculation
        self.max_mana = 6 + (2 * int_modifier * level_for_mana)
        
        # Set current mana to max if this is first calculation
        if self.current_mana == 0:
            self.current_mana = self.max_mana
            
        # Mages use INT modifier for spell attack bonus
        int_modifier = (self.stats['intelligence'] - 10) // 2
        self.base_attack_bonus = self.level + int_modifier
        
    def get_mana_percentage(self) -> float:
        """Get mana as percentage (0.0 to 1.0)"""
        if self.max_mana <= 0:
            return 0.0
        return self.current_mana / self.max_mana
        
    def spend_mana(self, amount: int) -> bool:
        """Spend mana for spellcasting"""
        if self.current_mana < amount:
            return False
        self.current_mana -= amount
        return True
        
    def restore_mana(self, amount: int) -> int:
        """Restore mana, return actual amount restored"""
        if self.current_mana >= self.max_mana:
            return 0
            
        old_mana = self.current_mana
        self.current_mana = min(self.max_mana, self.current_mana + amount)
        return self.current_mana - old_mana
        
    def regenerate_mana(self) -> int:
        """Natural mana regeneration (called periodically)"""
        regen_rate = self.get_special_abilities().get('mana_regeneration', 5)
        wis_modifier = (self.stats['wisdom'] - 10) // 2
        regen_amount = max(1, regen_rate + wis_modifier)
        return self.restore_mana(regen_amount)
        
    def get_spell_power_bonus(self) -> int:
        """Get spell damage bonus"""
        base_bonus = self.get_special_abilities().get('spell_power_bonus', 0)
        int_modifier = (self.stats['intelligence'] - 10) // 2
        return base_bonus + int_modifier + (self.level // 5)
        
    def can_cast_spell(self, mana_cost: int) -> bool:
        """Check if mage can cast a spell"""
        return self.current_mana >= mana_cost
        
    def get_fire_bolt_damage(self) -> str:
        """Get fire bolt spell damage dice"""
        # Fire bolt scales with level: 1d10 + spell power bonus
        base_dice = "1d10"
        spell_bonus = self.get_spell_power_bonus()
        if spell_bonus > 0:
            return f"{base_dice}+{spell_bonus}"
        return base_dice
        
    def to_dict(self) -> Dict[str, Any]:
        """Override to include mana in save data"""
        data = super().to_dict()
        data['mana'] = {
            'max_mana': self.max_mana,
            'current_mana': self.current_mana
        }
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mage':
        """Create Mage from save data"""
        race_id = data.get('race_id', 'human')
        mage = cls(data['character_name'], race_id)
        
        # Restore basic character data
        mage.level = data['level']
        mage.experience = data['experience']
        mage.base_stats = data.get('base_stats', mage.base_stats)
        mage.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        mage.max_hp = derived['max_hp']
        mage.current_hp = derived['current_hp']
        mage.armor_class = derived['armor_class']
        mage.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        mage.current_area = location.get('area_id')
        mage.current_room = location.get('room_id')
        
        # Initialize item systems
        mage.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            mage.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            mage.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        mage.unallocated_stats = data.get('unallocated_stats', 0)
        mage.creation_complete = data.get('creation_complete', True)
        
        # Restore mage-specific data
        if 'mana' in data:
            mage.max_mana = data['mana']['max_mana']
            mage.current_mana = data['mana']['current_mana']
        else:
            # Recalculate mana if not in save data
            mage.calculate_derived_stats()
            
        return mage
        
    def __str__(self) -> str:
        """String representation of Mage"""
        abilities = []
        
        mana_status = f"MP: {self.current_mana}/{self.max_mana}"
        abilities.append(mana_status)
        
        spell_bonus = self.get_spell_power_bonus()
        if spell_bonus > 0:
            abilities.append(f"Spell Power +{spell_bonus}")
            
        fire_bolt_dmg = self.get_fire_bolt_damage()
        abilities.append(f"Fire Bolt {fire_bolt_dmg}")
        
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str