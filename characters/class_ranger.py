"""
Ranger Character Class for Rogue City
Traditional MajorMUD nature warrior with dual-wield mastery and wilderness skills.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Ranger(BaseCharacter):
    """
    Ranger class - Nature warrior with dual-wield and nature magic
    
    WILDERNESS WARRIOR - Slow progression, combat + magic + skills
    
    Experience Penalty: +30% (combat + magic + skills = complex class)
    Stat Modifiers: +2 DEX, +2 WIS, +1 CON, -2 INT, -1 CHA
    Hit Die: d8 (good HP progression)
    Attack Speed: 2.5 seconds (fast with dual weapons)
    Critical Range: 20 (standard critical chance)
    
    WILDERNESS MASTERY CORE:
    - Dual-wield mastery for fighting with two weapons efficiently
    - Tracking ability to follow creature trails and signs
    - Animal empathy to communicate with and befriend animals
    - Favored enemy system with bonus damage against chosen types
    - Wilderness survival to navigate and thrive in natural environments
    - Nature magic with limited druidic spells for healing and utility
    
    RANGER ABILITIES:
    - Dual-Wield Mastery: Fight efficiently with two weapons
    - Tracking: Follow creature trails and signs
    - Animal Empathy: Communicate with and befriend animals
    - Favored Enemy: Bonus damage against chosen creature types
    - Wilderness Survival: Navigate and thrive in natural environments
    - Nature Magic: Limited druidic spells (healing, animal friendship)
    
    EQUIPMENT ACCESS:
    - Weapons: Light and medium weapons, dual-wield specialization
    - Armor: Light and medium armor for mobility
    - Magic: Can use nature-based magical items
    - Accessories: Survival gear, animal handling items
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Ranger character with wilderness and dual-wield systems"""
        super().__init__(name, 'ranger', race_id, alignment)
        
        # Dual-wield combat attributes
        self.dual_wield_penalty_reduction = self._calculate_dual_wield_reduction()
        self.two_weapon_fighting = True
        self.improved_two_weapon = self.level >= 6
        self.greater_two_weapon = self.level >= 11
        
        # Tracking and wilderness attributes
        self.tracking_bonus = self._calculate_tracking_bonus()
        self.survival_bonus = self._calculate_survival_bonus()
        self.hide_in_wilderness = self._calculate_wilderness_stealth()
        
        # Animal empathy system
        self.animal_empathy_bonus = self._calculate_animal_empathy()
        self.animal_companion = None  # Set when companion is gained
        self.animal_companion_level = max(1, self.level // 4)
        
        # Favored enemy system
        self.favored_enemies = self._get_starting_favored_enemies()
        self.favored_enemy_bonus = self._calculate_favored_enemy_bonus()
        
        # Nature magic system
        self.nature_magic_level = max(1, self.level // 2)  # Half level for spells
        self.nature_spells_per_day = self._calculate_nature_spells()
        self.nature_spells_used = {}  # Track by spell level
        
        # Wilderness abilities
        self.camouflage_bonus = self._calculate_camouflage()
        self.endurance_bonus = self._calculate_endurance()
        self.resist_environmental = self.level >= 4
        
    def get_hit_die_value(self) -> int:
        """Rangers use d8 hit die (good HP progression)"""
        return 8
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d8"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering dual-wield)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            base_speed = self.equipment_system.get_attack_speed_modifier()
            # Rangers attack faster when dual-wielding
            if self.is_dual_wielding():
                return base_speed * 0.85  # 15% faster
            return base_speed
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Rangers attack every 2.5 seconds unarmed (fast for dual-wield)"""
        return 2.5
        
    def get_critical_range(self) -> int:
        """Rangers crit on natural 20 (standard critical)"""
        return 20
        
    def get_experience_penalty(self) -> int:
        """Rangers have +30% experience penalty"""
        return 30
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Ranger special abilities"""
        return {
            # Dual-wield combat
            'dual_wield_mastery': True,
            'dual_wield_penalty_reduction': self.get_dual_wield_reduction(),
            'two_weapon_fighting': self.two_weapon_fighting,
            'improved_two_weapon': self.improved_two_weapon,
            'greater_two_weapon': self.greater_two_weapon,
            'ambidextrous': self.level >= 8,
            
            # Tracking and wilderness
            'tracking': self.get_tracking_bonus(),
            'wilderness_survival': self.get_survival_bonus(),
            'hide_in_wilderness': self.get_wilderness_stealth(),
            'move_silently_wilderness': self.get_wilderness_stealth(),
            'camouflage': self.get_camouflage_bonus(),
            'endurance': self.get_endurance_bonus(),
            
            # Animal abilities
            'animal_empathy': self.get_animal_empathy_bonus(),
            'animal_companion': self.animal_companion is not None,
            'companion_level': self.animal_companion_level,
            'speak_with_animals': self.level >= 4,
            'animal_friendship': self.level >= 2,
            
            # Favored enemy system
            'favored_enemies': self.favored_enemies.copy(),
            'favored_enemy_bonus': self.get_favored_enemy_bonus(),
            'instant_enemy': self.level >= 10,
            
            # Nature magic
            'nature_magic_level': self.nature_magic_level,
            'nature_spells_per_day': self.get_nature_spells_per_day(),
            'cure_light_wounds': self.nature_magic_level >= 1,
            'detect_animals': self.nature_magic_level >= 1,
            'entangle': self.nature_magic_level >= 2,
            'barkskin': self.nature_magic_level >= 2,
            'cure_moderate_wounds': self.nature_magic_level >= 3,
            'plant_growth': self.nature_magic_level >= 3,
            
            # Environmental resistance
            'resist_environmental': self.resist_environmental,
            'woodland_stride': self.level >= 3,
            'trackless_step': self.level >= 7,
            'swift_tracker': self.level >= 8,
            
            # Equipment proficiencies
            'simple_weapon_proficiency': True,
            'martial_weapon_proficiency': True,
            'light_armor_proficiency': True,
            'medium_armor_proficiency': True,
            'shield_proficiency': self.level >= 5
        }
    
    # === DUAL-WIELD COMBAT ABILITIES ===
    
    def _calculate_dual_wield_reduction(self) -> int:
        """Calculate dual-wield penalty reduction"""
        base_reduction = 3  # -3 to dual-wield penalties
        level_bonus = self.level // 3  # Additional reduction every 3 levels
        return base_reduction + level_bonus
    
    def get_dual_wield_reduction(self) -> int:
        """Get dual-wield penalty reduction"""
        return self._calculate_dual_wield_reduction()
    
    def is_dual_wielding(self) -> bool:
        """Check if ranger is currently dual-wielding"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.is_dual_wielding()
        return False
    
    def get_dual_wield_attacks(self) -> int:
        """Get number of attacks when dual-wielding"""
        base_attacks = 1  # Primary hand
        
        # Off-hand attacks
        if self.two_weapon_fighting:
            base_attacks += 1  # One off-hand attack
        if self.improved_two_weapon and self.level >= 6:
            base_attacks += 1  # Second off-hand attack
        if self.greater_two_weapon and self.level >= 11:
            base_attacks += 1  # Third off-hand attack
            
        return base_attacks
    
    def get_dual_wield_penalties(self) -> Dict[str, int]:
        """Get attack penalties when dual-wielding"""
        if not self.is_dual_wielding():
            return {'primary': 0, 'off_hand': 0}
        
        # Base penalties
        primary_penalty = -6
        off_hand_penalty = -10
        
        # Apply ranger dual-wield mastery
        reduction = self.get_dual_wield_reduction()
        primary_penalty += reduction
        off_hand_penalty += reduction
        
        # Two-weapon fighting feat reductions
        if self.two_weapon_fighting:
            primary_penalty += 2  # -6 becomes -4
            off_hand_penalty += 2  # -10 becomes -8
        
        return {
            'primary': max(0, primary_penalty),  # Don't go below 0
            'off_hand': max(0, off_hand_penalty)
        }
    
    # === TRACKING AND WILDERNESS ABILITIES ===
    
    def _calculate_tracking_bonus(self) -> int:
        """Calculate tracking skill bonus"""
        base_bonus = 3
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        level_bonus = self.level
        return base_bonus + wis_bonus + level_bonus
    
    def get_tracking_bonus(self) -> int:
        """Get tracking skill bonus"""
        return self._calculate_tracking_bonus()
    
    def _calculate_survival_bonus(self) -> int:
        """Calculate wilderness survival bonus"""
        base_bonus = 2
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        con_bonus = max(0, (self.stats['constitution'] - 10) // 4)
        level_bonus = self.level // 2
        return base_bonus + wis_bonus + con_bonus + level_bonus
    
    def get_survival_bonus(self) -> int:
        """Get wilderness survival bonus"""
        return self._calculate_survival_bonus()
    
    def _calculate_wilderness_stealth(self) -> int:
        """Calculate stealth bonus in wilderness"""
        base_bonus = 4
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 4)
        level_bonus = self.level // 3
        return base_bonus + dex_bonus + wis_bonus + level_bonus
    
    def get_wilderness_stealth(self) -> int:
        """Get stealth bonus in wilderness"""
        return self._calculate_wilderness_stealth()
    
    def attempt_tracking(self, difficulty: int = 15, terrain_modifier: int = 0) -> Dict[str, Any]:
        """Attempt to track creatures"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            tracking_roll = dice.roll("1d20") + self.get_tracking_bonus() - terrain_modifier
            success = tracking_roll >= difficulty
            
            return {
                'success': success,
                'tracking_roll': tracking_roll,
                'difficulty': difficulty,
                'terrain_modifier': terrain_modifier,
                'trail_quality': 'clear' if success else 'lost'
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_tracking_bonus() - terrain_modifier >= difficulty
            return {'success': success, 'trail_quality': 'clear' if success else 'lost'}
    
    def can_swift_track(self) -> bool:
        """Check if ranger can track at full speed"""
        return self.level >= 8
    
    def leaves_no_trail(self) -> bool:
        """Check if ranger leaves no trail (trackless step)"""
        return self.level >= 7
    
    # === ANIMAL EMPATHY ABILITIES ===
    
    def _calculate_animal_empathy(self) -> int:
        """Calculate animal empathy bonus"""
        base_bonus = 3
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 4)
        level_bonus = self.level // 2
        return base_bonus + wis_bonus + cha_bonus + level_bonus
    
    def get_animal_empathy_bonus(self) -> int:
        """Get animal empathy bonus"""
        return self._calculate_animal_empathy()
    
    def attempt_animal_empathy(self, animal_hd: int = 1) -> Dict[str, Any]:
        """Attempt to befriend an animal"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            empathy_roll = dice.roll("1d20") + self.get_animal_empathy_bonus()
            dc = 10 + animal_hd
            success = empathy_roll >= dc
            
            return {
                'success': success,
                'empathy_roll': empathy_roll,
                'difficulty': dc,
                'animal_reaction': 'friendly' if success else 'neutral'
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_animal_empathy_bonus() >= (10 + animal_hd)
            return {'success': success, 'animal_reaction': 'friendly' if success else 'neutral'}
    
    def can_gain_animal_companion(self) -> bool:
        """Check if ranger can gain animal companion"""
        return self.level >= 4 and self.animal_companion is None
    
    def gain_animal_companion(self, companion_type: str = "wolf") -> Dict[str, Any]:
        """Gain an animal companion"""
        if not self.can_gain_animal_companion():
            return {'success': False, 'reason': 'Cannot gain companion at this time'}
        
        valid_companions = ['wolf', 'hawk', 'bear', 'panther', 'horse', 'eagle']
        if companion_type not in valid_companions:
            companion_type = 'wolf'
        
        self.animal_companion = companion_type
        self.animal_companion_level = max(1, self.level // 4)
        
        return {
            'success': True,
            'companion_type': companion_type,
            'companion_level': self.animal_companion_level,
            'bond_strength': 'strong'
        }
    
    def can_speak_with_animals(self) -> bool:
        """Check if ranger can speak with animals"""
        return self.level >= 4
    
    # === FAVORED ENEMY SYSTEM ===
    
    def _get_starting_favored_enemies(self) -> List[str]:
        """Get starting favored enemies"""
        return ['humanoid']  # Start with humanoid as first favored enemy
    
    def _calculate_favored_enemy_bonus(self) -> int:
        """Calculate favored enemy bonus"""
        base_bonus = 2
        additional_bonuses = (len(self.favored_enemies) - 1) * 1
        level_bonus = (self.level - 1) // 5  # +1 every 5 levels
        return base_bonus + additional_bonuses + level_bonus
    
    def get_favored_enemy_bonus(self) -> int:
        """Get favored enemy bonus"""
        return self._calculate_favored_enemy_bonus()
    
    def can_add_favored_enemy(self) -> bool:
        """Check if ranger can add new favored enemy"""
        max_enemies = 1 + (self.level - 1) // 5  # 1 at level 1, +1 every 5 levels
        return len(self.favored_enemies) < max_enemies
    
    def add_favored_enemy(self, enemy_type: str) -> bool:
        """Add new favored enemy type"""
        if not self.can_add_favored_enemy():
            return False
        
        valid_types = ['humanoid', 'beast', 'undead', 'dragon', 'giant', 'outsider', 'aberration']
        if enemy_type.lower() in valid_types and enemy_type not in self.favored_enemies:
            self.favored_enemies.append(enemy_type.lower())
            return True
        return False
    
    def get_attack_bonus_vs_favored(self, enemy_type: str) -> int:
        """Get attack bonus against favored enemy"""
        if enemy_type.lower() in self.favored_enemies:
            return self.get_favored_enemy_bonus()
        return 0
    
    def get_damage_bonus_vs_favored(self, enemy_type: str) -> int:
        """Get damage bonus against favored enemy"""
        if enemy_type.lower() in self.favored_enemies:
            return self.get_favored_enemy_bonus()
        return 0
    
    def can_use_instant_enemy(self) -> bool:
        """Check if ranger can designate instant enemy"""
        return self.level >= 10
    
    # === NATURE MAGIC ABILITIES ===
    
    def _calculate_nature_spells(self) -> Dict[int, int]:
        """Calculate nature spells per day by level"""
        if self.nature_magic_level < 1:
            return {}
        
        spells_per_day = {}
        
        # Level 1 spells
        if self.nature_magic_level >= 1:
            spells_per_day[1] = 1 + max(0, (self.stats['wisdom'] - 10) // 2)
        
        # Level 2 spells
        if self.nature_magic_level >= 3:
            spells_per_day[2] = 1 + max(0, (self.stats['wisdom'] - 12) // 2)
        
        # Level 3 spells
        if self.nature_magic_level >= 5:
            spells_per_day[3] = 1 + max(0, (self.stats['wisdom'] - 14) // 2)
        
        # Level 4 spells
        if self.nature_magic_level >= 7:
            spells_per_day[4] = 1 + max(0, (self.stats['wisdom'] - 16) // 2)
        
        return spells_per_day
    
    def get_nature_spells_per_day(self) -> Dict[int, int]:
        """Get nature spells per day"""
        return self._calculate_nature_spells()
    
    def get_nature_spells_remaining(self, spell_level: int) -> int:
        """Get nature spells remaining for given level"""
        per_day = self.get_nature_spells_per_day().get(spell_level, 0)
        used = self.nature_spells_used.get(spell_level, 0)
        return max(0, per_day - used)
    
    def can_cast_nature_spell(self, spell_level: int) -> bool:
        """Check if ranger can cast nature spell of given level"""
        return self.get_nature_spells_remaining(spell_level) > 0
    
    def cast_nature_spell(self, spell_name: str, spell_level: int, target=None) -> Dict[str, Any]:
        """Cast a nature spell"""
        if not self.can_cast_nature_spell(spell_level):
            return {'success': False, 'reason': f'No level {spell_level} spells remaining'}
        
        if spell_level not in self.nature_spells_used:
            self.nature_spells_used[spell_level] = 0
        self.nature_spells_used[spell_level] += 1
        
        spell_effects = {
            'cure_light_wounds': {'healing': 8, 'target_self': True},
            'detect_animals': {'range': 100, 'duration': 60},
            'entangle': {'area': 20, 'duration': 30},
            'barkskin': {'ac_bonus': 2, 'duration': 600},
            'cure_moderate_wounds': {'healing': 16, 'target_self': True},
            'plant_growth': {'area': 50, 'permanent': True}
        }
        
        effect = spell_effects.get(spell_name, {})
        
        # Apply healing if applicable
        if 'healing' in effect and target:
            healing_done = target.heal(effect['healing'])
            effect['healing_done'] = healing_done
        
        return {
            'success': True,
            'spell_name': spell_name,
            'spell_level': spell_level,
            'effect': effect,
            'remaining_spells': self.get_nature_spells_remaining(spell_level)
        }
    
    # === WILDERNESS ABILITIES ===
    
    def _calculate_camouflage(self) -> int:
        """Calculate camouflage bonus"""
        base_bonus = 2
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 4)
        level_bonus = self.level // 4
        return base_bonus + dex_bonus + wis_bonus + level_bonus
    
    def get_camouflage_bonus(self) -> int:
        """Get camouflage bonus in natural terrain"""
        return self._calculate_camouflage()
    
    def _calculate_endurance(self) -> int:
        """Calculate endurance bonus"""
        base_bonus = 3
        con_bonus = max(0, (self.stats['constitution'] - 10) // 2)
        level_bonus = self.level // 3
        return base_bonus + con_bonus + level_bonus
    
    def get_endurance_bonus(self) -> int:
        """Get endurance bonus for long activities"""
        return self._calculate_endurance()
    
    def can_woodland_stride(self) -> bool:
        """Check if ranger can move through natural terrain unhindered"""
        return self.level >= 3
    
    def has_environmental_resistance(self) -> bool:
        """Check if ranger resists environmental effects"""
        return self.resist_environmental
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Rangers can use simple and martial weapons"""
        if hasattr(weapon, 'weapon_category'):
            return weapon.weapon_category.lower() in ['simple', 'martial']
        return True  # Default allow for basic weapons
    
    def can_use_armor(self, armor) -> bool:
        """Rangers can use light and medium armor"""
        if hasattr(armor, 'armor_type'):
            allowed_types = ['light', 'medium', 'leather', 'studded', 'chain']
            return armor.armor_type.lower() in allowed_types
        return True  # Default allow for basic armor
    
    def calculate_derived_stats(self):
        """Override to use DEX for attack bonus with finesse weapons"""
        super().calculate_derived_stats()
        
        # Rangers can use DEX for attack bonus when dual-wielding light weapons
        if self.is_dual_wielding():
            dex_modifier = (self.stats['dexterity'] - 10) // 2
            str_modifier = (self.stats['strength'] - 10) // 2
            # Use higher of DEX or STR
            self.base_attack_bonus = self.level + max(dex_modifier, str_modifier)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ranger':
        """Create Ranger from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        ranger = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        ranger.level = data['level']
        ranger.experience = data['experience']
        ranger.base_stats = data.get('base_stats', ranger.base_stats)
        ranger.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        ranger.max_hp = derived['max_hp']
        ranger.current_hp = derived['current_hp']
        ranger.armor_class = derived['armor_class']
        ranger.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        ranger.current_area = location.get('area_id')
        ranger.current_room = location.get('room_id')
        
        # Initialize item systems
        ranger.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            ranger.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            ranger.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        ranger.unallocated_stats = data.get('unallocated_stats', 0)
        ranger.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            ranger.load_alignment_data(data['alignment_data'])
        
        # Restore ranger-specific attributes
        ranger_data = data.get('ranger_data', {})
        ranger.favored_enemies = ranger_data.get('favored_enemies', ['humanoid'])
        ranger.animal_companion = ranger_data.get('animal_companion')
        ranger.nature_spells_used = ranger_data.get('nature_spells_used', {})
        
        # Recalculate ranger-specific attributes
        ranger.dual_wield_penalty_reduction = ranger._calculate_dual_wield_reduction()
        ranger.improved_two_weapon = ranger.level >= 6
        ranger.greater_two_weapon = ranger.level >= 11
        ranger.tracking_bonus = ranger._calculate_tracking_bonus()
        ranger.survival_bonus = ranger._calculate_survival_bonus()
        ranger.hide_in_wilderness = ranger._calculate_wilderness_stealth()
        ranger.animal_empathy_bonus = ranger._calculate_animal_empathy()
        ranger.animal_companion_level = max(1, ranger.level // 4)
        ranger.favored_enemy_bonus = ranger._calculate_favored_enemy_bonus()
        ranger.nature_magic_level = max(1, ranger.level // 2)
        ranger.nature_spells_per_day = ranger._calculate_nature_spells()
        ranger.camouflage_bonus = ranger._calculate_camouflage()
        ranger.endurance_bonus = ranger._calculate_endurance()
        ranger.resist_environmental = ranger.level >= 4
        
        return ranger
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include ranger-specific data"""
        data = super().to_dict()
        data['ranger_data'] = {
            'favored_enemies': self.favored_enemies,
            'animal_companion': self.animal_companion,
            'nature_spells_used': self.nature_spells_used
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Ranger"""
        abilities = []
        
        # Dual-wield
        if self.is_dual_wielding():
            attacks = self.get_dual_wield_attacks()
            abilities.append(f"Dual-Wield ({attacks} attacks)")
        else:
            reduction = self.get_dual_wield_reduction()
            abilities.append(f"DW -{reduction}")
        
        # Tracking
        tracking = self.get_tracking_bonus()
        abilities.append(f"Track +{tracking}")
        
        # Favored enemies
        if self.favored_enemies:
            enemies = '/'.join(self.favored_enemies[:2])  # Show first 2
            bonus = self.get_favored_enemy_bonus()
            abilities.append(f"{enemies} +{bonus}")
        
        # Animal companion
        if self.animal_companion:
            abilities.append(f"{self.animal_companion.title()} ({self.animal_companion_level})")
        
        # Nature magic
        total_spells = sum(self.get_nature_spells_per_day().values())
        if total_spells > 0:
            abilities.append(f"Spells {total_spells}")
        
        # Wilderness abilities
        if self.can_woodland_stride():
            abilities.append("Woodland Stride")
        if self.leaves_no_trail():
            abilities.append("Trackless")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str