"""
Mystic Character Class for Rogue City
Moderate difficulty balanced class focused on dexterity, wisdom, and evasion.
"""

from .base_character import BaseCharacter
from typing import Dict, Any


class Mystic(BaseCharacter):
    """
    Mystic class - Balanced warriors who blend physical and spiritual training
    
    Difficulty: 6 (Moderate)
    Stat Modifiers: +4 DEX, +2 WIS, +1 CHA, -1 STR, -2 INT, -1 CON
    Hit Die: d8
    Attack Speed: 3.0 seconds (unarmed/simple weapons)
    Critical Range: 20 (standard critical chance)
    Special: 15% base evasion chance
    """
    
    def __init__(self, name: str, race_id: str = "human"):
        """Initialize Mystic character"""
        super().__init__(name, 'mystic', race_id)
        
    def get_hit_die_value(self) -> int:
        """Mystics use d8 hit die (moderate HP per level)"""
        return 8
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d8"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Mystics attack every 3 seconds unarmed"""
        return 3.0
        
    def get_critical_range(self) -> int:
        """Mystics crit only on natural 20 (standard)"""
        return 20
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Mystic-specific special abilities"""
        return {
            'evasion_chance': self.get_evasion_chance(),
            'unarmed_bonus': 2,
            'meditation': True,
            'spiritual_awareness': True,
            'ki_strike': self.level >= 5,
            'light_medium_armor': True
        }
        
    def calculate_derived_stats(self):
        """Override to use DEX for attack bonus with unarmed combat"""
        super().calculate_derived_stats()
        
        # Mystics use DEX modifier for unarmed attack bonus
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        self.base_attack_bonus = self.level + dex_modifier
        
    def get_evasion_chance(self) -> int:
        """Calculate total evasion chance percentage"""
        base_evasion = 15  # Base 15% evasion
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        wis_modifier = (self.stats['wisdom'] - 10) // 2
        
        # Add stat modifiers and level bonus
        total_evasion = base_evasion + dex_modifier + (wis_modifier // 2) + (self.level // 4)
        
        # Cap at 50% maximum evasion
        return min(50, max(0, total_evasion))
        
    def can_evade_attack(self) -> bool:
        """Roll for evasion attempt"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            roll = dice.roll("1d100")
            return roll <= self.get_evasion_chance()
        except ImportError:
            # Fallback without dice system
            import random
            return random.randint(1, 100) <= self.get_evasion_chance()
            
    def get_unarmed_damage(self) -> str:
        """Get unarmed combat damage"""
        base_damage = "1d4"  # Base unarmed damage
        unarmed_bonus = self.get_special_abilities().get('unarmed_bonus', 0)
        
        # Unarmed damage improves with level
        if self.level >= 5:
            base_damage = "1d6"
        if self.level >= 10:
            base_damage = "1d8"
        if self.level >= 15:
            base_damage = "1d10"
            
        # Add strength modifier
        str_modifier = (self.stats['strength'] - 10) // 2
        total_bonus = unarmed_bonus + str_modifier
        
        if total_bonus > 0:
            return f"{base_damage}+{total_bonus}"
        elif total_bonus < 0:
            return f"{base_damage}{total_bonus}"
        else:
            return base_damage
            
    def can_use_ki_strike(self) -> bool:
        """Check if mystic can use ki strike ability"""
        return self.level >= 5
        
    def meditate(self) -> Dict[str, int]:
        """Meditation ability for healing and focus"""
        if not self.get_special_abilities().get('meditation'):
            return {}
            
        wis_modifier = (self.stats['wisdom'] - 10) // 2
        
        # Meditation restores HP and provides temporary bonuses
        hp_restored = max(1, wis_modifier + (self.level // 3))
        actual_healing = self.heal(hp_restored)
        
        return {
            'hp_restored': actual_healing,
            'focus_bonus': wis_modifier,  # Temporary bonus to next attack
            'duration_rounds': 3
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mystic':
        """Create Mystic from save data"""
        race_id = data.get('race_id', 'human')
        mystic = cls(data['character_name'], race_id)
        
        # Restore basic character data
        mystic.level = data['level']
        mystic.experience = data['experience']
        mystic.base_stats = data.get('base_stats', mystic.base_stats)
        mystic.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        mystic.max_hp = derived['max_hp']
        mystic.current_hp = derived['current_hp']
        mystic.armor_class = derived['armor_class']
        mystic.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        mystic.current_area = location.get('area_id')
        mystic.current_room = location.get('room_id')
        
        # Initialize item systems
        mystic.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            mystic.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            mystic.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        mystic.unallocated_stats = data.get('unallocated_stats', 0)
        mystic.creation_complete = data.get('creation_complete', True)
        
        return mystic
        
    def __str__(self) -> str:
        """String representation of Mystic"""
        abilities = []
        
        evasion = self.get_evasion_chance()
        abilities.append(f"Evasion {evasion}%")
        
        unarmed_dmg = self.get_unarmed_damage()
        abilities.append(f"Unarmed {unarmed_dmg}")
        
        if self.can_use_ki_strike():
            abilities.append("Ki Strike")
            
        if self.get_special_abilities().get('meditation'):
            abilities.append("Meditation")
        
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str