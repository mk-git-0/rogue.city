"""
Missionary Character Class for Rogue City
Traditional MajorMUD traveling healer and spreader of faith.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Missionary(BaseCharacter):
    """
    Missionary class - Divine healer and spreader of faith
    
    DIVINE HEALER - Moderate progression, healing-focused
    
    Experience Penalty: +20% (healing magic requires more experience)
    Alignment Restriction: Good or Neutral (cannot be Evil)
    Stat Modifiers: +3 WIS, +2 CHA, +1 CON, -2 STR, -2 DEX
    Hit Die: d8 (moderate HP progression)
    Attack Speed: 4.0 seconds (slower combat speed)
    Critical Range: 20 (standard critical chance)
    
    DIVINE HEALING CORE:
    - Superior healing magic with enhanced effectiveness
    - Cure disease and remove curses abilities
    - Sanctuary ability to become untargetable
    - Bless magic to improve allies' combat effectiveness
    - Turn undead through faith rather than combat
    - Divine protection and resistance to evil magic
    
    MISSIONARY ABILITIES:
    - Superior Healing: Enhanced effectiveness of all healing magic
    - Cure Disease: Remove diseases and curses
    - Sanctuary: Become untargetable for short periods
    - Bless: Improve allies' combat effectiveness
    - Turn Undead: Repel undead through faith
    - Divine Protection: Resistance to evil magic and attacks
    
    EQUIPMENT ACCESS:
    - Weapons: Simple weapons and holy symbols
    - Armor: Light armor and robes
    - Magic: Can use holy and blessed magical items
    - Accessories: Holy symbols, healing items, blessed accessories
    
    ALIGNMENT REQUIREMENT:
    - Must be Good or Neutral alignment
    - Cannot be Evil (loses healing abilities if Evil)
    - Receives bonuses when helping others
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.GOOD):
        """Initialize Missionary character with divine healing systems"""
        # Prevent Evil alignment for Missionaries
        if alignment == Alignment.EVIL:
            alignment = Alignment.NEUTRAL
            
        super().__init__(name, 'missionary', race_id, alignment)
        
        # Divine healing attributes
        self.healing_pool = self._calculate_healing_pool()
        self.healing_used = 0
        self.healing_bonus = self._calculate_healing_bonus()
        
        # Disease and curse removal
        self.cure_disease_uses = max(1, self.level // 2)
        self.cure_disease_used = 0
        self.remove_curse_uses = max(1, self.level // 4)
        self.remove_curse_used = 0
        
        # Sanctuary and protection abilities
        self.sanctuary_uses = max(1, self.level // 3)
        self.sanctuary_used = 0
        self.sanctuary_active = False
        self.sanctuary_duration = 0
        
        # Blessing abilities
        self.bless_uses = max(2, self.level // 2)
        self.bless_used = 0
        self.bless_bonus = self._calculate_bless_bonus()
        
        # Turn undead (weaker than Paladin)
        self.turn_undead_uses = max(1, self.level // 3)
        self.turn_undead_used = 0
        
        # Divine protection
        self.divine_protection_bonus = self._calculate_divine_protection()
        self.evil_resistance = 3  # +3 resistance to evil effects
        
    def get_hit_die_value(self) -> int:
        """Missionaries use d8 hit die (moderate HP progression)"""
        return 8
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d8"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Missionaries attack every 4 seconds unarmed (slower, focused on healing)"""
        return 4.0
        
    def get_critical_range(self) -> int:
        """Missionaries crit on natural 20 (standard critical)"""
        return 20
        
    def get_experience_penalty(self) -> int:
        """Missionaries have +20% experience penalty"""
        return 20
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Missionary special abilities"""
        # Check if Evil aligned (lose healing abilities)
        if self.get_alignment() == Alignment.EVIL:
            return {
                'lost_faith': True,
                'abilities_lost': 'All divine abilities lost due to evil alignment',
                'equipment_proficiency': True  # Still retains basic training
            }
        
        return {
            # Divine healing
            'superior_healing': self.get_healing_remaining(),
            'healing_pool': self.get_healing_pool(),
            'healing_bonus': self.get_healing_bonus(),
            'mass_healing': self.level >= 8,
            'resurrection': self.level >= 12,
            
            # Disease and curse removal
            'cure_disease': self.get_cure_disease_remaining(),
            'remove_curse': self.get_remove_curse_remaining(),
            'neutralize_poison': self.level >= 5,
            'break_enchantment': self.level >= 10,
            
            # Sanctuary and protection
            'sanctuary': self.get_sanctuary_remaining(),
            'sanctuary_active': self.sanctuary_active,
            'divine_protection': self.get_divine_protection_bonus(),
            'protection_from_evil': True,
            'spell_resistance': self.level >= 6,
            
            # Blessing abilities
            'bless': self.get_bless_remaining(),
            'bless_bonus': self.get_bless_bonus(),
            'consecrate': self.level >= 7,
            'holy_aura': self.level >= 15,
            
            # Turn undead (faith-based)
            'turn_undead': self.get_turn_undead_remaining(),
            'turn_undead_level': self.get_turn_undead_level(),
            'command_undead': False,  # Missionaries repel, not command
            
            # Divine resistances
            'evil_resistance': self.evil_resistance,
            'disease_resistance': 4,
            'charm_resistance': 2,
            'death_resistance': self.level >= 8,
            
            # Social abilities
            'divine_guidance': True,
            'detect_evil': True,
            'know_alignment': self.level >= 3,
            'zone_of_truth': self.level >= 5,
            
            # Equipment proficiencies
            'simple_weapon_proficiency': True,
            'light_armor_proficiency': True,
            'holy_symbol_mastery': True
        }
    
    # === DIVINE HEALING ABILITIES ===
    
    def _calculate_healing_pool(self) -> int:
        """Calculate total healing pool per day"""
        base_pool = self.level * 4  # 4 HP per level (better than Paladin)
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        return base_pool + (wis_bonus * self.level) + (cha_bonus * self.level // 2)
    
    def get_healing_pool(self) -> int:
        """Get total healing pool"""
        return self._calculate_healing_pool()
    
    def get_healing_remaining(self) -> int:
        """Get healing pool remaining"""
        return max(0, self.get_healing_pool() - self.healing_used)
    
    def _calculate_healing_bonus(self) -> int:
        """Calculate healing effectiveness bonus"""
        base_bonus = 2  # +2 to all healing
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 2)
        level_bonus = self.level // 4
        return base_bonus + wis_bonus + level_bonus
    
    def get_healing_bonus(self) -> int:
        """Get healing effectiveness bonus"""
        return self._calculate_healing_bonus()
    
    def can_heal(self, amount: int = 1) -> bool:
        """Check if missionary can use healing"""
        if self.get_alignment() == Alignment.EVIL:
            return False
        return self.get_healing_remaining() >= amount
    
    def use_superior_healing(self, base_amount: int, target=None) -> Dict[str, Any]:
        """Use superior healing with bonus effectiveness"""
        if not self.can_heal(base_amount):
            return {'success': False, 'reason': 'Insufficient healing pool'}
        
        if target is None:
            target = self
        
        # Apply healing bonus
        total_healing = base_amount + self.get_healing_bonus()
        self.healing_used += base_amount
        healing_done = target.heal(total_healing)
        
        return {
            'success': True,
            'base_healing': base_amount,
            'bonus_healing': self.get_healing_bonus(),
            'total_healing': total_healing,
            'healing_done': healing_done,
            'target': target.name,
            'remaining_pool': self.get_healing_remaining()
        }
    
    def can_mass_heal(self) -> bool:
        """Check if missionary can use mass healing"""
        return self.level >= 8 and self.get_alignment() != Alignment.EVIL
    
    def use_mass_healing(self, targets: List, amount_per_target: int) -> Dict[str, Any]:
        """Heal multiple targets simultaneously"""
        if not self.can_mass_heal():
            return {'success': False, 'reason': 'Mass healing not available'}
        
        total_cost = len(targets) * amount_per_target
        if not self.can_heal(total_cost):
            return {'success': False, 'reason': 'Insufficient healing pool'}
        
        self.healing_used += total_cost
        results = []
        
        for target in targets:
            enhanced_amount = amount_per_target + self.get_healing_bonus()
            healing_done = target.heal(enhanced_amount)
            results.append({
                'target': target.name,
                'healing_done': healing_done
            })
        
        return {
            'success': True,
            'targets_healed': len(targets),
            'results': results,
            'remaining_pool': self.get_healing_remaining()
        }
    
    # === CURE DISEASE AND CURSE REMOVAL ===
    
    def get_cure_disease_remaining(self) -> int:
        """Get cure disease uses remaining"""
        return max(0, self.cure_disease_uses - self.cure_disease_used)
    
    def can_cure_disease(self) -> bool:
        """Check if missionary can cure disease"""
        if self.get_alignment() == Alignment.EVIL:
            return False
        return self.get_cure_disease_remaining() > 0
    
    def cure_disease(self, target=None) -> Dict[str, Any]:
        """Cure disease on target"""
        if not self.can_cure_disease():
            return {'success': False, 'reason': 'No cure disease uses remaining'}
        
        self.cure_disease_used += 1
        
        return {
            'success': True,
            'target': target.name if target else self.name,
            'diseases_cured': True,
            'remaining_uses': self.get_cure_disease_remaining()
        }
    
    def get_remove_curse_remaining(self) -> int:
        """Get remove curse uses remaining"""
        return max(0, self.remove_curse_uses - self.remove_curse_used)
    
    def can_remove_curse(self) -> bool:
        """Check if missionary can remove curses"""
        if self.get_alignment() == Alignment.EVIL:
            return False
        return self.get_remove_curse_remaining() > 0
    
    def remove_curse(self, target=None) -> Dict[str, Any]:
        """Remove curse from target"""
        if not self.can_remove_curse():
            return {'success': False, 'reason': 'No remove curse uses remaining'}
        
        self.remove_curse_used += 1
        
        return {
            'success': True,
            'target': target.name if target else self.name,
            'curses_removed': True,
            'remaining_uses': self.get_remove_curse_remaining()
        }
    
    def can_neutralize_poison(self) -> bool:
        """Check if missionary can neutralize poison"""
        return self.level >= 5 and self.get_alignment() != Alignment.EVIL
    
    def neutralize_poison(self, target=None) -> bool:
        """Neutralize poison in target"""
        if not self.can_neutralize_poison():
            return False
        
        # Uses healing pool
        cost = 5
        if not self.can_heal(cost):
            return False
        
        self.healing_used += cost
        return True
    
    # === SANCTUARY AND PROTECTION ABILITIES ===
    
    def get_sanctuary_remaining(self) -> int:
        """Get sanctuary uses remaining"""
        return max(0, self.sanctuary_uses - self.sanctuary_used)
    
    def can_use_sanctuary(self) -> bool:
        """Check if missionary can use sanctuary"""
        if self.get_alignment() == Alignment.EVIL:
            return False
        return self.get_sanctuary_remaining() > 0 and not self.sanctuary_active
    
    def activate_sanctuary(self) -> Dict[str, Any]:
        """Activate sanctuary protection"""
        if not self.can_use_sanctuary():
            return {'success': False, 'reason': 'Cannot use sanctuary'}
        
        self.sanctuary_used += 1
        self.sanctuary_active = True
        self.sanctuary_duration = 5 + self.level  # 5 + level rounds
        
        return {
            'success': True,
            'duration': self.sanctuary_duration,
            'effect': 'Untargetable by hostile actions',
            'remaining_uses': self.get_sanctuary_remaining()
        }
    
    def _calculate_divine_protection(self) -> int:
        """Calculate divine protection bonus"""
        base_bonus = 1
        wis_bonus = max(0, (self.stats['wisdom'] - 10) // 4)
        level_bonus = self.level // 6
        return base_bonus + wis_bonus + level_bonus
    
    def get_divine_protection_bonus(self) -> int:
        """Get divine protection AC bonus"""
        if self.get_alignment() == Alignment.EVIL:
            return 0
        return self._calculate_divine_protection()
    
    def has_spell_resistance(self) -> bool:
        """Check if missionary has spell resistance"""
        return self.level >= 6 and self.get_alignment() != Alignment.EVIL
    
    def get_spell_resistance(self) -> int:
        """Get spell resistance value"""
        if not self.has_spell_resistance():
            return 0
        return 10 + self.level
    
    # === BLESSING ABILITIES ===
    
    def get_bless_remaining(self) -> int:
        """Get bless uses remaining"""
        return max(0, self.bless_uses - self.bless_used)
    
    def _calculate_bless_bonus(self) -> int:
        """Calculate bless effectiveness"""
        base_bonus = 1
        if self.level >= 8:
            base_bonus = 2
        if self.level >= 15:
            base_bonus = 3
        return base_bonus
    
    def get_bless_bonus(self) -> int:
        """Get bless bonus value"""
        return self._calculate_bless_bonus()
    
    def can_bless(self) -> bool:
        """Check if missionary can bless"""
        if self.get_alignment() == Alignment.EVIL:
            return False
        return self.get_bless_remaining() > 0
    
    def bless_target(self, target=None) -> Dict[str, Any]:
        """Bless a target with divine favor"""
        if not self.can_bless():
            return {'success': False, 'reason': 'No bless uses remaining'}
        
        self.bless_used += 1
        bonus = self.get_bless_bonus()
        
        return {
            'success': True,
            'target': target.name if target else self.name,
            'attack_bonus': bonus,
            'save_bonus': bonus,
            'skill_bonus': bonus,
            'duration_minutes': 10 * self.level,
            'remaining_uses': self.get_bless_remaining()
        }
    
    def can_consecrate(self) -> bool:
        """Check if missionary can consecrate area"""
        return self.level >= 7 and self.get_alignment() != Alignment.EVIL
    
    def consecrate_area(self) -> Dict[str, Any]:
        """Consecrate the current area"""
        if not self.can_consecrate():
            return {'success': False, 'reason': 'Consecrate not available'}
        
        return {
            'success': True,
            'effect': 'Area blessed against undead and evil',
            'undead_penalty': -2,
            'duration_hours': self.level,
            'area_size': f"{10 * self.level} foot radius"
        }
    
    # === TURN UNDEAD (FAITH-BASED) ===
    
    def get_turn_undead_remaining(self) -> int:
        """Get turn undead uses remaining"""
        return max(0, self.turn_undead_uses - self.turn_undead_used)
    
    def get_turn_undead_level(self) -> int:
        """Get effective cleric level for turning (weaker than Paladin)"""
        return max(1, self.level - 2)  # -2 levels compared to Paladin
    
    def can_turn_undead(self) -> bool:
        """Check if missionary can turn undead"""
        if self.get_alignment() == Alignment.EVIL:
            return False
        return self.get_turn_undead_remaining() > 0
    
    def attempt_turn_undead(self, undead_hd: int) -> Dict[str, Any]:
        """Attempt to turn undead through faith"""
        if not self.can_turn_undead():
            return {'success': False, 'reason': 'No turn attempts remaining'}
        
        self.turn_undead_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            turn_roll = dice.roll("1d20")
            turn_level = self.get_turn_undead_level()
            
            # Calculate turn difficulty (harder than Paladin)
            turn_dc = 12 + undead_hd - turn_level
            success = turn_roll >= turn_dc
            
            return {
                'success': success,
                'destroyed': False,  # Missionaries repel, don't destroy
                'turn_roll': turn_roll,
                'turn_dc': turn_dc,
                'remaining_uses': self.get_turn_undead_remaining()
            }
        except ImportError:
            import random
            success = random.randint(1, 20) >= (12 + undead_hd - self.get_turn_undead_level())
            return {
                'success': success,
                'destroyed': False,
                'remaining_uses': self.get_turn_undead_remaining()
            }
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Missionaries can use simple weapons"""
        if hasattr(weapon, 'weapon_category'):
            return weapon.weapon_category.lower() in ['simple']
        if hasattr(weapon, 'weapon_type'):
            allowed_types = ['staff', 'club', 'dagger', 'sling', 'crossbow']
            return weapon.weapon_type.lower() in allowed_types
        return True  # Default allow for basic weapons
    
    def can_use_armor(self, armor) -> bool:
        """Missionaries can use light armor"""
        if hasattr(armor, 'armor_type'):
            allowed_types = ['light', 'leather', 'cloth', 'robes']
            return armor.armor_type.lower() in allowed_types
        return True  # Default allow for basic armor
    
    def can_equip_item(self, item) -> Tuple[bool, str]:
        """Check if missionary can equip an item"""
        # Check for evil items
        if hasattr(item, 'alignment') and item.alignment == 'evil':
            return False, "Missionaries cannot use evil-aligned items"
        
        # Missionaries get bonuses with holy/healing items
        if hasattr(item, 'alignment') and item.alignment in ['good', 'holy', 'blessed']:
            return True, "Holy item - receives divine blessing"
        
        if hasattr(item, 'item_type') and 'healing' in item.item_type.lower():
            return True, "Healing item - enhanced effectiveness"
        
        return True, "Equipment allowed"
    
    def calculate_derived_stats(self):
        """Override to include divine protection bonus"""
        super().calculate_derived_stats()
        
        # Add divine protection AC bonus
        if self.get_alignment() != Alignment.EVIL:
            self.armor_class += self.get_divine_protection_bonus()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Missionary':
        """Create Missionary from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to good
        alignment = Alignment.GOOD
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'GOOD')
            alignment = getattr(Alignment, alignment_name, Alignment.GOOD)
        
        missionary = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        missionary.level = data['level']
        missionary.experience = data['experience']
        missionary.base_stats = data.get('base_stats', missionary.base_stats)
        missionary.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        missionary.max_hp = derived['max_hp']
        missionary.current_hp = derived['current_hp']
        missionary.armor_class = derived['armor_class']
        missionary.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        missionary.current_area = location.get('area_id')
        missionary.current_room = location.get('room_id')
        
        # Initialize item systems
        missionary.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            missionary.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            missionary.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        missionary.unallocated_stats = data.get('unallocated_stats', 0)
        missionary.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            missionary.load_alignment_data(data['alignment_data'])
        
        # Restore missionary-specific attributes
        missionary_data = data.get('missionary_data', {})
        missionary.healing_used = missionary_data.get('healing_used', 0)
        missionary.cure_disease_used = missionary_data.get('cure_disease_used', 0)
        missionary.remove_curse_used = missionary_data.get('remove_curse_used', 0)
        missionary.sanctuary_used = missionary_data.get('sanctuary_used', 0)
        missionary.bless_used = missionary_data.get('bless_used', 0)
        missionary.turn_undead_used = missionary_data.get('turn_undead_used', 0)
        missionary.sanctuary_active = missionary_data.get('sanctuary_active', False)
        missionary.sanctuary_duration = missionary_data.get('sanctuary_duration', 0)
        
        # Recalculate missionary-specific attributes
        missionary.healing_pool = missionary._calculate_healing_pool()
        missionary.healing_bonus = missionary._calculate_healing_bonus()
        missionary.cure_disease_uses = max(1, missionary.level // 2)
        missionary.remove_curse_uses = max(1, missionary.level // 4)
        missionary.sanctuary_uses = max(1, missionary.level // 3)
        missionary.bless_uses = max(2, missionary.level // 2)
        missionary.bless_bonus = missionary._calculate_bless_bonus()
        missionary.turn_undead_uses = max(1, missionary.level // 3)
        missionary.divine_protection_bonus = missionary._calculate_divine_protection()
        
        return missionary
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include missionary-specific data"""
        data = super().to_dict()
        data['missionary_data'] = {
            'healing_used': self.healing_used,
            'cure_disease_used': self.cure_disease_used,
            'remove_curse_used': self.remove_curse_used,
            'sanctuary_used': self.sanctuary_used,
            'bless_used': self.bless_used,
            'turn_undead_used': self.turn_undead_used,
            'sanctuary_active': self.sanctuary_active,
            'sanctuary_duration': self.sanctuary_duration
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Missionary"""
        # Check if lost faith
        if self.get_alignment() == Alignment.EVIL:
            return super().__str__() + " [LOST FAITH]"
        
        abilities = []
        
        # Healing pool
        healing_remaining = self.get_healing_remaining()
        abilities.append(f"Heal {healing_remaining}")
        
        # Cure disease
        cure_remaining = self.get_cure_disease_remaining()
        abilities.append(f"Cure {cure_remaining}")
        
        # Sanctuary
        sanctuary_remaining = self.get_sanctuary_remaining()
        if self.sanctuary_active:
            abilities.append(f"Sanctuary ({self.sanctuary_duration})")
        elif sanctuary_remaining > 0:
            abilities.append(f"Sanctuary {sanctuary_remaining}")
        
        # Bless
        bless_remaining = self.get_bless_remaining()
        abilities.append(f"Bless {bless_remaining}")
        
        # Turn undead
        turn_remaining = self.get_turn_undead_remaining()
        abilities.append(f"Turn {turn_remaining}")
        
        # Healing bonus
        healing_bonus = self.get_healing_bonus()
        abilities.append(f"Heal +{healing_bonus}")
        
        # Spell resistance
        if self.has_spell_resistance():
            sr = self.get_spell_resistance()
            abilities.append(f"SR {sr}")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str