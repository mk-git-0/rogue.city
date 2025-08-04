"""
Knight Character Class for Rogue City
Beginner-friendly defensive specialist with shield mastery and heavy armor.
Designed as the safest, most straightforward class for new players.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any


class Knight(BaseCharacter):
    """
    Knight class - Defensive specialist with shield mastery and heavy armor
    
    BEGINNER-FRIENDLY CLASS - Safe and straightforward
    
    Difficulty: 3 (Lowest) - Perfect for new players
    Stat Modifiers: +3 STR, +1 DEX, +2 CON, +1 CHA, -1 INT, -1 WIS
    Hit Die: d10 (Highest HP per level)  
    Attacks Per Turn: Steady defensive combat style
    Critical Range: 20 (standard critical chance)
    
    DEFENSIVE CORE ABILITIES:
    - Shield Mastery: Doubled AC bonus from shields, active blocking
    - Heavy Armor Proficiency: No movement penalties, bonus AC
    - Damage Resistance: Reduce all incoming damage
    - Guardian Protection: Protect party members
    
    TACTICAL ABILITIES:
    - Defensive Stance: Trade offense for superior defense
    - Taunt: Force enemies to attack the knight
    - Shield Bash: Stun enemies with shield attacks
    - Armor Mastery: Additional bonuses from heavy armor
    
    EQUIPMENT PERMISSIONS:
    - Weapons: All weapon types with proficiency
    - Armor: All armor types with mastery bonuses
    - Shields: All shield types with doubled bonuses
    - Equipment: Can use any non-class-restricted items
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Knight character with defensive systems"""
        super().__init__(name, 'knight', race_id, alignment)
        
        # Defensive stance system
        self.defensive_stance_active = False
        self.defensive_stance_ac_bonus = 3
        self.defensive_stance_damage_bonus = 2
        
        # Shield mastery system
        self.shield_ac_multiplier = 2.0  # Double shield AC bonuses
        self.shield_block_chance = 20  # Base 20% block chance
        
        # Guardian protection system
        self.protecting_allies = []
        self.guardian_ac_bonus = 1  # AC bonus provided to protected allies
        
        # Combat state tracking
        self.taunt_active = False
        self.taunt_duration = 0
        self.last_shield_bash = 0
        
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
        """Comprehensive Knight defensive abilities"""
        return {
            # Shield abilities
            'shield_mastery': True,
            'shield_ac_multiplier': self.get_shield_ac_multiplier(),
            'shield_block_chance': self.get_shield_block_chance(),
            'shield_bash': True,
            
            # Defensive abilities
            'damage_resistance': self.get_damage_resistance(),
            'defensive_stance': self.can_use_defensive_stance(),
            'defensive_stance_ac_bonus': self.defensive_stance_ac_bonus,
            'heavy_armor_proficiency': True,
            'armor_mastery': True,
            
            # Guardian abilities
            'guardian_protection': self.level >= 5,
            'taunt': self.level >= 3,
            'protective_aura': self.level >= 8,
            
            # Combat abilities
            'weapon_proficiency': 'all',
            'martial_training': True,
            'leadership_bonus': 1,
            'intimidation': True,
            
            # Equipment permissions
            'all_weapons': True,
            'all_armor': True,
            'all_shields': True
        }
        
    def calculate_derived_stats(self):
        """Override to include defensive bonuses and shield mastery"""
        super().calculate_derived_stats()
        
        # Apply defensive training bonuses
        if self.level >= 5:
            self.armor_class += 1  # Defensive training
        if self.level >= 10:
            self.armor_class += 1  # Advanced training
        
        # Apply defensive stance if active (check if attribute exists first)
        if hasattr(self, 'defensive_stance_active') and self.defensive_stance_active:
            self.armor_class += self.defensive_stance_ac_bonus
        
        # Apply shield bonuses if equipped
        if hasattr(self, 'equipment_system') and self.equipment_system:
            shield_ac = self.equipment_system.get_shield_ac_bonus()
            if shield_ac > 0:
                # Knights get doubled shield AC bonus
                additional_shield_ac = int(shield_ac * (self.get_shield_ac_multiplier() - 1))
                self.armor_class += additional_shield_ac
            
    # === SHIELD MASTERY ABILITIES ===
    
    def get_shield_ac_multiplier(self) -> float:
        """Get shield AC bonus multiplier"""
        return self.shield_ac_multiplier
    
    def get_shield_block_chance(self) -> int:
        """Calculate shield block chance percentage"""
        if not self._has_shield_equipped():
            return 0
        
        base_chance = self.shield_block_chance
        level_bonus = self.level // 4  # +5% per 4 levels
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 4)  # Small dex contribution
        
        total_chance = base_chance + (level_bonus * 5) + dex_bonus
        return min(50, total_chance)  # Max 50% block chance
    
    def attempt_shield_block(self) -> bool:
        """Attempt to block an attack with shield"""
        if not self._has_shield_equipped():
            return False
        
        block_chance = self.get_shield_block_chance()
        if block_chance <= 0:
            return False
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            roll = dice.roll("1d100")
            return roll <= block_chance
        except ImportError:
            import random
            return random.randint(1, 100) <= block_chance
    
    def can_shield_bash(self) -> bool:
        """Check if knight can perform shield bash"""
        return self._has_shield_equipped() and self.level >= 2
    
    def shield_bash_damage(self) -> str:
        """Get shield bash damage dice"""
        if not self.can_shield_bash():
            return "0"
        
        base_damage = "1d4"  # Base shield bash damage
        str_bonus = (self.stats['strength'] - 10) // 2
        
        if self.level >= 8:
            base_damage = "1d6"  # Improved shield bash
        
        if str_bonus > 0:
            return f"{base_damage}+{str_bonus}"
        elif str_bonus < 0:
            return f"{base_damage}{str_bonus}"
        return base_damage
    
    def _has_shield_equipped(self) -> bool:
        """Check if knight has a shield equipped"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.has_shield_equipped()
        return False
    
    # === DEFENSIVE ABILITIES ===
    
    def get_damage_resistance(self) -> int:
        """Get damage resistance value"""
        base_resistance = 1  # Base damage resistance
        
        # Increase resistance at higher levels
        if self.level >= 10:
            base_resistance += 1
        if self.level >= 20:
            base_resistance += 1
        
        # Bonus from defensive stance
        if self.defensive_stance_active:
            base_resistance += self.defensive_stance_damage_bonus
        
        # Heavy armor bonus
        if self._has_heavy_armor():
            base_resistance += 1
            
        return base_resistance
    
    def can_use_defensive_stance(self) -> bool:
        """Check if knight can use defensive stance"""
        return self.level >= 3
    
    def toggle_defensive_stance(self) -> bool:
        """Toggle defensive stance on/off"""
        if not self.can_use_defensive_stance():
            return False
        
        self.defensive_stance_active = not self.defensive_stance_active
        # Recalculate AC when stance changes
        self.calculate_derived_stats()
        return True
    
    def get_defensive_stance_bonuses(self) -> Dict[str, int]:
        """Get current defensive stance bonuses"""
        if not self.defensive_stance_active:
            return {}
            
        return {
            'armor_class': self.defensive_stance_ac_bonus,
            'damage_resistance': self.defensive_stance_damage_bonus,
            'attack_penalty': -2,  # Trade offense for defense
            'movement_penalty': -10  # Reduced movement speed
        }
    
    def _has_heavy_armor(self) -> bool:
        """Check if knight is wearing heavy armor"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.has_heavy_armor()
        return False
    
    # === GUARDIAN ABILITIES ===
    
    def can_use_guardian_protection(self) -> bool:
        """Check if knight can use guardian protection"""
        return self.level >= 5
    
    def protect_ally(self, ally_name: str) -> bool:
        """Add ally to protection list"""
        if not self.can_use_guardian_protection():
            return False
        
        if ally_name not in self.protecting_allies:
            max_protected = 1 + (self.level // 10)  # 1 + 1 per 10 levels
            if len(self.protecting_allies) < max_protected:
                self.protecting_allies.append(ally_name)
                return True
        return False
    
    def stop_protecting_ally(self, ally_name: str) -> bool:
        """Remove ally from protection list"""
        if ally_name in self.protecting_allies:
            self.protecting_allies.remove(ally_name)
            return True
        return False
    
    def get_guardian_ac_bonus(self) -> int:
        """Get AC bonus provided to protected allies"""
        if not self.can_use_guardian_protection():
            return 0
        return self.guardian_ac_bonus
    
    def can_use_taunt(self) -> bool:
        """Check if knight can use taunt ability"""
        return self.level >= 3
    
    def use_taunt(self, duration_rounds: int = 3) -> bool:
        """Activate taunt to force enemies to attack knight"""
        if not self.can_use_taunt():
            return False
        
        self.taunt_active = True
        self.taunt_duration = duration_rounds
        return True
    
    def get_intimidation_bonus(self) -> int:
        """Get intimidation skill bonus"""
        base_bonus = 2
        cha_bonus = (self.stats['charisma'] - 10) // 2
        level_bonus = self.level // 5
        return base_bonus + cha_bonus + level_bonus
        
    def can_use_weapon(self, weapon) -> bool:
        """Knights can use all weapon types"""
        return True  # Knights have proficiency with all weapons
    
    def can_use_armor(self, armor) -> bool:
        """Knights can use all armor types"""
        return True  # Knights have proficiency with all armor
    
    def can_use_shield(self, shield) -> bool:
        """Knights can use all shield types"""
        return True  # Knights have proficiency with all shields
    
    def get_experience_penalty(self) -> int:
        """Knights have 10% experience penalty (defensive specialist)"""
        return 10
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Knight':
        """Create Knight from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        knight = cls(data['character_name'], race_id, alignment)
        
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
        
        # Load alignment data
        if 'alignment_data' in data:
            knight.load_alignment_data(data['alignment_data'])
        
        # Restore knight-specific state
        knight.defensive_stance_active = data.get('defensive_stance_active', False)
        knight.protecting_allies = data.get('protecting_allies', [])
        knight.taunt_active = data.get('taunt_active', False)
        knight.taunt_duration = data.get('taunt_duration', 0)
        
        return knight
        
    def to_dict(self) -> Dict[str, Any]:
        """Override to include knight-specific state"""
        data = super().to_dict()
        data.update({
            'defensive_stance_active': self.defensive_stance_active,
            'protecting_allies': self.protecting_allies,
            'taunt_active': self.taunt_active,
            'taunt_duration': self.taunt_duration
        })
        return data
    
    def __str__(self) -> str:
        """String representation of enhanced Knight"""
        abilities = []
        
        # Damage resistance
        dr = self.get_damage_resistance()
        abilities.append(f"DR {dr}")
        
        # Shield abilities
        if self._has_shield_equipped():
            shield_ac_mult = self.get_shield_ac_multiplier()
            block_chance = self.get_shield_block_chance()
            abilities.append(f"Shield {shield_ac_mult}x AC, {block_chance}% Block")
        
        # Defensive stance status
        if self.defensive_stance_active:
            abilities.append("Defensive Stance Active")
        elif self.can_use_defensive_stance():
            abilities.append("Defensive Stance")
        
        # Guardian protection
        if self.protecting_allies:
            abilities.append(f"Protecting {len(self.protecting_allies)}")
        elif self.can_use_guardian_protection():
            abilities.append("Guardian")
        
        # Taunt status
        if self.taunt_active:
            abilities.append(f"Taunt ({self.taunt_duration})")
        elif self.can_use_taunt():
            abilities.append("Taunt")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str