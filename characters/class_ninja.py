"""
Ninja Character Class for Rogue City
Traditional MajorMUD shadow warrior with eastern martial arts and death techniques.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Ninja(BaseCharacter):
    """
    Ninja class - Eastern shadow warrior with death techniques
    
    SHADOW WARRIOR - Expert progression, exotic abilities and high power
    
    Experience Penalty: +50% (exotic abilities and high power justify cost)
    Stat Modifiers: +3 DEX, +2 WIS, +1 CON, -2 STR, -2 INT, -1 CHA
    Hit Die: d6 (moderate HP, relies on not being hit)
    Attack Speed: 2.0 seconds (very fast attacks)
    Critical Range: 18-20 (improved critical chance with eastern weapons)
    
    EASTERN MARTIAL ARTS CORE:
    - Eastern weapon mastery (katana, sai, nunchaku, shuriken)
    - Shadow step teleportation through shadows
    - Death strike with chance for instant kill on critical hits
    - Smoke cloud creation for concealment and escape
    - Wall walking to move on vertical surfaces briefly
    - Pressure point attacks for stunning and paralysis effects
    
    NINJA ABILITIES:
    - Shadow Step: Teleport short distances through shadows
    - Death Strike: Chance for instant kill on critical hits
    - Smoke Cloud: Create concealing smoke for escape/ambush
    - Wall Walking: Move on walls and ceilings briefly
    - Pressure Points: Stunning and paralysis attacks
    - Meditation: Recover health and restore special abilities
    
    EQUIPMENT ACCESS:
    - Weapons: Eastern weapons (katana, sai, nunchaku), shuriken
    - Armor: Light armor and ninja garb for mobility
    - Magic: Can use subtle magical items that don't conflict with training
    - Accessories: Ninja tools, climbing gear, concealment items
    
    HONOR CODE:
    - Philosophy affects alignment choices and abilities
    - Dishonor can temporarily disable certain abilities
    - Code of conduct influences NPC reactions and quest availability
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Ninja character with shadow and martial arts systems"""
        super().__init__(name, 'ninja', race_id, alignment)
        
        # Shadow abilities
        self.shadow_step_uses_per_day = max(1, self.level // 2)
        self.shadow_step_uses_used = 0
        self.shadow_step_range = 30 + (self.level * 5)  # Feet
        self.shadow_mastery = self.level >= 21
        
        # Death strike system
        self.death_strike_chance = self._calculate_death_strike_chance()
        self.death_strike_damage_multiplier = self._calculate_death_strike_multiplier()
        self.assassinate_chance = max(1, self.level // 4)  # % chance
        
        # Smoke and concealment
        self.smoke_cloud_uses = max(1, self.level // 4)
        self.smoke_cloud_used = 0
        self.smoke_duration = 5 + self.level  # Rounds
        
        # Wall walking and mobility
        self.wall_walking_duration = max(1, self.level // 3)  # Rounds per use
        self.wall_walking_uses = max(1, self.level // 6)
        self.wall_walking_used = 0
        
        # Pressure points and stunning
        self.pressure_points_bonus = self._calculate_pressure_points()
        self.stunning_attacks = self.level >= 3
        self.paralysis_attacks = self.level >= 8
        
        # Meditation and recovery
        self.meditation_uses_per_day = max(1, self.level // 5)
        self.meditation_uses_used = 0
        self.meditation_healing = self.level * 2
        
        # Eastern weapon mastery
        self.eastern_weapon_bonus = self._calculate_eastern_weapon_bonus()
        self.dual_wield_eastern = self.level >= 6
        self.weapon_expertise = self.level >= 10
        
        # Honor code system
        self.honor_points = 100  # Start with perfect honor
        self.dishonor_penalty = 0
        self.honor_abilities_active = True
        
    def get_hit_die_value(self) -> int:
        """Ninjas use d6 hit die (moderate HP, avoid being hit)"""
        return 6
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d6"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            base_speed = self.equipment_system.get_attack_speed_modifier()
            # Ninjas attack faster with eastern weapons
            if self.is_using_eastern_weapon():
                return base_speed * 0.75  # 25% faster
            return base_speed
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Ninjas attack every 2 seconds unarmed (very fast)"""
        return 2.0
        
    def get_critical_range(self) -> int:
        """Ninjas crit on 18-20 with eastern weapons, 20 otherwise"""
        if self.is_using_eastern_weapon():
            return 18  # Improved crit with katana/eastern weapons
        return 20
        
    def get_experience_penalty(self) -> int:
        """Ninjas have +50% experience penalty"""
        return 50
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Ninja special abilities"""
        return {
            # Shadow abilities
            'shadow_step': self.get_shadow_step_remaining(),
            'shadow_step_range': self.shadow_step_range,
            'shadow_mastery': self.shadow_mastery,
            'unlimited_shadow_step': self.shadow_mastery,
            'shadow_concealment': True,
            
            # Death techniques
            'death_strike_chance': self.get_death_strike_chance(),
            'death_strike_multiplier': self.get_death_strike_multiplier(),
            'assassinate_chance': self.assassinate_chance,
            'killing_blow': self.level >= 15,
            'death_mastery': self.level >= 20,
            
            # Smoke and concealment
            'smoke_cloud': self.get_smoke_cloud_remaining(),
            'smoke_duration': self.smoke_duration,
            'improved_concealment': self.level >= 10,
            'vanish': self.level >= 12,
            
            # Mobility and acrobatics
            'wall_walking': self.get_wall_walking_remaining(),
            'wall_walking_duration': self.wall_walking_duration,
            'spider_climb': self.level >= 15,
            'ceiling_walking': self.level >= 18,
            'acrobatic_dodge': self.level >= 5,
            
            # Pressure points and stunning
            'pressure_points': self.get_pressure_points_bonus(),
            'stunning_attacks': self.stunning_attacks,
            'paralysis_attacks': self.paralysis_attacks,
            'nerve_strike': self.level >= 12,
            'death_touch': self.level >= 18,
            
            # Meditation and recovery
            'meditation': self.get_meditation_remaining(),
            'meditation_healing': self.meditation_healing,
            'inner_peace': self.level >= 8,
            'ki_restoration': self.level >= 14,
            
            # Eastern weapon mastery
            'eastern_weapon_mastery': self.get_eastern_weapon_bonus(),
            'dual_wield_eastern': self.dual_wield_eastern,
            'weapon_expertise': self.weapon_expertise,
            'perfect_balance': self.level >= 16,
            
            # Honor code system
            'honor_points': self.honor_points,
            'dishonor_penalty': self.dishonor_penalty,
            'honor_abilities': self.honor_abilities_active,
            'code_of_bushido': True,
            
            # Combat abilities
            'improved_critical': True,
            'critical_range': self.get_critical_range(),
            'multiple_attacks': self.level >= 11,
            'whirlwind_attack': self.level >= 16,
            
            # Equipment proficiencies
            'eastern_weapon_proficiency': True,
            'light_armor_proficiency': True,
            'ninja_tool_mastery': True,
            'shuriken_mastery': True
        }
    
    # === SHADOW ABILITIES ===
    
    def get_shadow_step_remaining(self) -> int:
        """Get shadow step uses remaining"""
        if self.shadow_mastery:
            return float('inf')  # Unlimited at level 21+
        return max(0, self.shadow_step_uses_per_day - self.shadow_step_uses_used)
    
    def can_shadow_step(self) -> bool:
        """Check if ninja can use shadow step"""
        if not self.honor_abilities_active:
            return False
        if self.shadow_mastery:
            return True
        return self.get_shadow_step_remaining() > 0
    
    def use_shadow_step(self, distance: int = None) -> Dict[str, Any]:
        """Use shadow step teleportation"""
        if not self.can_shadow_step():
            return {'success': False, 'reason': 'No shadow step uses remaining'}
        
        if distance is None:
            distance = self.shadow_step_range
        
        if distance > self.shadow_step_range:
            distance = self.shadow_step_range
        
        # Use charge unless unlimited
        if not self.shadow_mastery:
            self.shadow_step_uses_used += 1
        
        return {
            'success': True,
            'distance': distance,
            'max_range': self.shadow_step_range,
            'stealth_bonus': 4,  # +4 to hide after shadow step
            'surprise_round': True,  # Can attack immediately
            'remaining_uses': self.get_shadow_step_remaining()
        }
    
    def shadow_concealment(self) -> Dict[str, Any]:
        """Use shadows for concealment"""
        if not self.honor_abilities_active:
            return {'success': False, 'reason': 'Honor abilities disabled'}
        
        stealth_bonus = 6 + (self.level // 3)
        return {
            'success': True,
            'stealth_bonus': stealth_bonus,
            'duration': 'until broken',
            'shadows_required': True
        }
    
    # === DEATH STRIKE ABILITIES ===
    
    def _calculate_death_strike_chance(self) -> int:
        """Calculate death strike chance percentage"""
        base_chance = 5  # 5% at level 1
        level_bonus = (self.level - 1) // 2  # +1% every 2 levels
        return min(base_chance + level_bonus, 15)  # Max 15% at level 21+
    
    def get_death_strike_chance(self) -> int:
        """Get death strike chance percentage"""
        if not self.honor_abilities_active:
            return max(1, self._calculate_death_strike_chance() // 2)
        return self._calculate_death_strike_chance()
    
    def _calculate_death_strike_multiplier(self) -> float:
        """Calculate death strike damage multiplier"""
        base_multiplier = 3.0
        if self.level >= 10:
            base_multiplier = 4.0
        if self.level >= 20:
            base_multiplier = 5.0
        return base_multiplier
    
    def get_death_strike_multiplier(self) -> float:
        """Get death strike damage multiplier"""
        return self._calculate_death_strike_multiplier()
    
    def attempt_death_strike(self, attack_roll: int, target_level: int = 1) -> Dict[str, Any]:
        """Attempt death strike on critical hit"""
        if attack_roll < self.get_critical_range():
            return {'death_strike': False, 'reason': 'Not a critical hit'}
        
        if not self.honor_abilities_active:
            return {'death_strike': False, 'reason': 'Honor abilities disabled'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            death_roll = dice.roll("1d100")
            success = death_roll <= self.get_death_strike_chance()
            
            # Instant kill on very high levels is harder
            if target_level > self.level + 5:
                success = False
            
            return {
                'death_strike': success,
                'death_roll': death_roll,
                'death_chance': self.get_death_strike_chance(),
                'damage_multiplier': self.get_death_strike_multiplier(),
                'instant_kill': success and self.level >= 15
            }
        except ImportError:
            import random
            success = random.randint(1, 100) <= self.get_death_strike_chance()
            return {
                'death_strike': success,
                'damage_multiplier': self.get_death_strike_multiplier(),
                'instant_kill': success and self.level >= 15
            }
    
    def can_assassinate(self) -> bool:
        """Check if ninja can attempt assassination"""
        return self.level >= 10 and self.honor_abilities_active
    
    def attempt_assassination(self, target_surprised: bool = False) -> Dict[str, Any]:
        """Attempt assassination attack"""
        if not self.can_assassinate():
            return {'success': False, 'reason': 'Assassination not available'}
        
        if not target_surprised:
            return {'success': False, 'reason': 'Target must be surprised'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            assassinate_roll = dice.roll("1d100")
            success = assassinate_roll <= self.assassinate_chance
            
            return {
                'success': success,
                'assassinate_roll': assassinate_roll,
                'assassinate_chance': self.assassinate_chance,
                'instant_kill': success,
                'massive_damage': not success  # Still does huge damage if fails
            }
        except ImportError:
            import random
            success = random.randint(1, 100) <= self.assassinate_chance
            return {'success': success, 'instant_kill': success}
    
    # === SMOKE AND CONCEALMENT ===
    
    def get_smoke_cloud_remaining(self) -> int:
        """Get smoke cloud uses remaining"""
        return max(0, self.smoke_cloud_uses - self.smoke_cloud_used)
    
    def can_use_smoke_cloud(self) -> bool:
        """Check if ninja can create smoke cloud"""
        return self.get_smoke_cloud_remaining() > 0 and self.honor_abilities_active
    
    def create_smoke_cloud(self) -> Dict[str, Any]:
        """Create concealing smoke cloud"""
        if not self.can_use_smoke_cloud():
            return {'success': False, 'reason': 'No smoke cloud uses remaining'}
        
        self.smoke_cloud_used += 1
        
        return {
            'success': True,
            'duration_rounds': self.smoke_duration,
            'area_radius': 15 + self.level,  # Feet
            'concealment': 'total',
            'escape_bonus': 8,
            'remaining_uses': self.get_smoke_cloud_remaining()
        }
    
    def can_vanish(self) -> bool:
        """Check if ninja can vanish from combat"""
        return self.level >= 12 and self.honor_abilities_active
    
    def vanish_from_combat(self) -> Dict[str, Any]:
        """Vanish from combat using advanced techniques"""
        if not self.can_vanish():
            return {'success': False, 'reason': 'Vanish not available'}
        
        # Costs smoke cloud use
        if not self.can_use_smoke_cloud():
            return {'success': False, 'reason': 'No smoke available'}
        
        self.smoke_cloud_used += 1
        
        return {
            'success': True,
            'instant_concealment': True,
            'combat_escape': True,
            'stealth_bonus': 10,
            'remaining_uses': self.get_smoke_cloud_remaining()
        }
    
    # === WALL WALKING AND MOBILITY ===
    
    def get_wall_walking_remaining(self) -> int:
        """Get wall walking uses remaining"""
        return max(0, self.wall_walking_uses - self.wall_walking_used)
    
    def can_wall_walk(self) -> bool:
        """Check if ninja can walk on walls"""
        return self.get_wall_walking_remaining() > 0 and self.honor_abilities_active
    
    def activate_wall_walking(self) -> Dict[str, Any]:
        """Activate wall walking ability"""
        if not self.can_wall_walk():
            return {'success': False, 'reason': 'No wall walking uses remaining'}
        
        self.wall_walking_used += 1
        
        abilities = ['walls', 'ceilings'] if self.level >= 18 else ['walls']
        if self.level >= 15:
            abilities.append('spider_climb')
        
        return {
            'success': True,
            'duration_rounds': self.wall_walking_duration,
            'surfaces': abilities,
            'movement_rate': 'normal' if self.level >= 15 else 'half',
            'remaining_uses': self.get_wall_walking_remaining()
        }
    
    def acrobatic_dodge(self) -> int:
        """Get acrobatic dodge AC bonus"""
        if not self.honor_abilities_active or self.level < 5:
            return 0
        
        base_bonus = 1
        level_bonus = self.level // 5
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 4)
        return base_bonus + level_bonus + dex_bonus
    
    # === PRESSURE POINTS AND STUNNING ===
    
    def _calculate_pressure_points(self) -> int:
        """Calculate pressure points attack bonus"""
        base_bonus = 2
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        level_bonus = self.level // 3
        return base_bonus + wis_bonus + level_bonus
    
    def get_pressure_points_bonus(self) -> int:
        """Get pressure points attack bonus"""
        if not self.honor_abilities_active:
            return max(1, self._calculate_pressure_points() // 2)
        return self._calculate_pressure_points()
    
    def attempt_stunning_attack(self, target_level: int = 1) -> Dict[str, Any]:
        """Attempt to stun target with pressure points"""
        if not self.stunning_attacks or not self.honor_abilities_active:
            return {'success': False, 'reason': 'Stunning attacks not available'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            stun_roll = dice.roll("1d20") + self.get_pressure_points_bonus()
            dc = 15 + target_level
            success = stun_roll >= dc
            
            return {
                'success': success,
                'stun_roll': stun_roll,
                'dc': dc,
                'duration_rounds': 2 + (self.level // 5),
                'effect': 'stunned'
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_pressure_points_bonus() >= (15 + target_level)
            return {'success': success, 'effect': 'stunned'}
    
    def attempt_paralysis_attack(self, target_level: int = 1) -> Dict[str, Any]:
        """Attempt to paralyze target with advanced pressure points"""
        if not self.paralysis_attacks or not self.honor_abilities_active:
            return {'success': False, 'reason': 'Paralysis attacks not available'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            paralysis_roll = dice.roll("1d20") + self.get_pressure_points_bonus()
            dc = 18 + target_level  # Harder than stunning
            success = paralysis_roll >= dc
            
            return {
                'success': success,
                'paralysis_roll': paralysis_roll,
                'dc': dc,
                'duration_rounds': 1 + (self.level // 8),
                'effect': 'paralyzed'
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_pressure_points_bonus() >= (18 + target_level)
            return {'success': success, 'effect': 'paralyzed'}
    
    def can_death_touch(self) -> bool:
        """Check if ninja can use death touch"""
        return self.level >= 18 and self.honor_abilities_active
    
    def attempt_death_touch(self, target_level: int = 1) -> Dict[str, Any]:
        """Attempt death touch attack"""
        if not self.can_death_touch():
            return {'success': False, 'reason': 'Death touch not available'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            death_touch_roll = dice.roll("1d20") + self.get_pressure_points_bonus()
            dc = 25 + target_level  # Very difficult
            success = death_touch_roll >= dc
            
            return {
                'success': success,
                'death_touch_roll': death_touch_roll,
                'dc': dc,
                'instant_death': success,
                'massive_damage': not success  # Heavy damage if fails
            }
        except ImportError:
            import random  
            success = random.randint(1, 20) + self.get_pressure_points_bonus() >= (25 + target_level)
            return {'success': success, 'instant_death': success}
    
    # === MEDITATION AND RECOVERY ===
    
    def get_meditation_remaining(self) -> int:
        """Get meditation uses remaining"""
        return max(0, self.meditation_uses_per_day - self.meditation_uses_used)
    
    def can_meditate(self) -> bool:
        """Check if ninja can meditate"""
        return self.get_meditation_remaining() > 0 and self.honor_abilities_active
    
    def meditate(self) -> Dict[str, Any]:
        """Meditate to recover health and abilities"""
        if not self.can_meditate():
            return {'success': False, 'reason': 'No meditation uses remaining'}
        
        self.meditation_uses_used += 1
        
        # Heal HP
        healing_done = self.heal(self.meditation_healing)
        
        # Restore some abilities
        abilities_restored = []
        if self.level >= 8:  # Inner peace
            self.shadow_step_uses_used = max(0, self.shadow_step_uses_used - 1)
            abilities_restored.append('shadow_step')
        
        if self.level >= 14:  # Ki restoration
            self.smoke_cloud_used = max(0, self.smoke_cloud_used - 1)
            self.wall_walking_used = max(0, self.wall_walking_used - 1)
            abilities_restored.extend(['smoke_cloud', 'wall_walking'])
        
        return {
            'success': True,
            'healing_done': healing_done,
            'abilities_restored': abilities_restored,
            'duration_minutes': 10,
            'remaining_uses': self.get_meditation_remaining()
        }
    
    # === EASTERN WEAPON MASTERY ===
    
    def _calculate_eastern_weapon_bonus(self) -> int:
        """Calculate eastern weapon mastery bonus"""
        base_bonus = 2
        level_bonus = self.level // 3
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 4)
        return base_bonus + level_bonus + dex_bonus
    
    def get_eastern_weapon_bonus(self) -> int:
        """Get eastern weapon mastery bonus"""
        if not self.honor_abilities_active:
            return max(1, self._calculate_eastern_weapon_bonus() // 2)
        return self._calculate_eastern_weapon_bonus()
    
    def is_using_eastern_weapon(self) -> bool:
        """Check if ninja is using eastern weapons"""
        # This would check equipped weapons in a full implementation
        return True  # Placeholder
    
    def get_eastern_weapon_damage_bonus(self, weapon_type: str = None) -> int:
        """Get damage bonus with eastern weapons"""
        if not self.is_using_eastern_weapon():
            return 0
        
        base_bonus = self.get_eastern_weapon_bonus()
        
        # Weapon-specific bonuses
        weapon_bonuses = {
            'katana': 2,     # +2 extra with katana
            'sai': 1,        # +1 extra with sai
            'nunchaku': 1,   # +1 extra with nunchaku
            'shuriken': 0    # No extra bonus
        }
        
        weapon_bonus = weapon_bonuses.get(weapon_type, 0)
        return base_bonus + weapon_bonus
    
    def can_dual_wield_eastern(self) -> bool:
        """Check if ninja can dual-wield eastern weapons"""
        return self.dual_wield_eastern and self.honor_abilities_active
    
    def get_dual_wield_penalty_reduction(self) -> int:
        """Get dual-wield penalty reduction with eastern weapons"""
        if not self.can_dual_wield_eastern():
            return 0
        
        base_reduction = 4  # Better than normal dual-wield
        level_bonus = self.level // 4
        return base_reduction + level_bonus
    
    # === HONOR CODE SYSTEM ===
    
    def modify_honor(self, change: int, reason: str = "") -> Dict[str, Any]:
        """Modify honor points"""
        old_honor = self.honor_points
        self.honor_points = max(0, min(100, self.honor_points + change))
        
        # Update dishonor penalty
        if self.honor_points < 50:
            self.dishonor_penalty = (50 - self.honor_points) // 10
            self.honor_abilities_active = self.honor_points >= 25
        else:
            self.dishonor_penalty = 0
            self.honor_abilities_active = True
        
        return {
            'old_honor': old_honor,
            'new_honor': self.honor_points,
            'change': change,
            'reason': reason,
            'dishonor_penalty': self.dishonor_penalty,
            'abilities_active': self.honor_abilities_active
        }
    
    def get_honor_status(self) -> str:
        """Get honor status description"""
        if self.honor_points >= 80:
            return "Honorable"
        elif self.honor_points >= 60:
            return "Respectable"
        elif self.honor_points >= 40:
            return "Neutral"
        elif self.honor_points >= 25:
            return "Dishonorable"
        else:
            return "Fallen Ninja"
    
    def check_honorable_action(self, action: str) -> int:
        """Check if action is honorable and return honor change"""
        honorable_actions = {
            'protect_innocent': +5,
            'keep_word': +3,
            'show_mercy': +2,
            'defend_weak': +4,
            'respect_elders': +1
        }
        
        dishonorable_actions = {
            'attack_innocent': -10,
            'break_word': -8,
            'flee_combat': -5,
            'use_poison': -6,
            'dishonest_dealing': -4
        }
        
        if action in honorable_actions:
            return honorable_actions[action]
        elif action in dishonorable_actions:
            return dishonorable_actions[action]
        return 0
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Ninjas prefer eastern weapons but can use most light weapons"""
        if hasattr(weapon, 'weapon_category'):
            return weapon.weapon_category.lower() in ['light', 'eastern', 'simple']
        if hasattr(weapon, 'weapon_type'):
            preferred_types = ['katana', 'sai', 'nunchaku', 'shuriken', 'dagger', 'short_sword']
            return weapon.weapon_type.lower() in preferred_types
        return True  # Default allow for basic weapons
    
    def can_use_armor(self, armor) -> bool:
        """Ninjas can only use light armor for mobility"""
        if hasattr(armor, 'armor_type'):
            allowed_types = ['light', 'leather', 'cloth', 'ninja_garb', 'padded']
            return armor.armor_type.lower() in allowed_types
        return True  # Default allow for basic armor
    
    def calculate_derived_stats(self):
        """Override to include acrobatic dodge and dishonor penalties"""
        super().calculate_derived_stats()
        
        # Add acrobatic dodge AC bonus
        self.armor_class += self.acrobatic_dodge()
        
        # Apply dishonor penalties
        if self.dishonor_penalty > 0:
            self.base_attack_bonus -= self.dishonor_penalty
            # Don't let attack bonus go negative
            self.base_attack_bonus = max(1, self.base_attack_bonus)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ninja':
        """Create Ninja from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        ninja = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        ninja.level = data['level']
        ninja.experience = data['experience']
        ninja.base_stats = data.get('base_stats', ninja.base_stats)
        ninja.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        ninja.max_hp = derived['max_hp']
        ninja.current_hp = derived['current_hp']
        ninja.armor_class = derived['armor_class']
        ninja.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        ninja.current_area = location.get('area_id')
        ninja.current_room = location.get('room_id')
        
        # Initialize item systems
        ninja.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            ninja.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            ninja.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        ninja.unallocated_stats = data.get('unallocated_stats', 0)
        ninja.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            ninja.load_alignment_data(data['alignment_data'])
        
        # Load currency data
        if 'currency_data' in data:
            ninja.load_currency_data(data['currency_data'])
        
        # Restore ninja-specific attributes
        ninja_data = data.get('ninja_data', {})
        ninja.shadow_step_uses_used = ninja_data.get('shadow_step_uses_used', 0)
        ninja.smoke_cloud_used = ninja_data.get('smoke_cloud_used', 0)
        ninja.wall_walking_used = ninja_data.get('wall_walking_used', 0)
        ninja.meditation_uses_used = ninja_data.get('meditation_uses_used', 0)
        ninja.honor_points = ninja_data.get('honor_points', 100)
        
        # Recalculate ninja-specific attributes
        ninja.shadow_step_uses_per_day = max(1, ninja.level // 2)
        ninja.shadow_step_range = 30 + (ninja.level * 5)
        ninja.shadow_mastery = ninja.level >= 21
        ninja.death_strike_chance = ninja._calculate_death_strike_chance()
        ninja.death_strike_damage_multiplier = ninja._calculate_death_strike_multiplier()
        ninja.assassinate_chance = max(1, ninja.level // 4)
        ninja.smoke_cloud_uses = max(1, ninja.level // 4)
        ninja.smoke_duration = 5 + ninja.level
        ninja.wall_walking_duration = max(1, ninja.level // 3)
        ninja.wall_walking_uses = max(1, ninja.level // 6)
        ninja.pressure_points_bonus = ninja._calculate_pressure_points()
        ninja.stunning_attacks = ninja.level >= 3
        ninja.paralysis_attacks = ninja.level >= 8
        ninja.meditation_uses_per_day = max(1, ninja.level // 5)
        ninja.meditation_healing = ninja.level * 2
        ninja.eastern_weapon_bonus = ninja._calculate_eastern_weapon_bonus()
        ninja.dual_wield_eastern = ninja.level >= 6
        ninja.weapon_expertise = ninja.level >= 10
        
        # Update honor system
        if ninja.honor_points < 50:
            ninja.dishonor_penalty = (50 - ninja.honor_points) // 10
            ninja.honor_abilities_active = ninja.honor_points >= 25
        else:
            ninja.dishonor_penalty = 0
            ninja.honor_abilities_active = True
        
        return ninja
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include ninja-specific data"""
        data = super().to_dict()
        data['ninja_data'] = {
            'shadow_step_uses_used': self.shadow_step_uses_used,
            'smoke_cloud_used': self.smoke_cloud_used,
            'wall_walking_used': self.wall_walking_used,
            'meditation_uses_used': self.meditation_uses_used,
            'honor_points': self.honor_points
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Ninja"""
        abilities = []
        
        # Honor status
        honor_status = self.get_honor_status()
        if self.honor_points < 50:
            abilities.append(f"{honor_status}")
        
        # Shadow step
        shadow_steps = self.get_shadow_step_remaining()
        if self.shadow_mastery:
            abilities.append("Unlimited Shadows")
        elif shadow_steps > 0:
            abilities.append(f"Shadow {shadow_steps}")
        
        # Death strike
        death_chance = self.get_death_strike_chance()
        abilities.append(f"Death {death_chance}%")
        
        # Smoke cloud
        smoke_remaining = self.get_smoke_cloud_remaining()
        if smoke_remaining > 0:
            abilities.append(f"Smoke {smoke_remaining}")
        
        # Wall walking
        wall_remaining = self.get_wall_walking_remaining()
        if wall_remaining > 0:
            abilities.append(f"Wall {wall_remaining}")
        
        # Meditation
        meditation_remaining = self.get_meditation_remaining()
        if meditation_remaining > 0:
            abilities.append(f"Meditate {meditation_remaining}")
        
        # High-level abilities
        if self.can_assassinate():
            abilities.append(f"Assassinate {self.assassinate_chance}%")
        if self.can_vanish():
            abilities.append("Vanish")
        if self.can_death_touch():
            abilities.append("Death Touch")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str