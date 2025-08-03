"""
Mystic Character Class for Rogue City
Balanced warrior-monk blending martial arts with mystical ki powers.
Moderate difficulty with versatile combat and spiritual abilities.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any


class Mystic(BaseCharacter):
    """
    Mystic class - Balanced warrior-monk with martial arts and ki powers
    
    BALANCED CLASS - Versatile combat and mystical abilities
    
    Difficulty: 6 (Moderate) - Accessible but rewarding mastery
    Stat Modifiers: +4 DEX, +2 WIS, +1 CHA, -1 STR, -2 INT, -1 CON
    Hit Die: d8 (Moderate HP per level)
    Attack Speed: 3.0 seconds (unarmed/simple weapons)
    Critical Range: 20 (standard critical chance)
    
    MARTIAL ARTS CORE:
    - Unarmed Combat: Scaling damage with bare hands
    - Evasion Training: High dodge chance with DEX/WIS
    - Multiple Attacks: Extra attacks at higher levels
    - Weapon Mastery: Bonus with simple weapons
    
    KI POWER SYSTEM:
    - Ki Pool: Based on WIS modifier and level
    - Ki Strike: Spend ki for bonus damage
    - Ki Defense: Spend ki for temporary AC boost
    - Ki Healing: Channel ki for self-healing
    - Ki Speed: Burst of enhanced movement
    
    SPIRITUAL ABILITIES:
    - Meditation: Recover ki and HP over time
    - Spiritual Resistance: Bonus vs mental effects
    - Inner Focus: Enhanced concentration
    - Mystical Insight: Detect spiritual auras
    
    EQUIPMENT BALANCE:
    - Weapons: Simple weapons and unarmed mastery
    - Armor: Light and medium armor (no heavy plate)
    - Flexibility: Most versatile equipment access
    - No Shields: Relies on evasion and ki defense
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Mystic character with ki and martial arts systems"""
        super().__init__(name, 'mystic', race_id, alignment)
        
        # Ki power system
        self.max_ki = self._calculate_max_ki()
        self.current_ki = self.max_ki
        self.ki_regeneration_rate = 1  # Ki per meditation/rest
        
        # Martial arts progression
        self.unarmed_damage_die = self._get_unarmed_damage_die()
        self.attacks_per_round = self._calculate_attacks_per_round()
        self.evasion_bonus = self._calculate_evasion_bonus()
        
        # Spiritual attributes
        self.meditation_uses = 3  # Uses per day
        self.spiritual_resistance = 2  # Base resistance to mental effects
        self.inner_focus_duration = 0  # Rounds of enhanced focus
        
        # Combat state
        self.ki_defense_active = False
        self.ki_defense_duration = 0
        self.last_meditation = 0
        
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
        """Comprehensive Mystic martial and mystical abilities"""
        return {
            # Ki power system
            'ki_pool': self.get_max_ki(),
            'ki_strike': True,
            'ki_defense': True,
            'ki_healing': self.level >= 3,
            'ki_speed': self.level >= 7,
            'ki_regeneration': True,
            
            # Martial arts abilities
            'unarmed_mastery': True,
            'unarmed_damage': self.get_unarmed_damage(),
            'evasion_training': self.get_evasion_chance(),
            'multiple_attacks': self.get_attacks_per_round(),
            'weapon_mastery': 'simple',
            'deflect_missiles': self.level >= 5,
            
            # Spiritual abilities
            'meditation': True,
            'meditation_uses': self.meditation_uses,
            'spiritual_resistance': self.get_spiritual_resistance(),
            'inner_focus': self.level >= 4,
            'mystical_insight': self.level >= 6,
            'spiritual_awareness': True,
            
            # Combat bonuses
            'improved_initiative': 2,
            'mental_fortitude': True,
            'balanced_fighting': True,
            
            # Equipment permissions
            'simple_weapons': True,
            'light_medium_armor': True,
            'no_shields': True,
            'unarmed_preferred': True
        }
        
    def calculate_derived_stats(self):
        """Override to include ki pool and martial arts calculations"""
        super().calculate_derived_stats()
        
        # Mystics use DEX modifier for unarmed attack bonus
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        self.base_attack_bonus = self.level + dex_modifier
        
        # Recalculate ki pool
        self.max_ki = self._calculate_max_ki()
        
        # Update martial arts progression
        self.unarmed_damage_die = self._get_unarmed_damage_die()
        self.attacks_per_round = self._calculate_attacks_per_round()
        self.evasion_bonus = self._calculate_evasion_bonus()
        
        # Update spiritual resistance
        self.spiritual_resistance = self.get_spiritual_resistance()
        
        # Ensure current ki doesn't exceed max (if attributes exist)
        if hasattr(self, 'current_ki') and hasattr(self, 'max_ki'):
            if self.current_ki > self.max_ki:
                self.current_ki = self.max_ki
        
    # === KI POWER SYSTEM ===
    
    def _calculate_max_ki(self) -> int:
        """Calculate maximum ki points"""
        base_ki = 3
        wis_modifier = max(0, (self.stats['wisdom'] - 10) // 2)
        level_bonus = self.level // 2  # +1 ki per 2 levels
        return base_ki + wis_modifier + level_bonus
    
    def get_max_ki(self) -> int:
        """Get maximum ki points"""
        return self._calculate_max_ki()
    
    def spend_ki(self, amount: int) -> bool:
        """Spend ki points for abilities"""
        if self.current_ki < amount:
            return False
        self.current_ki -= amount
        return True
    
    def restore_ki(self, amount: int) -> int:
        """Restore ki points, return actual amount restored"""
        if self.current_ki >= self.max_ki:
            return 0
        old_ki = self.current_ki
        self.current_ki = min(self.max_ki, self.current_ki + amount)
        return self.current_ki - old_ki
    
    def use_ki_strike(self) -> bool:
        """Use ki strike for bonus damage (1 ki point)"""
        if self.spend_ki(1):
            return True
        return False
    
    def get_ki_strike_damage(self) -> str:
        """Get bonus damage from ki strike"""
        return "1d6"  # +1d6 damage from ki strike
    
    def use_ki_defense(self, rounds: int = 1) -> bool:
        """Use ki defense for AC bonus (1 ki point per round)"""
        if self.spend_ki(rounds):
            self.ki_defense_active = True
            self.ki_defense_duration = rounds
            return True
        return False
    
    def get_ki_defense_bonus(self) -> int:
        """Get AC bonus from ki defense"""
        if self.ki_defense_active:
            return 2  # +2 AC while ki defense is active
        return 0
    
    def can_ki_heal(self) -> bool:
        """Check if mystic can use ki healing"""
        return self.level >= 3
    
    def use_ki_healing(self, ki_spent: int) -> int:
        """Use ki for self-healing (1 ki = 1d4 healing)"""
        if not self.can_ki_heal() or not self.spend_ki(ki_spent):
            return 0
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            total_healing = 0
            for _ in range(ki_spent):
                total_healing += dice.roll("1d4")
            return self.heal(total_healing)
        except ImportError:
            import random
            total_healing = sum(random.randint(1, 4) for _ in range(ki_spent))
            return self.heal(total_healing)
    
    def can_ki_speed(self) -> bool:
        """Check if mystic can use ki speed"""
        return self.level >= 7
    
    def use_ki_speed(self) -> bool:
        """Use ki for enhanced movement (2 ki points)"""
        if self.can_ki_speed() and self.spend_ki(2):
            return True
        return False
    
    # === MARTIAL ARTS SYSTEM ===
    
    def _get_unarmed_damage_die(self) -> str:
        """Get unarmed damage die based on level"""
        if self.level >= 15:
            return "1d10"  # Master level
        elif self.level >= 10:
            return "1d8"   # Advanced
        elif self.level >= 5:
            return "1d6"   # Trained
        else:
            return "1d4"   # Novice
    
    def _calculate_attacks_per_round(self) -> int:
        """Calculate number of attacks per round"""
        base_attacks = 1
        if self.level >= 8:
            base_attacks = 2  # Extra attack at level 8
        if self.level >= 16:
            base_attacks = 3  # Second extra attack at level 16
        return base_attacks
    
    def get_attacks_per_round(self) -> int:
        """Get current attacks per round"""
        return self._calculate_attacks_per_round()
    
    def _calculate_evasion_bonus(self) -> int:
        """Calculate evasion training bonus"""
        base_bonus = 2
        level_bonus = self.level // 4  # +1 per 4 levels
        return base_bonus + level_bonus
    
    def get_evasion_bonus(self) -> int:
        """Get evasion training bonus"""
        return self._calculate_evasion_bonus()
    
    def get_evasion_chance(self) -> int:
        """Calculate total evasion chance percentage"""
        base_evasion = 15  # Base 15% evasion
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        wis_modifier = (self.stats['wisdom'] - 10) // 2
        evasion_bonus = self.get_evasion_bonus()
        
        # Add all bonuses
        total_evasion = base_evasion + dex_modifier + (wis_modifier // 2) + evasion_bonus
        
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
        """Get unarmed combat damage with bonuses"""
        base_damage = self.unarmed_damage_die
        
        # Add strength modifier and unarmed training bonus
        str_modifier = (self.stats['strength'] - 10) // 2
        unarmed_training = 1 + (self.level // 5)  # +1 per 5 levels
        total_bonus = str_modifier + unarmed_training
        
        if total_bonus > 0:
            return f"{base_damage}+{total_bonus}"
        elif total_bonus < 0:
            return f"{base_damage}{total_bonus}"
        else:
            return base_damage
    
    def can_deflect_missiles(self) -> bool:
        """Check if mystic can deflect projectiles"""
        return self.level >= 5
    
    def attempt_deflect_missile(self) -> bool:
        """Attempt to deflect a missile attack"""
        if not self.can_deflect_missiles():
            return False
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            deflect_roll = dice.roll("1d20") + self.get_evasion_bonus() + (self.stats['dexterity'] - 10) // 2
            return deflect_roll >= 15  # DC 15 to deflect
        except ImportError:
            import random
            deflect_roll = random.randint(1, 20) + self.get_evasion_bonus() + (self.stats['dexterity'] - 10) // 2
            return deflect_roll >= 15
    
    # === SPIRITUAL ABILITIES ===
    
    def get_spiritual_resistance(self) -> int:
        """Get resistance to mental/spiritual effects"""
        base_resistance = 2
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 4)  # Small WIS contribution
        level_bonus = self.level // 8  # +1 per 8 levels
        return base_resistance + wis_bonus + level_bonus
    
    def can_use_inner_focus(self) -> bool:
        """Check if mystic can use inner focus"""
        return self.level >= 4
    
    def use_inner_focus(self, duration_rounds: int = 3) -> bool:
        """Activate inner focus for concentration bonus"""
        if not self.can_use_inner_focus():
            return False
        
        self.inner_focus_duration = duration_rounds
        return True
    
    def get_inner_focus_bonus(self) -> int:
        """Get concentration bonus from inner focus"""
        if self.inner_focus_duration > 0:
            return 4  # +4 to concentration while focused
        return 0
    
    def can_detect_spiritual_auras(self) -> bool:
        """Check if mystic can detect spiritual auras"""
        return self.level >= 6
    
    def meditate(self) -> Dict[str, int]:
        """Enhanced meditation ability"""
        if self.meditation_uses <= 0:
            return {'error': 'No meditation uses remaining'}
            
        self.meditation_uses -= 1
        wis_modifier = (self.stats['wisdom'] - 10) // 2
        
        # Meditation restores HP, ki, and provides focus
        hp_restored = max(1, wis_modifier + (self.level // 3))
        ki_restored = max(1, (wis_modifier + 1) // 2)
        
        actual_hp = self.heal(hp_restored)
        actual_ki = self.restore_ki(ki_restored)
        
        # Activate inner focus as bonus
        if self.can_use_inner_focus():
            self.use_inner_focus(5)  # 5 rounds of focus
        
        return {
            'hp_restored': actual_hp,
            'ki_restored': actual_ki,
            'inner_focus_rounds': 5 if self.can_use_inner_focus() else 0,
            'remaining_uses': self.meditation_uses
        }
        
    def can_use_weapon(self, weapon) -> bool:
        """Check if mystic can use a specific weapon (simple weapons)"""
        if hasattr(weapon, 'weapon_type'):
            allowed_types = ['simple', 'staff', 'club', 'dagger', 'sling', 'dart']
            return weapon.weapon_type.lower() in allowed_types
        # Default allow for basic weapons
        return True
    
    def can_use_armor(self, armor) -> bool:
        """Check if mystic can use specific armor (light and medium)"""
        if hasattr(armor, 'armor_type'):
            return armor.armor_type.lower() in ['light', 'medium', 'leather', 'cloth', 'studded']
        return True  # Default allow for most armor
    
    def get_experience_penalty(self) -> int:
        """Mystics have +25% experience penalty (warrior-monk hybrid)"""
        return 25
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mystic':
        """Create Mystic from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        mystic = cls(data['character_name'], race_id, alignment)
        
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
        
        # Load alignment data
        if 'alignment_data' in data:
            mystic.load_alignment_data(data['alignment_data'])
        
        # Restore mystic-specific attributes
        mystic.max_ki = mystic._calculate_max_ki()
        mystic.current_ki = data.get('current_ki', mystic.max_ki)
        mystic.meditation_uses = data.get('meditation_uses', 3)
        mystic.ki_defense_active = data.get('ki_defense_active', False)
        mystic.ki_defense_duration = data.get('ki_defense_duration', 0)
        mystic.inner_focus_duration = data.get('inner_focus_duration', 0)
        
        # Recalculate derived attributes
        mystic.unarmed_damage_die = mystic._get_unarmed_damage_die()
        mystic.attacks_per_round = mystic._calculate_attacks_per_round()
        mystic.evasion_bonus = mystic._calculate_evasion_bonus()
        mystic.spiritual_resistance = mystic.get_spiritual_resistance()
        
        return mystic
        
    def to_dict(self) -> Dict[str, Any]:
        """Override to include mystic-specific state"""
        data = super().to_dict()
        data.update({
            'current_ki': self.current_ki,
            'meditation_uses': self.meditation_uses,
            'ki_defense_active': self.ki_defense_active,
            'ki_defense_duration': self.ki_defense_duration,
            'inner_focus_duration': self.inner_focus_duration
        })
        return data
    
    def __str__(self) -> str:
        """String representation of enhanced Mystic"""
        abilities = []
        
        # Ki status
        ki_status = f"Ki: {self.current_ki}/{self.max_ki}"
        abilities.append(ki_status)
        
        # Evasion chance
        evasion = self.get_evasion_chance()
        abilities.append(f"Evasion {evasion}%")
        
        # Unarmed damage
        unarmed_dmg = self.get_unarmed_damage()
        abilities.append(f"Unarmed {unarmed_dmg}")
        
        # Multiple attacks
        attacks = self.get_attacks_per_round()
        if attacks > 1:
            abilities.append(f"{attacks} Attacks")
        
        # Ki abilities
        ki_abilities = []
        if self.level >= 1:
            ki_abilities.append("Strike")
        if self.level >= 1:
            ki_abilities.append("Defense")
        if self.can_ki_heal():
            ki_abilities.append("Heal")
        if self.can_ki_speed():
            ki_abilities.append("Speed")
        
        if ki_abilities:
            abilities.append(f"Ki: {'/'.join(ki_abilities)}")
        
        # Active effects
        if self.ki_defense_active:
            abilities.append(f"Ki Defense ({self.ki_defense_duration})")
        if self.inner_focus_duration > 0:
            abilities.append(f"Focused ({self.inner_focus_duration})")
        
        # Meditation uses
        if self.meditation_uses > 0:
            abilities.append(f"Meditation ({self.meditation_uses})")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str