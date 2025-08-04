"""
Warrior Character Class for Rogue City
Traditional MajorMUD pure fighter class - the baseline for all combat classes.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple


class Warrior(BaseCharacter):
    """
    Warrior class - Pure fighter and weapon master
    
    BASELINE CLASS - Fast progression, beginner-friendly
    
    Experience Penalty: +0% (fastest leveling in game)
    Stat Modifiers: +3 STR, +2 CON, -1 INT, -1 WIS
    Hit Die: d10 (excellent HP progression)
    Attacks Per Turn: Multiple attacks at higher levels
    Critical Range: 20 (standard critical chance)
    
    PURE FIGHTER CORE:
    - Weapon specialization with chosen weapon type
    - Multiple attacks per round at higher levels
    - All weapon and armor proficiencies
    - Combat expertise and battle tactics
    - Weapon mastery for critical hit improvements
    - Armor optimization for maximum protection
    
    COMBAT ABILITIES:
    - Weapon Specialization: Choose weapon type for +2 damage
    - Multiple Attacks: Extra attacks per round based on level
    - Combat Expertise: Proficiency with all weapon types
    - Battle Tactics: Temporary damage and accuracy bonuses
    - Weapon Mastery: Critical hit improvements with specialized weapons
    - Armor Optimization: Maximum AC benefit from all armor types
    
    EQUIPMENT ACCESS:
    - Weapons: All weapon types with full proficiency
    - Armor: All armor types with no penalties
    - Magic: Can use magical weapons and armor
    - Accessories: All equipment types available
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Warrior character with combat mastery systems"""
        super().__init__(name, 'warrior', race_id, alignment)
        
        # Combat mastery attributes
        self.weapon_specialization = None  # Set during character creation or leveling
        self.specialized_weapon_bonus = 2  # +2 damage with specialized weapon
        self.combat_expertise_bonus = self._calculate_combat_expertise()
        
        # Multiple attacks system
        self.attacks_per_round = self._calculate_attacks_per_round()
        self.battle_tactics_uses = max(1, self.level // 3)  # Uses per rest
        
        # Armor optimization
        self.armor_optimization_bonus = self._calculate_armor_optimization()
        
    def get_hit_die_value(self) -> int:
        """Warriors use d10 hit die (excellent HP progression)"""
        return 10
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d10"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Warriors attack every 3 seconds unarmed (standard speed)"""
        return 3.0
        
    def get_critical_range(self) -> int:
        """Warriors crit on natural 20 (standard critical)"""
        # Weapon mastery can improve this with specialized weapons
        if self.weapon_specialization and self.level >= 10:
            return 19  # Improved crit with specialized weapon at level 10+
        return 20
        
    def get_experience_penalty(self) -> int:
        """Warriors have 0% experience penalty (baseline class)"""
        return 0
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Warrior special abilities"""
        return {
            # Combat mastery
            'weapon_specialization': self.weapon_specialization,
            'specialized_weapon_bonus': self.specialized_weapon_bonus,
            'combat_expertise': self.get_combat_expertise_bonus(),
            'multiple_attacks': self.get_attacks_per_round(),
            'battle_tactics': self.level >= 5,
            'weapon_mastery': self.level >= 10,
            'armor_optimization': self.get_armor_optimization_bonus(),
            
            # Equipment proficiencies
            'all_weapon_proficiency': True,
            'all_armor_proficiency': True,
            'shield_mastery': True,
            
            # Combat abilities
            'improved_critical_specialized': self.weapon_specialization and self.level >= 10,
            'critical_range': self.get_critical_range(),
            'damage_reduction': self.level // 5,  # 1 point per 5 levels
            
            # Battle tactics
            'battle_tactics_uses': self.battle_tactics_uses,
            'intimidate': True,
            'rally': self.level >= 8
        }
        
    # === COMBAT MASTERY ABILITIES ===
    
    def _calculate_combat_expertise(self) -> int:
        """Calculate combat expertise bonus"""
        base_bonus = 1
        level_bonus = self.level // 4  # +1 per 4 levels
        return base_bonus + level_bonus
    
    def get_combat_expertise_bonus(self) -> int:
        """Get current combat expertise bonus"""
        return self._calculate_combat_expertise()
    
    def _calculate_attacks_per_round(self) -> int:
        """Calculate number of attacks per round"""
        base_attacks = 1
        if self.level >= 6:
            base_attacks += 1  # 2 attacks at level 6
        if self.level >= 11:
            base_attacks += 1  # 3 attacks at level 11
        if self.level >= 16:
            base_attacks += 1  # 4 attacks at level 16
        return base_attacks
    
    def get_attacks_per_round(self) -> int:
        """Get current attacks per round"""
        return self._calculate_attacks_per_round()
    
    def _calculate_armor_optimization(self) -> int:
        """Calculate armor optimization bonus"""
        base_bonus = 1
        level_bonus = self.level // 6  # +1 per 6 levels
        return base_bonus + level_bonus
    
    def get_armor_optimization_bonus(self) -> int:
        """Get armor optimization AC bonus"""
        return self._calculate_armor_optimization()
    
    def set_weapon_specialization(self, weapon_type: str) -> bool:
        """Set weapon specialization (once per character)"""
        if self.weapon_specialization is None:
            valid_types = ['sword', 'axe', 'mace', 'spear', 'bow', 'crossbow', 'dagger']
            if weapon_type.lower() in valid_types:
                self.weapon_specialization = weapon_type.lower()
                return True
        return False
    
    def get_weapon_damage_bonus(self, weapon_type: str = None) -> int:
        """Get damage bonus for weapon type"""
        bonus = 0
        
        # Strength modifier (always applies)
        str_modifier = (self.stats['strength'] - 10) // 2
        bonus += str_modifier
        
        # Weapon specialization bonus
        if weapon_type and self.weapon_specialization == weapon_type.lower():
            bonus += self.specialized_weapon_bonus
            
        # Combat expertise bonus (applies to all weapons)
        bonus += self.get_combat_expertise_bonus()
        
        return bonus
    
    def can_use_battle_tactics(self) -> bool:
        """Check if warrior can use battle tactics"""
        return self.level >= 5 and self.battle_tactics_uses > 0
    
    def use_battle_tactics(self) -> Dict[str, int]:
        """Use battle tactics ability"""
        if not self.can_use_battle_tactics():
            return {}
            
        self.battle_tactics_uses -= 1
        return {
            'attack_bonus': 2,
            'damage_bonus': 3,
            'duration_rounds': 5
        }
    
    def can_rally_allies(self) -> bool:
        """Check if warrior can rally allies"""
        return self.level >= 8
    
    def rally_allies(self) -> Dict[str, int]:
        """Rally allies with inspiring leadership"""
        if not self.can_rally_allies():
            return {}
            
        return {
            'morale_bonus': 1,
            'damage_bonus': 1,
            'fear_immunity': True,
            'duration_rounds': 10
        }
    
    def get_intimidation_bonus(self) -> int:
        """Get intimidation skill bonus"""
        base_bonus = 2
        str_bonus = (self.stats['strength'] - 10) // 2
        level_bonus = self.level // 3
        return base_bonus + str_bonus + level_bonus
    
    def attempt_intimidate(self, target_level: int = 1) -> bool:
        """Attempt to intimidate a target"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            intimidate_roll = dice.roll("1d20") + self.get_intimidation_bonus()
            dc = 10 + target_level
            return intimidate_roll >= dc
        except ImportError:
            import random
            return random.randint(1, 20) + self.get_intimidation_bonus() >= (10 + target_level)
    
    def get_damage_reduction(self) -> int:
        """Get damage reduction from warrior training"""
        return max(0, self.level // 5)  # 1 point per 5 levels
    
    # === EQUIPMENT MASTERY ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Warriors can use all weapon types"""
        return True
    
    def can_use_armor(self, armor) -> bool:
        """Warriors can use all armor types"""
        return True
    
    def can_use_shield(self, shield) -> bool:
        """Warriors can use all shield types"""
        return True
    
    def calculate_derived_stats(self):
        """Override to include armor optimization bonus"""
        super().calculate_derived_stats()
        
        # Add armor optimization bonus to AC
        if hasattr(self, 'armor_optimization_bonus'):
            self.armor_class += self.get_armor_optimization_bonus()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Warrior':
        """Create Warrior from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        warrior = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        warrior.level = data['level']
        warrior.experience = data['experience']
        warrior.base_stats = data.get('base_stats', warrior.base_stats)
        warrior.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        warrior.max_hp = derived['max_hp']
        warrior.current_hp = derived['current_hp']
        warrior.armor_class = derived['armor_class']
        warrior.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        warrior.current_area = location.get('area_id')
        warrior.current_room = location.get('room_id')
        
        # Initialize item systems
        warrior.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            warrior.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            warrior.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        warrior.unallocated_stats = data.get('unallocated_stats', 0)
        warrior.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            warrior.load_alignment_data(data['alignment_data'])
        
        # Restore warrior-specific attributes
        warrior_data = data.get('warrior_data', {})
        warrior.weapon_specialization = warrior_data.get('weapon_specialization')
        warrior.battle_tactics_uses = warrior_data.get('battle_tactics_uses', max(1, warrior.level // 3))
        
        # Recalculate warrior-specific attributes
        warrior.specialized_weapon_bonus = 2
        warrior.combat_expertise_bonus = warrior._calculate_combat_expertise()
        warrior.attacks_per_round = warrior._calculate_attacks_per_round()
        warrior.armor_optimization_bonus = warrior._calculate_armor_optimization()
        
        return warrior
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include warrior-specific data"""
        data = super().to_dict()
        data['warrior_data'] = {
            'weapon_specialization': self.weapon_specialization,
            'battle_tactics_uses': self.battle_tactics_uses
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Warrior"""
        abilities = []
        
        # Attacks per round
        attacks = self.get_attacks_per_round()
        if attacks > 1:
            abilities.append(f"{attacks} attacks")
        
        # Weapon specialization
        if self.weapon_specialization:
            abilities.append(f"{self.weapon_specialization.title()} Spec")
        
        # Combat expertise
        expertise = self.get_combat_expertise_bonus()
        abilities.append(f"Combat +{expertise}")
        
        # Armor optimization
        armor_bonus = self.get_armor_optimization_bonus()
        abilities.append(f"Armor +{armor_bonus}")
        
        # High-level abilities
        if self.can_use_battle_tactics():
            abilities.append(f"Tactics ({self.battle_tactics_uses})")
        if self.can_rally_allies():
            abilities.append("Rally")
        
        # Damage reduction
        dr = self.get_damage_reduction()
        if dr > 0:
            abilities.append(f"DR {dr}")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str