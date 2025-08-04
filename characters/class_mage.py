"""
Mage Character Class for Rogue City
Traditional MajorMUD spellcaster with extensive spell arsenal and mana system.
Glass cannon design requiring strategic resource management.
"""

from .base_character import BaseCharacter
from core.alignment_system import Alignment
from typing import Dict, Any, List, Tuple


class Mage(BaseCharacter):
    """
    Mage class - Traditional spellcaster with extensive magical arsenal
    
    GLASS CANNON CLASS - High damage, complex resource management
    
    Difficulty: 9 (High) - Complex spellcasting and resource management
    Stat Modifiers: +3 INT, +2 WIS, -2 STR, -3 CON
    Hit Die: d4 (Lowest HP per level)
    Attack Speed: 6.0 seconds (staff/spell casting)
    Critical Range: 20 (standard critical chance)
    
    SPELL SYSTEM:
    - Mana Pool: Based on INT and WIS modifiers
    - Spell Schools: Combat, Protection, Utility magic
    - Spell Learning: Gain new spells at odd levels
    - Spell Power: Bonus damage/healing from INT
    - Mana Regeneration: Enhanced natural recovery
    
    MAGICAL ABILITIES:
    - Spell Mastery: Access to all mage spells
    - Spell Critical: 20% chance for double effect
    - Elemental Resistance: Fire/Cold/Lightning +1
    - Magical Research: Learn spells faster
    - Arcane Knowledge: Detect magic, identify items
    
    EQUIPMENT RESTRICTIONS:
    - Weapons: Staves and daggers only
    - Armor: Robes only (cloth armor)
    - Focus: Must have spellcasting focus
    - Physical Combat: Penalties due to frailty
    """
    
    def __init__(self, name: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize Mage character with spell and mana systems"""
        super().__init__(name, 'mage', race_id, alignment)
        
        # Mage-specific spell attributes  
        self.spell_slots_used = {}  # Track spell usage per day
        self.spell_critical_chance = 20  # 20% chance for spell crits
        
        # Elemental resistances
        self.elemental_resistances = {
            'fire': 1,
            'cold': 1,
            'lightning': 1
        }
        
        # Spellcasting focus tracking
        self.has_spellcasting_focus = False
        self.spell_failure_chance = 0
        
    def get_hit_die_value(self) -> int:
        """Mages use d4 hit die (lowest HP per level)"""
        return 4
        
    def get_hit_die_type(self) -> str:
        """Return dice notation for hit die"""
        return "1d4"
        
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds (considering equipped weapon)"""
        if self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    def get_base_attack_speed(self) -> float:
        """Mages attack every 6 seconds unarmed"""
        return 6.0
        
    def get_critical_range(self) -> int:
        """Mages crit only on natural 20 (standard)"""
        return 20
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Comprehensive Mage magical abilities"""
        return {
            # Core spellcasting
            'mana_system': True,
            'known_spells': self.get_known_spells(),
            'spell_power_bonus': self.get_spell_power_bonus(),
            'spell_critical_chance': self.spell_critical_chance,
            'mana_efficiency': 25,  # +25% mana regeneration
            
            # Spell schools
            'combat_magic': True,
            'protection_magic': True,
            'utility_magic': True,
            'elemental_mastery': True,
            
            # Magical knowledge
            'arcane_knowledge': True,
            'magical_research': True,
            'detect_magic': True,
            'identify_items': True,
            'spell_learning': True,
            
            # Resistances and defenses
            'elemental_resistance': self.elemental_resistances,
            'magic_insight': True,
            'spell_turning': self.level >= 15,
            
            # Equipment restrictions
            'staves_and_daggers_only': True,
            'robes_only': True,
            'requires_focus': True,
            'no_heavy_armor': True
        }
        
    def calculate_derived_stats(self):
        """Override to include mage-specific calculations"""
        super().calculate_derived_stats()
            
        # Mages use INT modifier for spell attack bonus
        int_modifier = (self.stats['intelligence'] - 10) // 2
        self.base_attack_bonus = self.level + int_modifier
        
        # Update elemental resistances based on level (if attribute exists)
        if hasattr(self, 'elemental_resistances'):
            base_resistance = 1 + (self.level // 10)  # +1 per 10 levels
            for element in self.elemental_resistances:
                self.elemental_resistances[element] = base_resistance
        
    # === MAGE SPELL SYSTEM ===
    
    def can_learn_new_spell(self) -> bool:
        """Check if mage can learn a new spell this level"""
        # Learn spells at odd levels (3, 5, 7, 9, etc.)
        return self.level % 2 == 1 and self.level >= 3
    
    def get_available_spells_for_level(self) -> List[str]:
        """Get spells available to learn at current level"""
        spell_list = {
            1: ['magic_missile', 'light'],
            3: ['shield', 'detect_magic'],
            5: ['fireball', 'mage_armor'],
            7: ['lightning_bolt', 'dispel_magic'],
            9: ['ice_shard', 'teleport'],
            11: ['greater_fireball', 'protection_from_elements'],
            13: ['chain_lightning', 'identify'],
            15: ['meteor', 'spell_turning'],
            17: ['time_stop', 'disintegrate'],
            19: ['wish', 'power_word_kill']
        }
        
        available = []
        for level, spells in spell_list.items():
            if level <= self.level:
                available.extend(spells)
        
        # Return spells not yet known
        return [spell for spell in available if spell not in self.known_spells]
    
    # === MAGE MANA SYSTEM ===
        
    def regenerate_mana(self) -> int:
        """Enhanced mana regeneration for mages"""
        base_regen = 5
        wis_bonus = (self.stats['wisdom'] - 10) // 2
        efficiency_bonus = int(base_regen * 0.25)  # 25% efficiency bonus
        total_regen = base_regen + wis_bonus + efficiency_bonus
        return self.restore_mana(max(1, total_regen))
        
    def get_spell_power_bonus(self) -> int:
        """Get spell damage/healing bonus"""
        base_bonus = 2  # Base spell power
        int_modifier = (self.stats['intelligence'] - 10) // 2
        level_bonus = self.level // 5  # +1 per 5 levels
        return base_bonus + int_modifier + level_bonus
    
    # === SPELL CASTING ===
        
    def can_cast_spell(self, spell_name: str, mana_cost: int) -> Tuple[bool, str]:
        """Check if mage can cast a specific spell"""
        if spell_name not in self.known_spells:
            return False, f"Spell '{spell_name}' not known"
        
        if self.current_mana < mana_cost:
            return False, f"Insufficient mana (need {mana_cost}, have {self.current_mana})"
        
        if not self.has_spellcasting_focus:
            return False, "Requires spellcasting focus (staff or wand)"
        
        return True, "Can cast spell"
    
    def get_spell_mana_cost(self, spell_name: str) -> int:
        """Get mana cost for a specific spell"""
        spell_costs = {
            'magic_missile': 2,
            'light': 1,
            'shield': 3,
            'detect_magic': 2,
            'fireball': 4,
            'mage_armor': 3,
            'lightning_bolt': 4,
            'dispel_magic': 5,
            'ice_shard': 4,
            'teleport': 6,
            'greater_fireball': 6,
            'protection_from_elements': 5,
            'chain_lightning': 8,
            'identify': 3,
            'meteor': 10,
            'spell_turning': 8,
            'time_stop': 15,
            'disintegrate': 12,
            'wish': 20,
            'power_word_kill': 18
        }
        return spell_costs.get(spell_name, 5)  # Default 5 mana
    
    def attempt_spell_critical(self) -> bool:
        """Check if spell achieves critical effect"""
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            roll = dice.roll("1d100")
            return roll <= self.spell_critical_chance
        except ImportError:
            import random
            return random.randint(1, 100) <= self.spell_critical_chance
    
    def get_spell_damage(self, spell_name: str) -> str:
        """Get damage dice for combat spells"""
        spell_damage = {
            'magic_missile': '1d4',
            'fireball': '1d6',
            'lightning_bolt': '1d8',
            'ice_shard': '1d6',
            'greater_fireball': '2d6',
            'chain_lightning': '1d10',
            'meteor': '3d6',
            'disintegrate': '4d6',
            'power_word_kill': '10d10'
        }
        
        base_damage = spell_damage.get(spell_name, '1d4')
        spell_power = self.get_spell_power_bonus()
        
        if spell_power > 0:
            return f"{base_damage}+{spell_power}"
        return base_damage
    
    # === MAGICAL ABILITIES ===
    
    def get_elemental_resistance(self, element: str) -> int:
        """Get resistance to specific element"""
        return self.elemental_resistances.get(element.lower(), 0)
    
    def can_detect_magic(self) -> bool:
        """Mages can always detect magic"""
        return True
    
    def can_identify_items(self) -> bool:
        """Check if mage can identify magical items"""
        return self.level >= 5
    
    def get_magical_research_bonus(self) -> int:
        """Get bonus for learning new spells"""
        base_bonus = 3
        int_bonus = (self.stats['intelligence'] - 10) // 2
        return base_bonus + int_bonus
        
    def can_use_weapon(self, weapon) -> bool:
        """Check if mage can use a specific weapon (staves and daggers only)"""
        if hasattr(weapon, 'weapon_type'):
            return weapon.weapon_type.lower() in ['staff', 'dagger', 'wand']
        if hasattr(weapon, 'name'):
            weapon_name = weapon.name.lower()
            return any(word in weapon_name for word in ['staff', 'dagger', 'wand'])
        return False
    
    def can_use_armor(self, armor) -> bool:
        """Check if mage can use specific armor (robes only)"""
        if hasattr(armor, 'armor_type'):
            return armor.armor_type.lower() in ['robe', 'cloth']
        if hasattr(armor, 'name'):
            return 'robe' in armor.name.lower()
        return False
    
    def get_experience_penalty(self) -> int:
        """Mages have +40% experience penalty (arcane spellcaster)"""
        return 40
    
    def to_dict(self) -> Dict[str, Any]:
        """Override to include mage-specific data in save"""
        data = super().to_dict()
        data.update({
            'mana': {
                'max_mana': self.max_mana,
                'current_mana': self.current_mana
            },
            'spells': {
                'known_spells': self.known_spells,
                'spell_slots_used': self.spell_slots_used
            },
            'magical_attributes': {
                'elemental_resistances': self.elemental_resistances,
                'spell_critical_chance': self.spell_critical_chance,
                'has_spellcasting_focus': self.has_spellcasting_focus
            }
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mage':
        """Create Mage from save data"""
        race_id = data.get('race_id', 'human')
        
        # Load alignment from save data or default to neutral
        alignment = Alignment.NEUTRAL
        if 'alignment_data' in data:
            alignment_name = data['alignment_data'].get('alignment', 'NEUTRAL')
            alignment = getattr(Alignment, alignment_name, Alignment.NEUTRAL)
        
        mage = cls(data['character_name'], race_id, alignment)
        
        # Restore basic character data
        mage.level = data['level']
        mage.experience = data['experience']
        mage.base_stats = data.get('base_stats', mage.base_stats)
        mage.stats = data['stats']
        
        # Restore derived stats
        derived = data['derived_stats']
        mage.max_hp = derived['max_hp']
        mage.current_hp = derived['current_hp']
        mage.armor_class = derived['armor_class']
        mage.base_attack_bonus = derived['base_attack_bonus']
        
        # Restore location
        location = data['current_location']
        mage.current_area = location.get('area_id')
        mage.current_room = location.get('room_id')
        
        # Initialize item systems
        mage.initialize_item_systems()
        
        # Restore inventory and equipment data
        if 'inventory' in data:
            mage.inventory_system.from_dict(data['inventory'])
        if 'equipment' in data:
            mage.equipment_system.from_dict(data['equipment'])
        
        # Restore character creation state
        mage.unallocated_stats = data.get('unallocated_stats', 0)
        mage.creation_complete = data.get('creation_complete', True)
        
        # Restore magic data (mana and spells) - handled by base class now
        if 'magic_data' in data:
            mage.max_mana = data['magic_data'].get('max_mana', 0)
            mage.current_mana = data['magic_data'].get('current_mana', 0)
            mage.known_spells = data['magic_data'].get('known_spells', [])
        elif 'mana' in data and 'spells' in data:
            # Legacy save format
            mage.max_mana = data['mana']['max_mana']
            mage.current_mana = data['mana']['current_mana']
            mage.known_spells = data['spells'].get('known_spells', ['magic_missile', 'light'])
            mage.spell_slots_used = data['spells'].get('spell_slots_used', {})
        else:
            # Recalculate if not in save data
            mage.calculate_derived_stats()
        
        # Restore magical attributes
        if 'magical_attributes' in data:
            mage.elemental_resistances = data['magical_attributes'].get('elemental_resistances', 
                                                                      {'fire': 1, 'cold': 1, 'lightning': 1})
            mage.spell_critical_chance = data['magical_attributes'].get('spell_critical_chance', 20)
            mage.has_spellcasting_focus = data['magical_attributes'].get('has_spellcasting_focus', False)
        
        # Load alignment data
        if 'alignment_data' in data:
            mage.load_alignment_data(data['alignment_data'])
            
        return mage
        
    def __str__(self) -> str:
        """String representation of enhanced Mage"""
        abilities = []
        
        # Mana status
        mana_status = f"MP: {self.current_mana}/{self.max_mana}"
        abilities.append(mana_status)
        
        # Spell power
        spell_power = self.get_spell_power_bonus()
        abilities.append(f"Spell Power +{spell_power}")
        
        # Known spells count
        spell_count = len(self.known_spells)
        abilities.append(f"{spell_count} Spells")
        
        # Elemental resistances (if any are > 1)
        high_resistances = [f"{elem.title()} {res}" for elem, res in self.elemental_resistances.items() if res > 1]
        if high_resistances:
            abilities.append(f"Resist: {', '.join(high_resistances)}")
        
        # Spell critical chance (if different from default)
        if self.spell_critical_chance != 20:
            abilities.append(f"Spell Crit {self.spell_critical_chance}%")
        
        # Focus status
        if self.has_spellcasting_focus:
            abilities.append("Focus")
        else:
            abilities.append("No Focus")
            
        base_str = super().__str__()
        if abilities:
            base_str += f" [{', '.join(abilities)}]"
        return base_str