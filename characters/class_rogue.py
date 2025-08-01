"""
Rogue Character Class for Rogue City
High difficulty class focused on dexterity, critical strikes, and skill.
"""

from .base_character import BaseCharacter
from typing import Dict, Any


class Rogue(BaseCharacter):
    """
    Rogue class - Masters of stealth and precision
    
    Difficulty: 11 (High)
    Stat Modifiers: +3 DEX, +2 INT, -2 STR, -2 CON, -1 WIS, -1 CHA
    Hit Die: d6
    Attack Speed: 2.0 seconds (fast daggers)
    Critical Range: 19-20 (improved critical chance)
    """
    
    def __init__(self, name: str):
        """Initialize Rogue character"""
        super().__init__(name, 'rogue')
        
    def get_hit_die_value(self) -> int:
        """Rogues use d6 hit die (average 6 HP per level)"""
        return 6
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d6"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Rogues attack every 2 seconds unarmed (fastest)"""
        return 2.0
        
    def get_critical_range(self) -> int:
        """Rogues crit on 19-20 (improved critical chance)"""
        return 19
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Rogue-specific special abilities"""
        return {
            'sneak_attack': True,
            'skill_bonus': 2,
            'evasion_bonus': 1,
            'backstab_multiplier': 1.5,
            'improved_critical': True,
            'light_armor_only': True
        }
        
    def calculate_derived_stats(self):
        """Override to use DEX for attack bonus instead of STR"""
        super().calculate_derived_stats()
        
        # Rogues use DEX modifier for attack bonus with finesse weapons
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        self.base_attack_bonus = self.level + dex_modifier
        
    def get_sneak_attack_damage(self) -> int:
        """Calculate sneak attack bonus damage dice"""
        # Sneak attack: +1d6 per 2 levels (minimum 1d6)
        sneak_dice = max(1, (self.level + 1) // 2)
        return sneak_dice
        
    def can_sneak_attack(self, target_surprised: bool = False, flanking: bool = False) -> bool:
        """Check if rogue can perform sneak attack"""
        # Sneak attack when target is surprised, flanked, or rogue is hidden
        return target_surprised or flanking
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rogue':
        """Create Rogue from save data"""
        rogue = cls(data['character_name'])
        
        # Restore basic character data
        rogue.level = data['level']
        rogue.experience = data['experience']
        rogue.base_stats = data.get('base_stats', rogue.base_stats)
        rogue.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        rogue.max_hp = derived['max_hp']
        rogue.current_hp = derived['current_hp']
        rogue.armor_class = derived['armor_class']
        rogue.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        rogue.current_area = location.get('area_id')
        rogue.current_room = location.get('room_id')
        
        # Initialize item systems
        rogue.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            rogue.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            rogue.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        rogue.unallocated_stats = data.get('unallocated_stats', 0)
        rogue.creation_complete = data.get('creation_complete', True)
        
        return rogue
        
    def __str__(self) -> str:
        """String representation of Rogue"""
        abilities = []
        if self.get_special_abilities().get('sneak_attack'):
            sneak_dice = self.get_sneak_attack_damage()
            abilities.append(f"Sneak Attack +{sneak_dice}d6")
        if self.get_special_abilities().get('improved_critical'):
            abilities.append("Improved Critical (19-20)")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str