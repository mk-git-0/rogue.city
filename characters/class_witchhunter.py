"""
Witchhunter Character Class for Rogue City
Traditional MajorMUD fanatical anti-magic specialist with supreme magic resistance.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Witchhunter(BaseCharacter):
    """
    Witchhunter class - Fanatical anti-magic zealot
    
    ANTI-MAGIC ZEALOT - Expert progression, extreme restrictions but incredible anti-magic power
    
    Experience Penalty: +70% (extreme restrictions but incredible anti-magic power)
    Stat Modifiers: +3 CON, +2 WIS, +2 STR, -3 INT, -2 CHA, -1 DEX
    Hit Die: d10 (high HP to survive without magic)
    Attack Speed: 3.5 seconds (moderate combat speed)
    Critical Range: 19-20 (improved critical vs spellcasters)
    
    SUPREME ANTI-MAGIC CORE:
    - Supreme magic resistance with near-immunity to spells
    - Anti-magic aura creating large area spell disruption field
    - Spell turning to reflect spells back at casters
    - Dispel magic ability to permanently destroy magical effects
    - Mage slayer providing massive bonus damage against spellcasters
    - Magic immunity granting complete immunity to specific spell types
    
    WITCHHUNTER ABILITIES:
    - Supreme Magic Resistance: Near-immunity to spells (+10 base)
    - Anti-Magic Aura: Large area spell disruption field
    - Spell Turning: Reflect spells back at casters
    - Dispel Magic: Permanently destroy magical effects
    - Mage Slayer: Massive bonus damage against spellcasters
    - Magic Immunity: Complete immunity to specific spell types
    
    EQUIPMENT RESTRICTIONS:
    - Cannot use ANY magical items, healing, or assistance
    - Non-magical items ONLY - refuses all magical aid
    - Enhanced effectiveness with masterwork non-magical equipment
    - Gains bonuses to compensate for lack of magical enhancement
    
    ZEALOT PHILOSOPHY:
    - Fanatical hatred of all magic and magical creatures
    - Cannot accept magical healing or assistance
    - Destroys magical items rather than using them
    - Views magic as corruption that must be purged
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Witchhunter character with supreme anti-magic systems"""
        super().__init__(name, 'witchhunter', race_id, alignment)
        
        # Supreme magic resistance system
        self.base_magic_resistance = 10 + self.level  # Starts at 11 at level 1
        self.magic_resistance_scaling = self._calculate_magic_resistance_scaling()
        self.spell_immunity_types = self._get_spell_immunities()
        
        # Anti-magic aura system
        self.anti_magic_aura_range = 15 + (self.level * 2)  # Feet
        self.aura_spell_failure_chance = 75 + self.level  # Percentage
        self.aura_item_malfunction_chance = 25  # Percentage per round
        self.permanent_aura = self.level >= 10
        
        # Spell turning and reflection
        self.spell_turning_uses = max(1, self.level // 4)
        self.spell_turning_used = 0
        self.spell_turning_chance = 50 + (self.level * 2)  # Percentage
        self.reflect_area_spells = self.level >= 16
        
        # Dispel magic mastery
        self.dispel_magic_uses = max(2, self.level // 3)
        self.dispel_magic_used = 0
        self.dispel_bonus = self._calculate_dispel_bonus()
        self.permanent_dispel = self.level >= 12
        
        # Mage slayer abilities
        self.mage_slayer_bonus = self._calculate_mage_slayer_bonus()
        self.detect_magic_active = True  # Always active
        self.spellcaster_sense_range = 120  # Feet
        self.spell_interruption = self.level >= 6
        
        # Magic immunity progression
        self.magic_immunity_list = self._calculate_magic_immunities()
        self.spell_resistance_penetration = 99  # Almost impossible to penetrate
        self.magic_item_destruction = True
        
        # Zealot philosophy and restrictions
        self.refuses_magical_healing = True
        self.refuses_magical_assistance = True
        self.destroys_magical_items = True
        self.zealot_bonus = self._calculate_zealot_bonus()
        
        # Compensation bonuses for lack of magic
        self.natural_armor_bonus = self._calculate_natural_armor()
        self.weapon_expertise_bonus = self._calculate_weapon_expertise()
        self.saving_throw_bonus = self._calculate_saving_throw_bonus()
        
    def get_hit_die_value(self) -> int:
        """Witchhunters use d10 hit die (high HP to survive without magic)"""
        return 10
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d10"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            # Witchhunters attack faster against spellcasters
            base_speed = self.equipment_system.get_attack_speed_modifier()
            return base_speed * 0.9  # 10% faster
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Witchhunters attack every 3.5 seconds unarmed (moderate speed)"""
        return 3.5
        
    def get_critical_range(self) -> int:
        """Witchhunters crit on 19-20 vs spellcasters, 20 vs others"""
        return 19  # Improved critical chance
        
    def get_experience_penalty(self) -> int:
        """Witchhunters have +70% experience penalty"""
        return 70
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Witchhunter special abilities"""
        return {
            # Supreme magic resistance
            'magic_resistance': self.get_total_magic_resistance(),
            'magic_resistance_scaling': self.magic_resistance_scaling,
            'spell_failure_chance': f"{self.get_spell_failure_chance()}%",
            'spell_immunity': self.spell_immunity_types.copy(),
            'spell_resistance_penetration': f"{self.spell_resistance_penetration}%",
            
            # Anti-magic aura
            'anti_magic_aura_range': self.anti_magic_aura_range,
            'aura_spell_failure': f"{self.aura_spell_failure_chance}%",
            'aura_item_malfunction': f"{self.aura_item_malfunction_chance}%",
            'permanent_aura': self.permanent_aura,
            'aura_affects_magical_creatures': True,
            
            # Spell turning and reflection
            'spell_turning': self.get_spell_turning_remaining(),
            'spell_turning_chance': f"{self.spell_turning_chance}%",
            'reflect_area_spells': self.reflect_area_spells,
            'spell_reflection_mastery': self.level >= 18,
            
            # Dispel magic mastery
            'dispel_magic': self.get_dispel_magic_remaining(),
            'dispel_bonus': self.get_dispel_bonus(),
            'permanent_dispel': self.permanent_dispel,
            'greater_dispel': self.level >= 15,
            'disjunction': self.level >= 20,
            
            # Mage slayer abilities
            'mage_slayer_bonus': self.get_mage_slayer_bonus(),
            'detect_magic': self.detect_magic_active,
            'spellcaster_sense_range': self.spellcaster_sense_range,
            'spell_interruption': self.spell_interruption,
            'mage_bane_weapons': self.level >= 8,
            
            # Magic immunity
            'magic_immunity_count': len(self.magic_immunity_list),
            'magic_immunity_list': self.magic_immunity_list.copy(),
            'blanket_immunity': self.level >= 18,
            
            # Zealot restrictions and bonuses
            'refuses_magical_healing': self.refuses_magical_healing,
            'refuses_magical_assistance': self.refuses_magical_assistance,
            'destroys_magical_items': self.destroys_magical_items,
            'zealot_bonus': self.get_zealot_bonus(),
            
            # Compensation bonuses
            'natural_armor_bonus': self.get_natural_armor_bonus(),
            'weapon_expertise': self.get_weapon_expertise_bonus(),
            'saving_throw_bonus': self.get_saving_throw_bonus(),
            'magic_item_immunity': True,
            
            # Combat abilities
            'improved_critical_vs_casters': True,
            'critical_range': self.get_critical_range(),
            'spell_disruption_attacks': self.level >= 4,
            'counterspell_master': self.level >= 10,
            
            # Equipment proficiencies
            'masterwork_weapon_mastery': True,
            'non_magical_item_expertise': True,
            'magical_item_destruction': self.magic_item_destruction
        }
    
    # === SUPREME MAGIC RESISTANCE ===
    
    def _calculate_magic_resistance_scaling(self) -> int:
        """Calculate magic resistance scaling bonus"""
        base_scaling = self.level // 5  # +1 every 5 levels
        con_bonus = max(0, (self.stats['constitution'] - 10) // 4)
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 4)
        return base_scaling + con_bonus + wis_bonus
    
    def get_total_magic_resistance(self) -> int:
        """Get total magic resistance"""
        base_mr = self.base_magic_resistance
        scaling_mr = self.magic_resistance_scaling
        return base_mr + scaling_mr
    
    def get_spell_failure_chance(self) -> int:
        """Get percentage chance for spells to fail"""
        mr = self.get_total_magic_resistance()
        # Convert MR to percentage (MR 20 = 95% failure, MR 30 = 99% failure)
        failure_chance = min(99, 75 + (mr * 2))
        return failure_chance
    
    def _get_spell_immunities(self) -> List[str]:
        """Get list of spell types with complete immunity"""
        immunities = []
        
        # Level-based immunities
        if self.level >= 3:
            immunities.append('charm')
        if self.level >= 5:
            immunities.append('fear')
        if self.level >= 7:
            immunities.append('enchantment')
        if self.level >= 9:
            immunities.append('illusion')
        if self.level >= 12:
            immunities.append('necromancy')
        if self.level >= 15:
            immunities.append('transmutation')
        if self.level >= 18:
            immunities.extend(['evocation', 'conjuration'])
        
        return immunities
    
    def is_immune_to_spell_type(self, spell_type: str) -> bool:
        """Check if immune to specific spell type"""
        return spell_type.lower() in [immunity.lower() for immunity in self.spell_immunity_types]
    
    def resist_spell(self, spell_level: int, caster_level: int = 1) -> Dict[str, Any]:
        """Resist incoming spell"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            resistance_roll = dice.roll("1d100")
            
            failure_chance = self.get_spell_failure_chance()
            # Higher level spells have slight bonus to penetrate
            penetration_bonus = max(0, spell_level - self.level // 3)
            adjusted_failure_chance = max(50, failure_chance - penetration_bonus)
            
            spell_failed = resistance_roll <= adjusted_failure_chance
            
            return {
                'spell_failed': spell_failed,
                'resistance_roll': resistance_roll,
                'failure_chance': adjusted_failure_chance,
                'magic_resistance': self.get_total_magic_resistance(),
                'penetration_bonus': penetration_bonus
            }
        except ImportError:
            import random
            spell_failed = random.randint(1, 100) <= self.get_spell_failure_chance()
            return {'spell_failed': spell_failed, 'magic_resistance': self.get_total_magic_resistance()}
    
    # === ANTI-MAGIC AURA ===
    
    def has_anti_magic_aura(self) -> bool:
        """Check if anti-magic aura is active"""
        return self.level >= 1  # Always active
    
    def get_aura_effects_on_spell(self, spell_level: int, distance: int) -> Dict[str, Any]:
        """Get aura effects on spell cast within range"""
        if distance > self.anti_magic_aura_range:
            return {'affected': False, 'reason': 'Outside aura range'}
        
        if not self.has_anti_magic_aura():
            return {'affected': False, 'reason': 'No aura active'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            aura_roll = dice.roll("1d100")
            
            # Base failure chance from aura
            failure_chance = self.aura_spell_failure_chance
            # Closer to witchhunter = higher failure chance
            distance_modifier = max(0, (self.anti_magic_aura_range - distance) * 2)
            total_failure_chance = min(95, failure_chance + distance_modifier)
            
            spell_disrupted = aura_roll <= total_failure_chance
            
            return {
                'affected': True,
                'spell_disrupted': spell_disrupted,
                'aura_roll': aura_roll,
                'failure_chance': total_failure_chance,
                'distance': distance,
                'aura_range': self.anti_magic_aura_range
            }
        except ImportError:
            import random
            spell_disrupted = random.randint(1, 100) <= self.aura_spell_failure_chance
            return {'affected': True, 'spell_disrupted': spell_disrupted}
    
    def get_aura_effects_on_magic_item(self, item, rounds_in_aura: int = 1) -> Dict[str, Any]:
        """Get aura effects on magical items"""
        if not self.has_anti_magic_aura():
            return {'affected': False}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            
            malfunctions = 0
            for _ in range(rounds_in_aura):
                malfunction_roll = dice.roll("1d100")
                if malfunction_roll <= self.aura_item_malfunction_chance:
                    malfunctions += 1
            
            # Permanent destruction chance at high levels
            destruction_chance = 0
            if self.level >= 15:
                destruction_chance = 5  # 5% per round at high level
                destruction_roll = dice.roll("1d100")
                permanently_destroyed = destruction_roll <= destruction_chance
            else:
                permanently_destroyed = False
            
            return {
                'affected': True,
                'malfunctions': malfunctions,
                'temporarily_suppressed': malfunctions > 0,
                'permanently_destroyed': permanently_destroyed,
                'destruction_chance': destruction_chance,
                'aura_strength': self.aura_item_malfunction_chance
            }
        except ImportError:
            import random
            malfunctions = sum(1 for _ in range(rounds_in_aura) 
                             if random.randint(1, 100) <= self.aura_item_malfunction_chance)
            return {'affected': True, 'malfunctions': malfunctions}
    
    # === SPELL TURNING AND REFLECTION ===
    
    def get_spell_turning_remaining(self) -> int:
        """Get spell turning uses remaining"""
        return max(0, self.spell_turning_uses - self.spell_turning_used)
    
    def can_turn_spell(self) -> bool:
        """Check if witchhunter can turn spells"""
        return self.get_spell_turning_remaining() > 0
    
    def attempt_spell_turning(self, spell_level: int, area_spell: bool = False) -> Dict[str, Any]:
        """Attempt to turn spell back at caster"""
        if not self.can_turn_spell():
            return {'success': False, 'reason': 'No spell turning uses remaining'}
        
        # Area spells require higher level ability
        if area_spell and not self.reflect_area_spells:
            return {'success': False, 'reason': 'Cannot reflect area spells yet'}
        
        self.spell_turning_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            turning_roll = dice.roll("1d100")
            
            # Base chance to turn
            turn_chance = self.spell_turning_chance
            # Higher level spells harder to turn
            spell_penalty = spell_level * 5
            # Area spells harder to turn
            area_penalty = 20 if area_spell else 0
            
            final_chance = max(10, turn_chance - spell_penalty - area_penalty)
            success = turning_roll <= final_chance
            
            return {
                'success': success,
                'turning_roll': turning_roll,
                'turn_chance': final_chance,
                'spell_reflected': success,
                'spell_level': spell_level,
                'area_spell': area_spell,
                'remaining_uses': self.get_spell_turning_remaining()
            }
        except ImportError:
            import random
            success = random.randint(1, 100) <= (self.spell_turning_chance - spell_level * 5)
            return {
                'success': success,
                'spell_reflected': success,
                'remaining_uses': self.get_spell_turning_remaining()
            }
    
    def has_spell_reflection_mastery(self) -> bool:
        """Check if witchhunter has spell reflection mastery"""
        return self.level >= 18
    
    # === DISPEL MAGIC MASTERY ===
    
    def get_dispel_magic_remaining(self) -> int:
        """Get dispel magic uses remaining"""
        return max(0, self.dispel_magic_uses - self.dispel_magic_used)
    
    def _calculate_dispel_bonus(self) -> int:
        """Calculate dispel magic bonus"""
        base_bonus = 5
        level_bonus = self.level
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        return base_bonus + level_bonus + wis_bonus
    
    def get_dispel_bonus(self) -> int:
        """Get dispel magic bonus"""
        return self._calculate_dispel_bonus()
    
    def can_dispel_magic(self) -> bool:
        """Check if witchhunter can dispel magic"""
        return self.get_dispel_magic_remaining() > 0
    
    def attempt_dispel_magic(self, target_caster_level: int, permanent: bool = False) -> Dict[str, Any]:
        """Attempt to dispel magical effects"""
        if not self.can_dispel_magic():
            return {'success': False, 'reason': 'No dispel magic uses remaining'}
        
        # Permanent dispel requires higher level
        if permanent and not self.permanent_dispel:
            permanent = False
        
        self.dispel_magic_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            dispel_roll = dice.roll("1d20") + self.get_dispel_bonus()
            
            # DC based on target caster level
            dispel_dc = 11 + target_caster_level
            success = dispel_roll >= dispel_dc
            
            # Permanent dispel is harder but destroys magic permanently
            if permanent:
                dispel_dc += 5
                success = dispel_roll >= dispel_dc
            
            return {
                'success': success,
                'dispel_roll': dispel_roll,
                'dispel_dc': dispel_dc,
                'dispel_bonus': self.get_dispel_bonus(),
                'permanent_dispel': permanent and success,
                'target_caster_level': target_caster_level,
                'remaining_uses': self.get_dispel_magic_remaining()
            }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.get_dispel_bonus() >= (11 + target_caster_level)
            return {
                'success': success,
                'permanent_dispel': permanent and success,
                'remaining_uses': self.get_dispel_magic_remaining()
            }
    
    def can_greater_dispel(self) -> bool:
        """Check if witchhunter can use greater dispel"""
        return self.level >= 15
    
    def can_disjunction(self) -> bool:
        """Check if witchhunter can use disjunction"""
        return self.level >= 20
    
    # === MAGE SLAYER ABILITIES ===
    
    def _calculate_mage_slayer_bonus(self) -> int:
        """Calculate mage slayer damage bonus"""
        base_bonus = 3
        level_bonus = self.level // 2
        str_bonus = max(0, (self.stats['strength'] - 10) // 4)
        return base_bonus + level_bonus + str_bonus
    
    def get_mage_slayer_bonus(self) -> int:
        """Get mage slayer damage bonus vs spellcasters"""
        return self._calculate_mage_slayer_bonus()
    
    def detect_spellcaster(self, target_caster_level: int = 0, distance: int = 60) -> Dict[str, Any]:
        """Detect spellcasters in range"""
        if not self.detect_magic_active:
            return {'detected': False, 'reason': 'Detect magic not active'}
        
        if distance > self.spellcaster_sense_range:
            return {'detected': False, 'reason': 'Target too far'}
        
        is_spellcaster = target_caster_level > 0
        
        return {
            'detected': is_spellcaster,
            'caster_level': target_caster_level if is_spellcaster else 0,
            'distance': distance,
            'sense_range': self.spellcaster_sense_range,
            'magical_aura_strength': 'strong' if target_caster_level >= 10 else 'moderate' if target_caster_level >= 5 else 'weak'
        }
    
    def can_interrupt_spells(self) -> bool:
        """Check if witchhunter can interrupt spellcasting"""
        return self.spell_interruption
    
    def attempt_spell_interruption(self, target_concentration: int) -> Dict[str, Any]:
        """Attempt to interrupt enemy spellcasting"""
        if not self.can_interrupt_spells():
            return {'success': False, 'reason': 'Spell interruption not available'}
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            
            # Attack roll to hit for interruption
            attack_bonus = self.base_attack_bonus + self.get_mage_slayer_bonus()
            attack_roll = dice.roll("1d20") + attack_bonus
            
            # Must beat AC and cause concentration check
            hit_success = attack_roll >= 15  # Assume moderate AC
            
            if hit_success:
                # Force concentration check
                damage = dice.roll("1d6") + self.get_mage_slayer_bonus()
                concentration_dc = 10 + damage
                interrupted = target_concentration < concentration_dc
                
                return {
                    'success': hit_success,
                    'attack_roll': attack_roll,
                    'damage': damage,
                    'concentration_dc': concentration_dc,
                    'spell_interrupted': interrupted,
                    'mage_slayer_bonus': self.get_mage_slayer_bonus()
                }
            else:
                return {
                    'success': False,
                    'attack_roll': attack_roll,
                    'missed_attack': True
                }
        except ImportError:
            import random
            success = random.randint(1, 20) + self.base_attack_bonus >= 15
            return {'success': success, 'spell_interrupted': success}
    
    def has_mage_bane_weapons(self) -> bool:
        """Check if witchhunter can create mage bane weapons"""
        return self.level >= 8
    
    # === ZEALOT RESTRICTIONS AND BONUSES ===
    
    def _calculate_zealot_bonus(self) -> int:
        """Calculate zealot philosophy bonus"""
        base_bonus = 2
        level_bonus = self.level // 4
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 4)
        return base_bonus + level_bonus + wis_bonus
    
    def get_zealot_bonus(self) -> int:
        """Get zealot bonus to anti-magic abilities"""
        return self._calculate_zealot_bonus()
    
    def can_accept_magical_healing(self) -> bool:
        """Check if witchhunter can accept magical healing"""
        return not self.refuses_magical_healing
    
    def can_use_magical_items(self) -> bool:
        """Check if witchhunter can use magical items"""
        return False  # Never can use magical items
    
    def destroys_magic_items_on_contact(self) -> bool:
        """Check if witchhunter destroys magical items on contact"""
        return self.destroys_magical_items
    
    def destroy_magical_item(self, item) -> Dict[str, Any]:
        """Destroy magical item on contact"""
        if not self.destroys_magic_items_on_contact():
            return {'destroyed': False, 'reason': 'Does not destroy magical items'}
        
        # Chance to destroy based on item power and witchhunter level
        item_power = getattr(item, 'caster_level', 5)  # Default power level
        destruction_chance = min(95, 50 + self.level - item_power)
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            destroy_roll = dice.roll("1d100")
            destroyed = destroy_roll <= destruction_chance
            
            return {
                'destroyed': destroyed,
                'destroy_roll': destroy_roll,
                'destruction_chance': destruction_chance,
                'item_power': item_power,
                'witchhunter_level': self.level
            }
        except ImportError:
            import random
            destroyed = random.randint(1, 100) <= destruction_chance
            return {'destroyed': destroyed, 'destruction_chance': destruction_chance}
    
    # === COMPENSATION BONUSES ===
    
    def _calculate_natural_armor(self) -> int:
        """Calculate natural armor bonus to compensate for no magical armor"""
        base_bonus = 2
        level_bonus = self.level // 4
        con_bonus = max(0, (self.stats['constitution'] - 10) // 6)
        return base_bonus + level_bonus + con_bonus
    
    def get_natural_armor_bonus(self) -> int:
        """Get natural armor bonus"""
        return self._calculate_natural_armor()
    
    def _calculate_weapon_expertise(self) -> int:
        """Calculate weapon expertise bonus to compensate for no magical weapons"""
        base_bonus = 1
        level_bonus = self.level // 3
        str_bonus = max(0, (self.stats['strength'] - 10) // 6)
        return base_bonus + level_bonus + str_bonus
    
    def get_weapon_expertise_bonus(self) -> int:
        """Get weapon expertise bonus"""
        return self._calculate_weapon_expertise()
    
    def _calculate_saving_throw_bonus(self) -> int:
        """Calculate saving throw bonus"""
        base_bonus = 3
        level_bonus = self.level // 3
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 4)
        return base_bonus + level_bonus + wis_bonus
    
    def get_saving_throw_bonus(self) -> int:
        """Get saving throw bonus"""
        return self._calculate_saving_throw_bonus()
    
    def _calculate_magic_immunities(self) -> List[str]:
        """Calculate current magic immunities"""
        return self._get_spell_immunities()
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Witchhunters can use any non-magical weapon"""
        if hasattr(weapon, 'is_magical') and weapon.is_magical:
            return False  # Cannot use magical weapons
        return True
    
    def can_use_armor(self, armor) -> bool:
        """Witchhunters can use any non-magical armor"""
        if hasattr(armor, 'is_magical') and armor.is_magical:
            return False  # Cannot use magical armor
        return True
    
    def can_equip_item(self, item) -> Tuple[bool, str]:
        """Check if witchhunter can equip an item"""
        # Check for magical items (forbidden)
        if hasattr(item, 'is_magical') and item.is_magical:
            return False, "Witchhunters cannot use magical items - destroys them instead"
        
        # Witchhunters get bonuses with masterwork non-magical items
        if hasattr(item, 'quality') and item.quality == 'masterwork':
            return True, "Masterwork item - enhanced effectiveness"
        
        return True, "Non-magical equipment allowed"
    
    def calculate_derived_stats(self):
        """Override to include compensation bonuses"""
        super().calculate_derived_stats()
        
        # Add natural armor bonus
        self.armor_class += self.get_natural_armor_bonus()
        
        # Add weapon expertise to attack bonus
        self.base_attack_bonus += self.get_weapon_expertise_bonus()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Witchhunter':
        """Create Witchhunter from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        witchhunter = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        witchhunter.level = data['level']
        witchhunter.experience = data['experience']
        witchhunter.base_stats = data.get('base_stats', witchhunter.base_stats)
        witchhunter.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        witchhunter.max_hp = derived['max_hp']
        witchhunter.current_hp = derived['current_hp']
        witchhunter.armor_class = derived['armor_class']
        witchhunter.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        witchhunter.current_area = location.get('area_id')
        witchhunter.current_room = location.get('room_id')
        
        # Initialize item systems
        witchhunter.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            witchhunter.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            witchhunter.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        witchhunter.unallocated_stats = data.get('unallocated_stats', 0)
        witchhunter.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            witchhunter.load_alignment_data(data['alignment_data'])
        
        # Restore witchhunter-specific attributes
        witchhunter_data = data.get('witchhunter_data', {})
        witchhunter.spell_turning_used = witchhunter_data.get('spell_turning_used', 0)
        witchhunter.dispel_magic_used = witchhunter_data.get('dispel_magic_used', 0)
        
        # Recalculate witchhunter-specific attributes
        witchhunter.base_magic_resistance = 10 + witchhunter.level
        witchhunter.magic_resistance_scaling = witchhunter._calculate_magic_resistance_scaling()
        witchhunter.spell_immunity_types = witchhunter._get_spell_immunities()
        witchhunter.anti_magic_aura_range = 15 + (witchhunter.level * 2)
        witchhunter.aura_spell_failure_chance = 75 + witchhunter.level
        witchhunter.permanent_aura = witchhunter.level >= 10
        witchhunter.spell_turning_uses = max(1, witchhunter.level // 4)
        witchhunter.spell_turning_chance = 50 + (witchhunter.level * 2)
        witchhunter.reflect_area_spells = witchhunter.level >= 16
        witchhunter.dispel_magic_uses = max(2, witchhunter.level // 3)
        witchhunter.dispel_bonus = witchhunter._calculate_dispel_bonus()
        witchhunter.permanent_dispel = witchhunter.level >= 12
        witchhunter.mage_slayer_bonus = witchhunter._calculate_mage_slayer_bonus()
        witchhunter.spellcaster_sense_range = 120
        witchhunter.spell_interruption = witchhunter.level >= 6
        witchhunter.magic_immunity_list = witchhunter._calculate_magic_immunities()
        witchhunter.zealot_bonus = witchhunter._calculate_zealot_bonus()
        witchhunter.natural_armor_bonus = witchhunter._calculate_natural_armor()
        witchhunter.weapon_expertise_bonus = witchhunter._calculate_weapon_expertise()
        witchhunter.saving_throw_bonus = witchhunter._calculate_saving_throw_bonus()
        
        return witchhunter
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include witchhunter-specific data"""
        data = super().to_dict()
        data['witchhunter_data'] = {
            'spell_turning_used': self.spell_turning_used,
            'dispel_magic_used': self.dispel_magic_used
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Witchhunter"""
        abilities = []
        
        # Magic resistance
        mr = self.get_total_magic_resistance()
        spell_failure = self.get_spell_failure_chance()
        abilities.append(f"MR {mr} ({spell_failure}%)")
        
        # Anti-magic aura
        aura_range = self.anti_magic_aura_range
        abilities.append(f"Aura {aura_range}ft")
        
        # Spell turning
        turning_remaining = self.get_spell_turning_remaining()
        if turning_remaining > 0:
            abilities.append(f"Turn {turning_remaining}")
        
        # Dispel magic
        dispel_remaining = self.get_dispel_magic_remaining()
        dispel_bonus = self.get_dispel_bonus()
        abilities.append(f"Dispel {dispel_remaining} (+{dispel_bonus})")
        
        # Mage slayer
        mage_slayer = self.get_mage_slayer_bonus()
        abilities.append(f"Mage Slayer +{mage_slayer}")
        
        # Immunities
        immunity_count = len(self.magic_immunity_list)
        abilities.append(f"{immunity_count} Immunities")
        
        # High-level abilities
        if self.permanent_aura:
            abilities.append("Permanent Aura")
        if self.can_greater_dispel():
            abilities.append("Greater Dispel")
        if self.can_disjunction():
            abilities.append("Disjunction")
        if self.has_spell_reflection_mastery():
            abilities.append("Reflection Master")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str