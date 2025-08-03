"""
Thief Character Class for Rogue City
Traditional MajorMUD urban specialist in stealth and skills with devastating backstab.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Thief(BaseCharacter):
    """
    Thief class - Urban stealth specialist with devastating backstab
    
    STEALTH MASTER - Slow progression, high-skill class with powerful abilities
    
    Experience Penalty: +35% (high-skill class with powerful backstab abilities)
    Stat Modifiers: +3 DEX, +2 INT, +1 CHA, -3 STR, -2 CON, -1 WIS
    Hit Die: d4 (very low HP, relies on not being hit)
    Attack Speed: 2.0 seconds (very fast for backstab opportunities)
    Critical Range: 19-20 (improved critical chance)
    
    URBAN MASTERY CORE:
    - Master lockpicking to open any mechanical lock
    - Trap detection and disarmament for all trap types
    - Devastating backstab with massive damage from stealth (up to 5x damage)
    - Pickpocket ability to steal from NPCs and other players
    - Superior stealth with hide in shadows mastery
    - Escape artist abilities to slip bonds and escape danger
    
    THIEF ABILITIES:
    - Master Lockpicking: Open any mechanical lock
    - Trap Detection: Find and disarm all trap types
    - Backstab: Massive damage from stealth (up to 5x damage)
    - Pickpocket: Steal from NPCs and other players
    - Hide in Shadows: Superior stealth abilities
    - Escape Artist: Slip bonds and escape dangerous situations
    
    EQUIPMENT ACCESS:
    - Weapons: Light weapons and thief tools
    - Armor: Light armor only (leather and lighter)
    - Magic: Can use stealth-enhancing magical items
    - Accessories: Thief tools, lock picks, stealth gear
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Thief character with stealth and skill systems"""
        super().__init__(name, 'thief', race_id, alignment)
        
        # Lockpicking mastery
        self.lockpicking_bonus = self._calculate_lockpicking_bonus()
        self.master_lockpicking = self.level >= 5
        self.legendary_lockpicking = self.level >= 15
        
        # Trap mastery
        self.trap_detection_bonus = self._calculate_trap_detection()
        self.trap_disarm_bonus = self._calculate_trap_disarm()
        self.trap_immunity = self.level >= 10  # Immune to mechanical traps
        
        # Stealth mastery
        self.stealth_bonus = self._calculate_stealth_bonus()
        self.hide_in_shadows_bonus = self._calculate_hide_bonus()
        self.move_silently_bonus = self._calculate_move_silently()
        self.is_hidden = False
        self.improved_invisibility = self.level >= 12
        
        # Backstab system
        self.backstab_multiplier = self._calculate_backstab_multiplier()
        self.sneak_attack_dice = self._calculate_sneak_attack_dice()
        self.death_attack = self.level >= 20  # Instant kill on backstab
        
        # Pickpocket mastery
        self.pickpocket_bonus = self._calculate_pickpocket_bonus()
        self.steal_magic_items = self.level >= 8
        self.plant_items = self.level >= 6
        
        # Escape abilities
        self.escape_artist_bonus = self._calculate_escape_bonus()
        self.slippery_mind = self.level >= 7  # Bonus to mental saves
        self.evasion = self.level >= 2  # Avoid area effects
        self.improved_evasion = self.level >= 8
        
        # Urban knowledge
        self.streetwise_bonus = self._calculate_streetwise()
        self.gather_information_bonus = self._calculate_gather_info()
        self.underworld_contacts = self.level >= 10
        
    def get_hit_die_value(self) -> int:
        """Thieves use d4 hit die (lowest HP, glass cannon)"""
        return 4
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d4"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Thieves attack every 2 seconds unarmed (very fast for backstab)"""
        return 2.0
        
    def get_critical_range(self) -> int:
        """Thieves crit on 19-20 (improved critical chance)"""
        return 19
        
    def get_experience_penalty(self) -> int:
        """Thieves have +35% experience penalty"""
        return 35
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Thief special abilities"""
        return {
            # Lockpicking mastery
            'master_lockpicking': self.get_lockpicking_bonus(),
            'lockpicking_mastery': self.master_lockpicking,
            'legendary_lockpicking': self.legendary_lockpicking,
            'open_any_lock': self.level >= 5,
            'lock_expertise': True,
            
            # Trap mastery
            'trap_detection': self.get_trap_detection_bonus(),
            'trap_disarmament': self.get_trap_disarm_bonus(),
            'trap_immunity': self.trap_immunity,
            'trap_expertise': True,
            'find_all_traps': True,
            
            # Stealth mastery
            'stealth_master': self.get_stealth_bonus(),
            'hide_in_shadows': self.get_hide_bonus(),
            'move_silently': self.get_move_silently_bonus(),
            'improved_invisibility': self.improved_invisibility,
            'shadow_mastery': self.level >= 10,
            
            # Backstab system
            'backstab_multiplier': self.get_backstab_multiplier(),
            'sneak_attack_dice': self.get_sneak_attack_dice(),
            'death_attack': self.death_attack,
            'assassination': self.level >= 15,
            'crippling_strike': self.level >= 10,
            
            # Pickpocket mastery
            'pickpocket': self.get_pickpocket_bonus(),
            'steal_magic_items': self.steal_magic_items,
            'plant_items': self.plant_items,
            'perfect_theft': self.level >= 12,
            
            # Escape abilities
            'escape_artist': self.get_escape_bonus(),
            'slippery_mind': self.slippery_mind,
            'evasion': self.evasion,
            'improved_evasion': self.improved_evasion,
            'uncanny_dodge': self.level >= 4,
            
            # Urban knowledge
            'streetwise': self.get_streetwise_bonus(),
            'gather_information': self.get_gather_info_bonus(),
            'underworld_contacts': self.underworld_contacts,
            'criminal_network': self.level >= 8,
            
            # Combat abilities
            'improved_critical': True,
            'critical_range': 19,
            'opportunist': self.level >= 6,
            'defensive_roll': self.level >= 8,
            
            # Equipment restrictions
            'light_weapons_only': True,
            'light_armor_only': True,
            'thief_tools_mastery': True
        }
    
    # === LOCKPICKING MASTERY ===
    
    def _calculate_lockpicking_bonus(self) -> int:
        """Calculate master lockpicking bonus"""
        base_bonus = 5
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        level_bonus = self.level * 2  # +2 per level (specialists)
        return base_bonus + dex_bonus + int_bonus + level_bonus
    
    def get_lockpicking_bonus(self) -> int:
        """Get master lockpicking bonus"""
        return self._calculate_lockpicking_bonus()
    
    def attempt_lockpicking(self, lock_difficulty: int = 15) -> Dict[str, Any]:
        """Attempt to pick a lock"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            
            # Take 10 on routine locks if master
            if self.master_lockpicking and lock_difficulty <= 20:
                lockpick_roll = 10 + self.get_lockpicking_bonus()
            else:
                lockpick_roll = dice.roll("1d20") + self.get_lockpicking_bonus()
            
            success = lockpick_roll >= lock_difficulty
            
            # Legendary lockpicking can open any lock
            if self.legendary_lockpicking and not success:
                if dice.roll("1d20") >= 15:  # 30% chance to open anyway
                    success = True
                    lockpick_roll = "Legendary"
            
            return {
                'success': success,
                'lockpick_roll': lockpick_roll,
                'difficulty': lock_difficulty,
                'lock_status': 'opened' if success else 'remains locked',
                'time_taken': 1 if success else 3  # Rounds
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_lockpicking_bonus() >= lock_difficulty
            return {
                'success': success,
                'lock_status': 'opened' if success else 'remains locked'
            }
    
    def can_open_any_lock(self) -> bool:
        """Check if thief can open any mechanical lock"""
        return self.level >= 5
    
    def pick_lock_silently(self, lock_difficulty: int = 15) -> bool:
        """Pick lock without making noise"""
        result = self.attempt_lockpicking(lock_difficulty)
        # Silent picking is easier for masters
        if result['success'] and self.master_lockpicking:
            return True
        return False
    
    # === TRAP MASTERY ===
    
    def _calculate_trap_detection(self) -> int:
        """Calculate trap detection bonus"""
        base_bonus = 4
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 4)
        level_bonus = self.level + 5  # +1 per level + 5 base
        return base_bonus + int_bonus + wis_bonus + level_bonus
    
    def get_trap_detection_bonus(self) -> int:
        """Get trap detection bonus"""
        return self._calculate_trap_detection()
    
    def _calculate_trap_disarm(self) -> int:
        """Calculate trap disarmament bonus"""
        base_bonus = 5
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        level_bonus = self.level * 2  # +2 per level
        return base_bonus + dex_bonus + int_bonus + level_bonus
    
    def get_trap_disarm_bonus(self) -> int:
        """Get trap disarmament bonus"""
        return self._calculate_trap_disarm()
    
    def detect_traps(self, search_dc: int = 15) -> Dict[str, Any]:
        """Detect traps in area"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            detection_roll = dice.roll("1d20") + self.get_trap_detection_bonus()
            success = detection_roll >= search_dc
            
            return {
                'success': success,
                'detection_roll': detection_roll,
                'search_dc': search_dc,
                'traps_found': ['pressure plate', 'dart trap'] if success else [],
                'detailed_info': success and self.level >= 8
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_trap_detection_bonus() >= search_dc
            return {
                'success': success,
                'traps_found': ['pressure plate'] if success else []
            }
    
    def disarm_trap(self, trap_difficulty: int = 20) -> Dict[str, Any]:
        """Disarm a detected trap"""
        if self.trap_immunity and trap_difficulty <= 25:
            return {
                'success': True,
                'method': 'immunity',
                'trap_status': 'disabled safely'
            }
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            disarm_roll = dice.roll("1d20") + self.get_trap_disarm_bonus()
            success = disarm_roll >= trap_difficulty
            
            return {
                'success': success,
                'disarm_roll': disarm_roll,
                'difficulty': trap_difficulty,
                'trap_status': 'disabled' if success else 'triggered',
                'time_taken': 2 if success else 1  # Rounds
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_trap_disarm_bonus() >= trap_difficulty
            return {
                'success': success,
                'trap_status': 'disabled' if success else 'triggered'
            }
    
    def is_immune_to_traps(self) -> bool:
        """Check if thief is immune to mechanical traps"""
        return self.trap_immunity
    
    # === STEALTH MASTERY ===
    
    def _calculate_stealth_bonus(self) -> int:
        """Calculate master stealth bonus"""
        base_bonus = 5
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        level_bonus = self.level + 3  # +1 per level + 3 base
        return base_bonus + dex_bonus + level_bonus
    
    def get_stealth_bonus(self) -> int:
        """Get master stealth bonus"""
        return self._calculate_stealth_bonus()
    
    def _calculate_hide_bonus(self) -> int:
        """Calculate hide in shadows bonus"""
        base_bonus = 6
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        level_bonus = self.level + 5  # +1 per level + 5 base
        return base_bonus + dex_bonus + level_bonus
    
    def get_hide_bonus(self) -> int:
        """Get hide in shadows bonus"""
        return self._calculate_hide_bonus()
    
    def _calculate_move_silently(self) -> int:
        """Calculate move silently bonus"""
        base_bonus = 5
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        level_bonus = self.level + 4  # +1 per level + 4 base
        return base_bonus + dex_bonus + level_bonus
    
    def get_move_silently_bonus(self) -> int:
        """Get move silently bonus"""
        return self._calculate_move_silently()
    
    def attempt_stealth(self, detection_dc: int = 15) -> Dict[str, Any]:
        """Attempt to enter stealth"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            stealth_roll = dice.roll("1d20") + self.get_stealth_bonus()
            success = stealth_roll >= detection_dc
            
            if success:
                self.is_hidden = True
                
            return {
                'success': success,
                'stealth_roll': stealth_roll,
                'detection_dc': detection_dc,
                'stealth_status': 'hidden' if success else 'detected',
                'duration': 'until broken' if success else 0
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_stealth_bonus() >= detection_dc
            self.is_hidden = success
            return {
                'success': success,
                'stealth_status': 'hidden' if success else 'detected'
            }
    
    def hide_in_shadows(self, shadow_dc: int = 12) -> bool:
        """Hide in shadows (easier than general stealth)"""
        result = self.attempt_stealth(shadow_dc)
        return result['success']
    
    def can_use_improved_invisibility(self) -> bool:
        """Check if thief can use improved invisibility"""
        return self.improved_invisibility
    
    def break_stealth(self):
        """Break stealth (when attacking, etc.)"""
        self.is_hidden = False
    
    # === BACKSTAB SYSTEM ===
    
    def _calculate_backstab_multiplier(self) -> float:
        """Calculate backstab damage multiplier"""
        base_multiplier = 2.0  # 2x damage at level 1
        if self.level >= 5:
            base_multiplier = 3.0  # 3x at level 5
        if self.level >= 9:
            base_multiplier = 4.0  # 4x at level 9
        if self.level >= 13:
            base_multiplier = 5.0  # 5x at level 13
        return base_multiplier
    
    def get_backstab_multiplier(self) -> float:
        """Get backstab damage multiplier"""
        return self._calculate_backstab_multiplier()
    
    def _calculate_sneak_attack_dice(self) -> int:
        """Calculate sneak attack bonus dice"""
        return (self.level + 1) // 2  # +1d6 per 2 levels
    
    def get_sneak_attack_dice(self) -> int:
        """Get sneak attack bonus dice"""
        return self._calculate_sneak_attack_dice()
    
    def can_backstab(self, target_aware: bool = True) -> bool:
        """Check if thief can perform backstab"""
        return not target_aware or self.is_hidden
    
    def perform_backstab(self, base_damage: int, target_aware: bool = False) -> Dict[str, Any]:
        """Perform backstab attack"""
        if not self.can_backstab(target_aware):
            return {
                'success': False,
                'reason': 'Cannot backstab aware target',
                'damage': base_damage
            }
        
        # Calculate backstab damage
        multiplier = self.get_backstab_multiplier()
        backstab_damage = int(base_damage * multiplier)
        
        # Add sneak attack dice
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            sneak_dice = self.get_sneak_attack_dice()
            sneak_damage = sum(dice.roll("1d6") for _ in range(sneak_dice))
            total_damage = backstab_damage + sneak_damage
        except ImportError:
            import random
            sneak_dice = self.get_sneak_attack_dice()
            sneak_damage = sum(random.randint(1, 6) for _ in range(sneak_dice))
            total_damage = backstab_damage + sneak_damage
        
        # Check for death attack
        death_attack_success = False
        if self.death_attack and self.level >= 20:
            try:
                from core.dice_system import DiceSystem
                dice = DiceSystem(show_rolls=False)
                death_roll = dice.roll("1d20")
                death_attack_success = death_roll >= 15  # 30% chance
            except ImportError:
                import random
                death_attack_success = random.randint(1, 20) >= 15
        
        # Break stealth after attacking
        self.break_stealth()
        
        return {
            'success': True,
            'base_damage': base_damage,
            'multiplier': multiplier,
            'backstab_damage': backstab_damage,
            'sneak_dice': sneak_dice,
            'sneak_damage': sneak_damage,
            'total_damage': total_damage,
            'death_attack': death_attack_success,
            'crippling': self.level >= 10  # Crippling strike
        }
    
    def can_use_death_attack(self) -> bool:
        """Check if thief can use death attack"""
        return self.death_attack
    
    # === PICKPOCKET MASTERY ===
    
    def _calculate_pickpocket_bonus(self) -> int:
        """Calculate pickpocket bonus"""
        base_bonus = 4
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 4)
        level_bonus = self.level + 2  # +1 per level + 2 base
        return base_bonus + dex_bonus + cha_bonus + level_bonus
    
    def get_pickpocket_bonus(self) -> int:
        """Get pickpocket bonus"""
        return self._calculate_pickpocket_bonus()
    
    def attempt_pickpocket(self, target_level: int = 1, item_value: str = "common") -> Dict[str, Any]:
        """Attempt to pickpocket a target"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            pickpocket_roll = dice.roll("1d20") + self.get_pickpocket_bonus()
            
            # Calculate difficulty
            base_dc = 10 + target_level
            value_modifiers = {'common': 0, 'valuable': 5, 'magical': 10, 'legendary': 15}
            difficulty = base_dc + value_modifiers.get(item_value, 0)
            
            # Magic items require higher level
            if item_value == 'magical' and not self.steal_magic_items:
                return {
                    'success': False,
                    'reason': 'Cannot steal magical items yet',
                    'detected': False
                }
            
            success = pickpocket_roll >= difficulty
            detected = pickpocket_roll < (difficulty - 5)  # Detected if fail badly
            
            return {
                'success': success,
                'pickpocket_roll': pickpocket_roll,
                'difficulty': difficulty,
                'detected': detected,
                'item_stolen': success,
                'target_notices': detected
            }
        except ImportError:
            import random
            base_dc = 10 + target_level
            success = random.randint(1, 20) + self.get_pickpocket_bonus() >= base_dc
            return {
                'success': success,
                'detected': not success and random.randint(1, 2) == 1
            }
    
    def can_steal_magic_items(self) -> bool:
        """Check if thief can steal magical items"""
        return self.steal_magic_items
    
    def can_plant_items(self) -> bool:
        """Check if thief can plant items on targets"""
        return self.plant_items
    
    def plant_item_on_target(self, target_level: int = 1) -> bool:
        """Plant an item on a target"""
        if not self.can_plant_items():
            return False
        
        result = self.attempt_pickpocket(target_level, "common")
        return result['success'] and not result.get('detected', False)
    
    # === ESCAPE ABILITIES ===
    
    def _calculate_escape_bonus(self) -> int:
        """Calculate escape artist bonus"""
        base_bonus = 3
        dex_bonus = max(0, (self.stats['dexterity'] - 10) // 2)
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 4)
        level_bonus = self.level // 2
        return base_bonus + dex_bonus + int_bonus + level_bonus
    
    def get_escape_bonus(self) -> int:
        """Get escape artist bonus"""
        return self._calculate_escape_bonus()
    
    def attempt_escape(self, restraint_dc: int = 15) -> Dict[str, Any]:
        """Attempt to escape from restraints"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            escape_roll = dice.roll("1d20") + self.get_escape_bonus()
            success = escape_roll >= restraint_dc
            
            return {
                'success': success,
                'escape_roll': escape_roll,
                'restraint_dc': restraint_dc,
                'escape_status': 'free' if success else 'still bound',
                'time_taken': 1 if success else 3  # Rounds
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_escape_bonus() >= restraint_dc
            return {
                'success': success,
                'escape_status': 'free' if success else 'still bound'
            }
    
    def has_slippery_mind(self) -> bool:
        """Check if thief has slippery mind (mental save bonus)"""
        return self.slippery_mind
    
    def get_mental_save_bonus(self) -> int:
        """Get bonus to mental saves from slippery mind"""
        return 2 if self.has_slippery_mind() else 0
    
    def has_evasion(self) -> bool:
        """Check if thief has evasion"""
        return self.evasion
    
    def has_improved_evasion(self) -> bool:
        """Check if thief has improved evasion"""
        return self.improved_evasion
    
    # === URBAN KNOWLEDGE ===
    
    def _calculate_streetwise(self) -> int:
        """Calculate streetwise bonus"""
        base_bonus = 3
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 2)
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        level_bonus = self.level // 2
        return base_bonus + int_bonus + cha_bonus + level_bonus
    
    def get_streetwise_bonus(self) -> int:
        """Get streetwise bonus"""
        return self._calculate_streetwise()
    
    def _calculate_gather_info(self) -> int:
        """Calculate gather information bonus"""
        base_bonus = 2
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        int_bonus = max(0, (self.stats['intelligence'] - 10) // 4)
        level_bonus = self.level // 3
        return base_bonus + cha_bonus + int_bonus + level_bonus
    
    def get_gather_info_bonus(self) -> int:
        """Get gather information bonus"""
        return self._calculate_gather_info()
    
    def has_underworld_contacts(self) -> bool:
        """Check if thief has underworld contacts"""
        return self.underworld_contacts
    
    def use_underworld_contacts(self, information_type: str = "general") -> Dict[str, Any]:
        """Use underworld contacts to gather information"""
        if not self.has_underworld_contacts():
            return {'success': False, 'reason': 'No underworld contacts'}
        
        return {
            'success': True,
            'information_type': information_type,
            'contacts_available': True,
            'cost': 'moderate',
            'reliability': 'high' if self.level >= 15 else 'moderate'
        }
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Thieves can only use light weapons"""
        if hasattr(weapon, 'weapon_category'):
            return weapon.weapon_category.lower() in ['light', 'simple']
        if hasattr(weapon, 'weapon_type'):
            allowed_types = ['dagger', 'short_sword', 'dart', 'sling', 'light_crossbow']
            return weapon.weapon_type.lower() in allowed_types
        return True  # Default allow for basic weapons
    
    def can_use_armor(self, armor) -> bool:
        """Thieves can only use light armor"""
        if hasattr(armor, 'armor_type'):
            allowed_types = ['light', 'leather', 'studded_leather', 'cloth']
            return armor.armor_type.lower() in allowed_types
        return True  # Default allow for basic armor
    
    def calculate_derived_stats(self):
        """Override to use DEX for attack bonus with finesse weapons"""
        super().calculate_derived_stats()
        
        # Thieves use DEX modifier for attack bonus
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        self.base_attack_bonus = self.level + dex_modifier
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Thief':
        """Create Thief from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        thief = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        thief.level = data['level']
        thief.experience = data['experience']
        thief.base_stats = data.get('base_stats', thief.base_stats)
        thief.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        thief.max_hp = derived['max_hp']
        thief.current_hp = derived['current_hp']
        thief.armor_class = derived['armor_class']
        thief.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        thief.current_area = location.get('area_id')
        thief.current_room = location.get('room_id')
        
        # Initialize item systems
        thief.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            thief.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            thief.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        thief.unallocated_stats = data.get('unallocated_stats', 0)
        thief.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            thief.load_alignment_data(data['alignment_data'])
        
        # Restore thief-specific attributes
        thief_data = data.get('thief_data', {})
        thief.is_hidden = thief_data.get('is_hidden', False)
        
        # Recalculate thief-specific attributes
        thief.lockpicking_bonus = thief._calculate_lockpicking_bonus()
        thief.master_lockpicking = thief.level >= 5
        thief.legendary_lockpicking = thief.level >= 15
        thief.trap_detection_bonus = thief._calculate_trap_detection()
        thief.trap_disarm_bonus = thief._calculate_trap_disarm()
        thief.trap_immunity = thief.level >= 10
        thief.stealth_bonus = thief._calculate_stealth_bonus()
        thief.hide_in_shadows_bonus = thief._calculate_hide_bonus()
        thief.move_silently_bonus = thief._calculate_move_silently()
        thief.improved_invisibility = thief.level >= 12
        thief.backstab_multiplier = thief._calculate_backstab_multiplier()
        thief.sneak_attack_dice = thief._calculate_sneak_attack_dice()
        thief.death_attack = thief.level >= 20
        thief.pickpocket_bonus = thief._calculate_pickpocket_bonus()
        thief.steal_magic_items = thief.level >= 8
        thief.plant_items = thief.level >= 6
        thief.escape_artist_bonus = thief._calculate_escape_bonus()
        thief.slippery_mind = thief.level >= 7
        thief.evasion = thief.level >= 2
        thief.improved_evasion = thief.level >= 8
        thief.streetwise_bonus = thief._calculate_streetwise()
        thief.gather_information_bonus = thief._calculate_gather_info()
        thief.underworld_contacts = thief.level >= 10
        
        return thief
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include thief-specific data"""
        data = super().to_dict()
        data['thief_data'] = {
            'is_hidden': self.is_hidden
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Thief"""
        abilities = []
        
        # Stealth status
        if self.is_hidden:
            abilities.append("Hidden")
        else:
            stealth = self.get_stealth_bonus()
            abilities.append(f"Stealth +{stealth}")
        
        # Backstab multiplier
        backstab = self.get_backstab_multiplier()
        abilities.append(f"Backstab {backstab}x")
        
        # Lockpicking
        lockpick = self.get_lockpicking_bonus()
        abilities.append(f"Lock +{lockpick}")
        
        # Trap detection
        trap_detect = self.get_trap_detection_bonus()
        abilities.append(f"Trap +{trap_detect}")
        
        # Pickpocket
        pickpocket = self.get_pickpocket_bonus()
        abilities.append(f"Pick +{pickpocket}")
        
        # High-level abilities
        if self.master_lockpicking:
            abilities.append("Master Locks")
        if self.trap_immunity:
            abilities.append("Trap Immune")
        if self.death_attack:
            abilities.append("Death Attack")
        if self.has_underworld_contacts():
            abilities.append("Contacts")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str