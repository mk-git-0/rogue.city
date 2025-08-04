"""
Rogue Character Class for Rogue City
Flagship MajorMUD-style class: Anti-magic Witchhunter + Thief + Ninja hybrid.
Highest difficulty but extremely rewarding for skilled players.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple


class Rogue(BaseCharacter):
    """
    Rogue class - Anti-magic specialist combining Witchhunter, Thief, and Ninja
    
    FLAGSHIP CLASS - Highest difficulty, highest reward
    
    Difficulty: 11 (Highest) - Challenging but extremely powerful
    Stat Modifiers: +3 DEX, +2 INT, -2 STR, -2 CON, -1 WIS, -1 CHA
    Hit Die: d6
    Attacks Per Turn: Fast dual-wield dagger combat
    Critical Range: 19-20 (improved critical chance)
    
    WITCHHUNTER HERITAGE (Anti-Magic Core):
    - Magic Resistance: +4 base, scaling with level
    - Cannot use magical items (anti-magic aura interferes)
    - Spell immunity to charm, fear, mind control
    - Anti-magic aura causes nearby spells to fail
    
    THIEF HERITAGE (Stealth and Skills):
    - Stealth mastery with scaling bonuses
    - Lockpicking and trap detection/disarmament
    - Backstab for massive damage from stealth
    - Pickpocketing and hide in shadows
    
    NINJA HERITAGE (Combat Precision):
    - Dual-wield daggers with reduced penalties
    - Pressure point strikes cause status effects
    - Shadow step teleportation
    - Assassination chance on backstab
    
    EQUIPMENT RESTRICTIONS:
    - Weapons: Daggers only (including throwing daggers)
    - Armor: Light armor only (leather and lighter)
    - Magic: Cannot use ANY enchanted equipment
    - Accessories: Non-magical only
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Rogue character with anti-magic and stealth systems"""
        super().__init__(name, 'rogue', race_id, alignment)
        
        # Anti-magic heritage attributes
        self.magic_resistance = self._calculate_magic_resistance()
        self.spell_failure_aura = True
        
        # Stealth and thief attributes
        self.stealth_bonus = self._calculate_stealth_bonus()
        self.is_hidden = False
        self.lockpicking_skill = self._calculate_lockpicking()
        self.trap_detection = True
        
        # Ninja combat attributes
        self.dual_wield_penalty_reduction = self._calculate_dual_wield_reduction()
        self.shadow_step_uses = max(1, self.level // 5)
        self.assassination_chance = self.level  # 1% per level
        
    def get_hit_die_value(self) -> int:
        """Rogues use d6 hit die (average 6 HP per level)"""
        return 6
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d6"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Rogues attack every 2 seconds unarmed (fastest)"""
        return 2.0
        
    def get_critical_range(self) -> int:
        """Rogues crit on 19-20 (improved critical chance)"""
        return 19
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Rogue special abilities"""
        return {
            # Witchhunter abilities
            'magic_resistance': self.get_magic_resistance(),
            'anti_magic_aura': True,
            'spell_immunity': ['charm', 'fear', 'mind_control'],
            'cannot_use_magic_items': True,
            
            # Thief abilities
            'stealth_mastery': self.get_stealth_bonus(),
            'backstab_multiplier': self.get_backstab_multiplier(),
            'lockpicking': self.get_lockpicking_skill(),
            'trap_detection': True,
            'trap_disarmament': True,
            'pickpocket': True,
            'hide_in_shadows': True,
            
            # Ninja abilities
            'dual_wield_mastery': True,
            'dual_wield_penalty_reduction': self.get_dual_wield_reduction(),
            'pressure_points': self.level >= 5,
            'shadow_step': self.level >= 8,
            'assassination': self.level >= 10,
            
            # Combat abilities
            'improved_critical': True,
            'critical_range': 19,
            'poison_resistance': 2,
            
            # Equipment restrictions
            'daggers_only': True,
            'light_armor_only': True,
            'no_magical_equipment': True
        }
        
    def calculate_derived_stats(self):
        """Override to use DEX for attack bonus instead of STR"""
        super().calculate_derived_stats()
        
        # Rogues use DEX modifier for attack bonus with finesse weapons
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        self.base_attack_bonus = self.level + dex_modifier
        
    # === WITCHHUNTER ABILITIES ===
    
    def _calculate_magic_resistance(self) -> int:
        """Calculate total magic resistance"""
        base_resistance = 4
        level_bonus = self.level // 5  # +1 per 5 levels
        return base_resistance + level_bonus
    
    def get_magic_resistance(self) -> int:
        """Get current magic resistance value"""
        return self._calculate_magic_resistance()
    
    def can_use_magical_items(self) -> bool:
        """Rogues cannot use magical items due to anti-magic heritage"""
        return False
    
    def causes_spell_failure(self, distance: int = 5) -> bool:
        """Check if rogue's anti-magic aura causes spell failure"""
        # Spells cast within 5 feet have 25% failure chance
        return distance <= 5
    
    def get_spell_failure_chance(self) -> int:
        """Get spell failure chance caused by anti-magic aura"""
        return 25  # 25% base failure chance
    
    def is_immune_to_spell(self, spell_type: str) -> bool:
        """Check immunity to specific spell types"""
        immune_types = ['charm', 'fear', 'mind_control', 'dominate', 'suggestion']
        return spell_type.lower() in immune_types
    
    # === THIEF ABILITIES ===
    
    def _calculate_stealth_bonus(self) -> int:
        """Calculate stealth skill bonus"""
        base_bonus = 3
        level_bonus = self.level // 3  # +1 per 3 levels
        dex_bonus = (self.stats['dexterity'] - 10) // 2
        return base_bonus + level_bonus + max(0, dex_bonus)
    
    def get_stealth_bonus(self) -> int:
        """Get current stealth bonus"""
        return self._calculate_stealth_bonus()
    
    def _calculate_lockpicking(self) -> int:
        """Calculate lockpicking skill"""
        base_skill = 5 + self.level
        dex_bonus = (self.stats['dexterity'] - 10) // 2
        int_bonus = (self.stats['intelligence'] - 10) // 4  # Intelligence helps with complex locks
        return base_skill + dex_bonus + int_bonus
    
    def get_lockpicking_skill(self) -> int:
        """Get current lockpicking skill"""
        return self._calculate_lockpicking()
    
    def get_backstab_multiplier(self) -> float:
        """Calculate backstab damage multiplier"""
        base_multiplier = 3.0  # 3x damage base
        if self.level >= 10:
            return 4.0  # 4x damage at level 10+
        return base_multiplier
    
    def can_backstab(self, target_aware: bool = True) -> bool:
        """Check if rogue can perform backstab"""
        return not target_aware or self.is_hidden
    
    def attempt_stealth(self) -> bool:
        """Attempt to enter stealth mode"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            stealth_roll = dice.roll("1d20") + self.get_stealth_bonus()
            # DC 15 base, modified by circumstances
            success = stealth_roll >= 15
            self.is_hidden = success
            return success
        except ImportError:
            # Fallback without dice system
            import random
            self.is_hidden = random.randint(1, 20) + self.get_stealth_bonus() >= 15
            return self.is_hidden
    
    def attempt_pickpocket(self, target_level: int = 1) -> bool:
        """Attempt to pickpocket a target"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            skill_roll = dice.roll("1d20") + self.get_stealth_bonus()
            dc = 10 + target_level
            return skill_roll >= dc
        except ImportError:
            import random
            return random.randint(1, 20) + self.get_stealth_bonus() >= (10 + target_level)
    
    def can_detect_traps(self) -> bool:
        """Rogues automatically detect traps"""
        return True
    
    def attempt_disarm_trap(self, trap_difficulty: int = 15) -> bool:
        """Attempt to disarm a trap"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            skill_roll = dice.roll("1d20") + self.get_lockpicking_skill()
            return skill_roll >= trap_difficulty
        except ImportError:
            import random
            return random.randint(1, 20) + self.get_lockpicking_skill() >= trap_difficulty
    
    # === NINJA ABILITIES ===
    
    def _calculate_dual_wield_reduction(self) -> int:
        """Calculate dual-wield penalty reduction"""
        base_reduction = 2  # -2 to dual-wield penalties
        level_bonus = self.level // 4  # Additional reduction every 4 levels
        return base_reduction + level_bonus
    
    def get_dual_wield_reduction(self) -> int:
        """Get dual-wield penalty reduction"""
        return self._calculate_dual_wield_reduction()
    
    def can_use_pressure_points(self) -> bool:
        """Check if rogue can use pressure point attacks"""
        return self.level >= 5
    
    def pressure_point_effect(self) -> str:
        """Determine pressure point effect on critical hit"""
        if not self.can_use_pressure_points():
            return "none"
        
        effects = ["stun", "poison", "paralysis", "slow"]
        # Higher level rogues get better effects
        if self.level >= 15:
            effects.extend(["blindness", "weakness"])
        
        import random
        return random.choice(effects)
    
    def can_shadow_step(self) -> bool:
        """Check if rogue can use shadow step"""
        return self.level >= 8 and self.shadow_step_uses > 0
    
    def use_shadow_step(self) -> bool:
        """Use shadow step ability"""
        if self.can_shadow_step():
            self.shadow_step_uses -= 1
            return True
        return False
    
    def get_assassination_chance(self) -> int:
        """Get assassination chance percentage on successful backstab"""
        if self.level < 10:
            return 0
        return min(20, self.level)  # 1% per level, max 20%
    
    def attempt_assassination(self) -> bool:
        """Attempt assassination on successful backstab"""
        chance = self.get_assassination_chance()
        if chance <= 0:
            return False
        
        import random
        return random.randint(1, 100) <= chance
    
    # === COMBAT ABILITIES ===
    
    def get_sneak_attack_damage(self) -> int:
        """Calculate sneak attack bonus damage dice"""
        # Sneak attack: +1d6 per 2 levels (minimum 1d6)
        sneak_dice = max(1, (self.level + 1) // 2)
        return sneak_dice
        
    def can_sneak_attack(self, target_surprised: bool = False, flanking: bool = False) -> bool:
        """Check if rogue can perform sneak attack"""
        # Sneak attack when target is surprised, flanked, or rogue is hidden
        return target_surprised or flanking or self.is_hidden
    
    def get_poison_resistance(self) -> int:
        """Get poison resistance bonus"""
        return 2  # +2 resistance to poison effects
        
    def can_use_weapon(self, weapon) -> bool:
        """Check if rogue can use a specific weapon (daggers only)"""
        if hasattr(weapon, 'weapon_type'):
            return weapon.weapon_type.lower() in ['dagger', 'throwing_dagger']
        if hasattr(weapon, 'name'):
            return 'dagger' in weapon.name.lower()
        return False
    
    def can_use_armor(self, armor) -> bool:
        """Check if rogue can use specific armor (light only)"""
        if hasattr(armor, 'armor_type'):
            return armor.armor_type.lower() in ['light', 'leather', 'cloth']
        return True  # Default allow for basic armor
    
    def can_equip_item(self, item) -> Tuple[bool, str]:
        """Check if rogue can equip an item with detailed reason"""
        # Check for magical items first
        if hasattr(item, 'is_magical') and item.is_magical:
            return False, "Rogues cannot use magical items due to anti-magic heritage"
        
        # Check weapon restrictions
        if hasattr(item, 'item_type') and item.item_type == 'weapon':
            if not self.can_use_weapon(item):
                return False, "Rogues can only use daggers and throwing daggers"
        
        # Check armor restrictions
        if hasattr(item, 'item_type') and item.item_type == 'armor':
            if not self.can_use_armor(item):
                return False, "Rogues can only wear light armor (leather and lighter)"
        
        return True, "Equipment allowed"
    
    def get_experience_penalty(self) -> int:
        """Rogues have +77% experience penalty (flagship class)"""
        return 77
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rogue':
        """Create Rogue from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        rogue = cls(data['character_name'], race_id, alignment)
        
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
        
        # Load alignment data
        if 'alignment_data' in data:
            rogue.load_alignment_data(data['alignment_data'])
        
        # Recalculate rogue-specific attributes
        rogue.magic_resistance = rogue._calculate_magic_resistance()
        rogue.stealth_bonus = rogue._calculate_stealth_bonus()
        rogue.lockpicking_skill = rogue._calculate_lockpicking()
        rogue.dual_wield_penalty_reduction = rogue._calculate_dual_wield_reduction()
        rogue.shadow_step_uses = max(1, rogue.level // 5)
        rogue.assassination_chance = rogue.level
        
        return rogue
        
    def __str__(self) -> str:
        """String representation of enhanced Rogue"""
        abilities = []
        
        # Magic resistance
        mr = self.get_magic_resistance()
        abilities.append(f"MR {mr}")
        
        # Stealth bonus
        stealth = self.get_stealth_bonus()
        abilities.append(f"Stealth +{stealth}")
        
        # Backstab
        backstab_mult = self.get_backstab_multiplier()
        abilities.append(f"Backstab {backstab_mult}x")
        
        # Lockpicking
        lockpick = self.get_lockpicking_skill()
        abilities.append(f"Lockpick {lockpick}")
        
        # High-level abilities
        if self.can_use_pressure_points():
            abilities.append("Pressure Points")
        if self.can_shadow_step():
            abilities.append(f"Shadow Step ({self.shadow_step_uses})")
        if self.get_assassination_chance() > 0:
            abilities.append(f"Assassinate {self.get_assassination_chance()}%")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str