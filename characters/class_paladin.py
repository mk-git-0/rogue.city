"""
Paladin Character Class for Rogue City
Traditional MajorMUD holy warrior with divine magic and healing abilities.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, Tuple, List


class Paladin(BaseCharacter):
    """
    Paladin class - Holy warrior with divine magic
    
    DIVINE WARRIOR - Moderate progression, alignment-restricted
    
    Experience Penalty: +20% (divine powers justify slower progression)
    Alignment Restriction: Good only (lose abilities if alignment changes)
    Stat Modifiers: +2 STR, +2 WIS, +1 CHA, -2 INT, -1 DEX
    Hit Die: d10 (excellent HP progression)
    Attack Speed: 3.0 seconds (standard combat speed)
    Critical Range: 20 (standard critical chance)
    
    DIVINE MAGIC CORE:
    - Lay on hands healing magic (limited daily uses)
    - Turn undead ability to repel or destroy undead
    - Detect evil to sense evil auras and intentions
    - Divine favor for temporary bonuses from deity
    - Smite evil for extra damage against evil opponents
    - Protection from evil as constant ward
    
    PALADIN ABILITIES:
    - Lay on Hands: Heal self and others (limited daily uses)
    - Turn Undead: Repel or destroy undead creatures
    - Detect Evil: Sense evil auras and intentions
    - Divine Favor: Temporary bonuses from deity
    - Smite Evil: Extra damage against evil opponents
    - Protection from Evil: Constant ward against evil magic
    
    EQUIPMENT ACCESS:
    - Weapons: All weapons with holy weapon bonuses
    - Armor: All armor types with divine protection
    - Magic: Can use holy and blessed magical items
    - Accessories: Holy symbols, blessed accessories
    
    ALIGNMENT REQUIREMENT:
    - Must be Good alignment to retain abilities
    - Loses all divine abilities if alignment shifts away from Good
    - Cannot use evil-aligned items or magic
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.GOOD):
        """Initialize Paladin character with divine magic systems"""
        # Force Good alignment for Paladins
        if alignment != Alignment.GOOD:
            alignment = Alignment.GOOD
            
        super().__init__(name, 'paladin', race_id, alignment)
        
        # Divine magic attributes
        self.lay_on_hands_pool = self._calculate_lay_on_hands_pool()
        self.lay_on_hands_used = 0
        self.turn_undead_uses = self._calculate_turn_undead_uses()
        self.turn_undead_used = 0
        
        # Smite abilities
        self.smite_evil_uses = max(1, (self.level + 2) // 3)  # 1 at level 1, +1 every 3 levels
        self.smite_evil_used = 0
        self.smite_damage_bonus = self._calculate_smite_damage()
        
        # Divine favor and blessings
        self.divine_favor_uses = max(1, self.level // 4)
        self.divine_favor_used = 0
        self.protection_from_evil_active = True  # Always active for paladins
        
        # Detect evil ability
        self.detect_evil_range = 60  # 60 feet range
        self.detect_evil_active = False
        
        # Divine resistance bonuses
        self.disease_immunity = self.level >= 3
        self.fear_immunity = self.level >= 2
        self.charm_resistance = 2  # +2 resistance
        
    def get_hit_die_value(self) -> int:
        """Paladins use d10 hit die (excellent HP progression)"""
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
        """Paladins attack every 3 seconds unarmed (standard speed)"""
        return 3.0
        
    def get_critical_range(self) -> int:
        """Paladins crit on natural 20 (standard critical)"""
        return 20
        
    def get_experience_penalty(self) -> int:
        """Paladins have +20% experience penalty"""
        return 20
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Paladin special abilities"""
        # Check if still Good aligned
        if self.get_alignment() != Alignment.GOOD:
            return {
                'fallen_paladin': True,
                'abilities_lost': 'All divine abilities lost due to alignment change',
                'equipment_proficiency': True  # Still retains weapon/armor training
            }
        
        return {
            # Divine healing
            'lay_on_hands': self.get_lay_on_hands_remaining(),
            'lay_on_hands_pool': self.get_lay_on_hands_pool(),
            'cure_disease': self.level >= 6,
            'remove_curse': self.level >= 9,
            
            # Turn undead
            'turn_undead': self.get_turn_undead_remaining(),
            'turn_undead_level': self.get_turn_undead_level(),
            'destroy_undead': self.level >= 8,
            
            # Smite abilities
            'smite_evil': self.get_smite_evil_remaining(),
            'smite_damage': self.get_smite_damage_bonus(),
            'smite_accuracy': True,
            
            # Divine favor and protection
            'divine_favor': self.get_divine_favor_remaining(),
            'protection_from_evil': True,
            'magic_circle_vs_evil': self.level >= 8,
            'holy_aura': self.level >= 15,
            
            # Detection abilities
            'detect_evil': True,
            'detect_undead': self.level >= 4,
            'detect_lies': self.level >= 7,
            
            # Divine resistances
            'disease_immunity': self.disease_immunity,
            'fear_immunity': self.fear_immunity,
            'charm_resistance': self.charm_resistance,
            'poison_resistance': 2,
            
            # Combat abilities
            'divine_grace': True,  # CHA bonus to saves
            'divine_health': self.level >= 3,
            'aura_of_courage': self.level >= 3,
            'divine_weapon': self.level >= 5,
            
            # Equipment mastery
            'all_weapon_proficiency': True,
            'all_armor_proficiency': True,
            'holy_weapon_mastery': True,
            'blessed_equipment': True
        }
    
    # === DIVINE HEALING ABILITIES ===
    
    def _calculate_lay_on_hands_pool(self) -> int:
        """Calculate total lay on hands healing pool"""
        base_pool = self.level * 2  # 2 HP per level
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        return base_pool + (cha_bonus * self.level)
    
    def get_lay_on_hands_pool(self) -> int:
        """Get total lay on hands healing pool"""
        return self._calculate_lay_on_hands_pool()
    
    def get_lay_on_hands_remaining(self) -> int:
        """Get lay on hands healing remaining"""
        return max(0, self.get_lay_on_hands_pool() - self.lay_on_hands_used)
    
    def can_lay_on_hands(self, amount: int = 1) -> bool:
        """Check if paladin can use lay on hands"""
        if self.get_alignment() != Alignment.GOOD:
            return False
        return self.get_lay_on_hands_remaining() >= amount
    
    def use_lay_on_hands(self, amount: int, target=None) -> Dict[str, Any]:
        """Use lay on hands healing"""
        if not self.can_lay_on_hands(amount):
            return {'success': False, 'reason': 'Insufficient healing pool'}
        
        if target is None:
            target = self
        
        self.lay_on_hands_used += amount
        healing_done = target.heal(amount)
        
        return {
            'success': True,
            'healing_done': healing_done,
            'target': target.name,
            'remaining_pool': self.get_lay_on_hands_remaining()
        }
    
    def can_cure_disease(self) -> bool:
        """Check if paladin can cure disease"""
        return self.level >= 6 and self.get_alignment() == Alignment.GOOD
    
    def cure_disease(self, target=None) -> bool:
        """Cure disease on target"""
        if not self.can_cure_disease():
            return False
        
        # Uses lay on hands pool
        cost = 5  # 5 points from pool
        if not self.can_lay_on_hands(cost):
            return False
        
        self.lay_on_hands_used += cost
        return True
    
    # === TURN UNDEAD ABILITIES ===
    
    def _calculate_turn_undead_uses(self) -> int:
        """Calculate turn undead uses per day"""
        base_uses = 3 + max(0, (self.stats['charisma'] - 10) // 2)
        return base_uses
    
    def get_turn_undead_uses(self) -> int:
        """Get total turn undead uses per day"""
        return self._calculate_turn_undead_uses()
    
    def get_turn_undead_remaining(self) -> int:
        """Get turn undead uses remaining"""
        return max(0, self.get_turn_undead_uses() - self.turn_undead_used)
    
    def get_turn_undead_level(self) -> int:
        """Get effective cleric level for turning undead"""
        return self.level  # Paladins turn as clerics of same level
    
    def can_turn_undead(self) -> bool:
        """Check if paladin can turn undead"""
        if self.get_alignment() != Alignment.GOOD:
            return False
        return self.get_turn_undead_remaining() > 0
    
    def attempt_turn_undead(self, undead_hd: int) -> Dict[str, Any]:
        """Attempt to turn undead"""
        if not self.can_turn_undead():
            return {'success': False, 'reason': 'No turn attempts remaining'}
        
        self.turn_undead_used += 1
        
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            turn_roll = dice.roll("1d20")
            turn_level = self.get_turn_undead_level()
            
            # Calculate turn difficulty
            turn_dc = 10 + undead_hd - turn_level
            success = turn_roll >= turn_dc
            
            # Check for destruction at higher levels
            can_destroy = self.level >= 8 and turn_level >= undead_hd + 4
            destroyed = success and can_destroy and turn_roll >= 15
            
            return {
                'success': success,
                'destroyed': destroyed,
                'turn_roll': turn_roll,
                'turn_dc': turn_dc,
                'remaining_uses': self.get_turn_undead_remaining()
            }
        except ImportError:
            import random
            success = random.randint(1, 20) >= (10 + undead_hd - self.get_turn_undead_level())
            return {
                'success': success,
                'destroyed': False,
                'remaining_uses': self.get_turn_undead_remaining()
            }
    
    # === SMITE EVIL ABILITIES ===
    
    def _calculate_smite_damage(self) -> int:
        """Calculate smite evil damage bonus"""
        return self.level  # +1 damage per level
    
    def get_smite_damage_bonus(self) -> int:
        """Get smite evil damage bonus"""
        return self._calculate_smite_damage()
    
    def get_smite_evil_remaining(self) -> int:
        """Get smite evil uses remaining"""
        return max(0, self.smite_evil_uses - self.smite_evil_used)
    
    def can_smite_evil(self) -> bool:
        """Check if paladin can smite evil"""
        if self.get_alignment() != Alignment.GOOD:
            return False
        return self.get_smite_evil_remaining() > 0
    
    def use_smite_evil(self, target_alignment: Alignment = None) -> Dict[str, Any]:
        """Use smite evil ability"""
        if not self.can_smite_evil():
            return {'success': False, 'reason': 'No smite uses remaining'}
        
        # Only works on evil targets
        if target_alignment != Alignment.EVIL:
            return {'success': False, 'reason': 'Target is not evil'}
        
        self.smite_evil_used += 1
        
        # Calculate smite bonuses
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        attack_bonus = cha_bonus
        damage_bonus = self.get_smite_damage_bonus()
        
        return {
            'success': True,
            'attack_bonus': attack_bonus,
            'damage_bonus': damage_bonus,
            'remaining_uses': self.get_smite_evil_remaining()
        }
    
    # === DIVINE FAVOR AND PROTECTION ===
    
    def get_divine_favor_remaining(self) -> int:
        """Get divine favor uses remaining"""
        return max(0, self.divine_favor_uses - self.divine_favor_used)
    
    def can_use_divine_favor(self) -> bool:
        """Check if paladin can use divine favor"""
        if self.get_alignment() != Alignment.GOOD:
            return False
        return self.get_divine_favor_remaining() > 0
    
    def use_divine_favor(self) -> Dict[str, Any]:
        """Use divine favor ability"""
        if not self.can_use_divine_favor():
            return {'success': False, 'reason': 'No divine favor uses remaining'}
        
        self.divine_favor_used += 1
        return {
            'success': True,
            'attack_bonus': 1,
            'damage_bonus': 1,
            'duration_minutes': 10,
            'remaining_uses': self.get_divine_favor_remaining()
        }
    
    def has_protection_from_evil(self) -> bool:
        """Check if paladin has protection from evil active"""
        return self.get_alignment() == Alignment.GOOD
    
    def get_protection_bonus(self) -> int:
        """Get protection from evil AC bonus"""
        if self.has_protection_from_evil():
            return 2  # +2 deflection bonus vs evil
        return 0
    
    # === DETECTION ABILITIES ===
    
    def can_detect_evil(self) -> bool:
        """Check if paladin can detect evil"""
        return self.get_alignment() == Alignment.GOOD
    
    def detect_evil(self, target_alignment: Alignment) -> Dict[str, Any]:
        """Detect evil in target"""
        if not self.can_detect_evil():
            return {'detected': False, 'reason': 'Lost divine abilities'}
        
        is_evil = target_alignment == Alignment.EVIL
        return {
            'detected': is_evil,
            'alignment': target_alignment.name if is_evil else 'Not Evil',
            'strength': 'Strong' if is_evil else 'None'
        }
    
    def detect_undead(self, target_type: str) -> bool:
        """Detect undead creatures"""
        if self.level < 4 or self.get_alignment() != Alignment.GOOD:
            return False
        
        undead_types = ['skeleton', 'zombie', 'ghost', 'wraith', 'lich', 'vampire']
        return target_type.lower() in undead_types
    
    # === DIVINE RESISTANCES ===
    
    def get_save_bonus(self, save_type: str = None) -> int:
        """Get divine grace save bonus"""
        if self.get_alignment() != Alignment.GOOD:
            return 0
        
        cha_bonus = max(0, (self.stats['charisma'] - 10) // 2)
        return cha_bonus  # Divine grace adds CHA bonus to all saves
    
    def is_immune_to_disease(self) -> bool:
        """Check disease immunity"""
        return self.disease_immunity and self.get_alignment() == Alignment.GOOD
    
    def is_immune_to_fear(self) -> bool:
        """Check fear immunity"""
        return self.fear_immunity and self.get_alignment() == Alignment.GOOD
    
    def get_charm_resistance(self) -> int:
        """Get charm resistance bonus"""
        if self.get_alignment() == Alignment.GOOD:
            return self.charm_resistance
        return 0
    
    def provides_aura_of_courage(self) -> bool:
        """Check if paladin provides aura of courage to allies"""
        return self.level >= 3 and self.get_alignment() == Alignment.GOOD
    
    # === EQUIPMENT RESTRICTIONS ===
    
    def can_use_weapon(self, weapon) -> bool:
        """Paladins can use all weapons"""
        return True
    
    def can_use_armor(self, armor) -> bool:
        """Paladins can use all armor types"""
        return True
    
    def can_equip_item(self, item) -> Tuple[bool, str]:
        """Check if paladin can equip an item"""
        # Check for evil items
        if hasattr(item, 'alignment') and item.alignment == 'evil':
            return False, "Paladins cannot use evil-aligned items"
        
        # Paladins get bonuses with holy/blessed items
        if hasattr(item, 'alignment') and item.alignment in ['good', 'holy', 'blessed']:
            return True, "Holy item - receives divine blessing"
        
        return True, "Equipment allowed"
    
    def calculate_derived_stats(self):
        """Override to include divine bonuses"""
        super().calculate_derived_stats()
        
        # Add protection from evil AC bonus
        if self.has_protection_from_evil():
            self.armor_class += self.get_protection_bonus()
    
    def set_alignment(self, new_alignment: Alignment) -> bool:
        """Override to handle fallen paladin mechanics"""
        old_alignment = self.get_alignment()
        success = super().set_alignment(new_alignment)
        
        # Check if paladin has fallen
        if success and old_alignment == Alignment.GOOD and new_alignment != Alignment.GOOD:
            # Paladin has fallen - lose all divine abilities
            self.lay_on_hands_used = self.get_lay_on_hands_pool()  # Can't use healing
            self.turn_undead_used = self.get_turn_undead_uses()  # Can't turn undead
            self.smite_evil_used = self.smite_evil_uses  # Can't smite
            self.divine_favor_used = self.divine_favor_uses  # Can't use favor
            self.protection_from_evil_active = False
        
        return success
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paladin':
        """Create Paladin from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to good
        alignment = Alignment.GOOD
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'GOOD')
            alignment = getattr(Alignment, alignment_name, Alignment.GOOD)
        
        paladin = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        paladin.level = data['level']
        paladin.experience = data['experience']
        paladin.base_stats = data.get('base_stats', paladin.base_stats)
        paladin.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        paladin.max_hp = derived['max_hp']
        paladin.current_hp = derived['current_hp']
        paladin.armor_class = derived['armor_class']
        paladin.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        paladin.current_area = location.get('area_id')
        paladin.current_room = location.get('room_id')
        
        # Initialize item systems
        paladin.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            paladin.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            paladin.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        paladin.unallocated_stats = data.get('unallocated_stats', 0)
        paladin.creation_complete = data.get('creation_complete', True)
        
        # Load alignment data
        if 'alignment_data' in data:
            paladin.load_alignment_data(data['alignment_data'])
        
        # Load currency data
        if 'currency_data' in data:
            paladin.load_currency_data(data['currency_data'])
        
        # Restore paladin-specific attributes
        paladin_data = data.get('paladin_data', {})
        paladin.lay_on_hands_used = paladin_data.get('lay_on_hands_used', 0)
        paladin.turn_undead_used = paladin_data.get('turn_undead_used', 0)
        paladin.smite_evil_used = paladin_data.get('smite_evil_used', 0)
        paladin.divine_favor_used = paladin_data.get('divine_favor_used', 0)
        
        # Recalculate paladin-specific attributes
        paladin.lay_on_hands_pool = paladin._calculate_lay_on_hands_pool()
        paladin.turn_undead_uses = paladin._calculate_turn_undead_uses()
        paladin.smite_evil_uses = max(1, (paladin.level + 2) // 3)
        paladin.divine_favor_uses = max(1, paladin.level // 4)
        paladin.smite_damage_bonus = paladin._calculate_smite_damage()
        paladin.disease_immunity = paladin.level >= 3
        paladin.fear_immunity = paladin.level >= 2
        
        return paladin
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include paladin-specific data"""
        data = super().to_dict()
        data['paladin_data'] = {
            'lay_on_hands_used': self.lay_on_hands_used,
            'turn_undead_used': self.turn_undead_used,
            'smite_evil_used': self.smite_evil_used,
            'divine_favor_used': self.divine_favor_used
        }
        return data
        
    def __str__(self) -> str:
        """String representation of Paladin"""
        # Check if fallen
        if self.get_alignment() != Alignment.GOOD:
            return super().__str__() + " [FALLEN PALADIN]"
        
        abilities = []
        
        # Lay on hands
        healing_remaining = self.get_lay_on_hands_remaining()
        abilities.append(f"Heal {healing_remaining}")
        
        # Turn undead
        turn_remaining = self.get_turn_undead_remaining()
        abilities.append(f"Turn {turn_remaining}")
        
        # Smite evil
        smite_remaining = self.get_smite_evil_remaining()
        abilities.append(f"Smite {smite_remaining}")
        
        # Divine favor
        favor_remaining = self.get_divine_favor_remaining()
        if favor_remaining > 0:
            abilities.append(f"Favor {favor_remaining}")
        
        # Immunities
        immunities = []
        if self.is_immune_to_disease():
            immunities.append("Disease")
        if self.is_immune_to_fear():
            immunities.append("Fear")
        if immunities:
            abilities.append(f"Immune: {', '.join(immunities)}")
        
        # Aura of courage
        if self.provides_aura_of_courage():
            abilities.append("Courage Aura")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str