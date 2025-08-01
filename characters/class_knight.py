"""
Knight Character Class for Rogue City
Low difficulty tank class focused on strength, constitution, and survivability.
"""

from .base_character import BaseCharacter
from typing import Dict, Any


class Knight(BaseCharacter):
    """
    Knight class - Stalwart defenders and front-line fighters
    
    Difficulty: 3 (Easy)
    Stat Modifiers: +3 STR, +1 DEX, +2 CON, +1 CHA, -1 INT, -1 WIS
    Hit Die: d10
    Attack Speed: 4.0 seconds (heavy swords)
    Critical Range: 20 (standard critical chance)
    """
    
    def __init__(self, name: str):
        """Initialize Knight character"""
        super().__init__(name, 'knight')
        
    def get_hit_die_value(self) -> int:
        """Knights use d10 hit die (highest HP per level)"""
        return 10
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d10"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Knights attack every 4 seconds unarmed"""
        return 4.0
        
    def get_critical_range(self) -> int:
        """Knights crit only on natural 20 (standard)"""
        return 20
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Knight-specific special abilities"""
        return {
            'damage_resistance': 1,
            'heavy_armor_proficiency': True,
            'leadership_bonus': 1,
            'defensive_stance': True,
            'weapon_specialization': 'martial',
            'armor_mastery': True
        }
        
    def calculate_derived_stats(self):
        """Override to include damage resistance in effective HP"""
        super().calculate_derived_stats()
        
        # Knights get +1 AC from defensive training at higher levels
        if self.level >= 5:
            self.armor_class += 1
            
    def get_damage_resistance(self) -> int:
        """Get damage resistance value"""
        base_resistance = self.get_special_abilities().get('damage_resistance', 0)
        
        # Increase resistance at higher levels
        if self.level >= 10:
            base_resistance += 1
        if self.level >= 20:
            base_resistance += 1
            
        return base_resistance
        
    def can_use_defensive_stance(self) -> bool:
        """Check if knight can use defensive stance"""
        return self.level >= 3
        
    def defensive_stance_bonus(self) -> Dict[str, int]:
        """Get defensive stance bonuses"""
        if not self.can_use_defensive_stance():
            return {}
            
        return {
            'armor_class': 2,
            'damage_resistance': 2,
            'attack_penalty': -2  # Trade offense for defense
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Knight':
        """Create Knight from save data"""
        knight = cls(data['character_name'])
        
        # Restore basic character data
        knight.level = data['level']
        knight.experience = data['experience']
        knight.base_stats = data.get('base_stats', knight.base_stats)
        knight.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        knight.max_hp = derived['max_hp']
        knight.current_hp = derived['current_hp']
        knight.armor_class = derived['armor_class']
        knight.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        knight.current_area = location.get('area_id')
        knight.current_room = location.get('room_id')
        
        # Initialize item systems
        knight.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            knight.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            knight.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        knight.unallocated_stats = data.get('unallocated_stats', 0)
        knight.creation_complete = data.get('creation_complete', True)
        
        return knight
        
    def __str__(self) -> str:
        """String representation of Knight"""
        abilities = []
        
        dr = self.get_damage_resistance()
        if dr > 0:
            abilities.append(f"DR {dr}")
            
        if self.can_use_defensive_stance():
            abilities.append("Defensive Stance")
            
        if self.get_special_abilities().get('heavy_armor_proficiency'):
            abilities.append("Heavy Armor")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str