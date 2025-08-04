"""
Magic Command System for Rogue City
Framework for spellcasting, mana management, and class-specific magical abilities.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class SpellSchool(Enum):
    """Schools of magic."""
    EVOCATION = "evocation"        # Damage spells (Magic Missile, Fireball)
    CONJURATION = "conjuration"    # Summoning and creation
    ENCHANTMENT = "enchantment"    # Mind-affecting spells
    DIVINATION = "divination"      # Information-gathering spells
    TRANSMUTATION = "transmutation" # Changing properties
    ILLUSION = "illusion"          # Deception and misdirection
    NECROMANCY = "necromancy"      # Death magic
    ABJURATION = "abjuration"      # Protection spells


class SpellLevel(Enum):
    """Spell levels (power/complexity)."""
    CANTRIP = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    EIGHTH = 8
    NINTH = 9


class TargetType(Enum):
    """Spell targeting types."""
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    SINGLE_ALLY = "single_ally"
    SINGLE_ANY = "single_any"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"
    AREA = "area"
    NONE = "none"


class MagicCommandSystem:
    """
    Manages spellcasting, mana, and magical abilities for all spellcasting classes.
    """
    
    def __init__(self, dice_system, ui_manager):
        """Initialize the magic command system."""
        self.dice_system = dice_system
        self.ui_manager = ui_manager
        
        # Class spellcasting abilities
        self.spellcasting_classes = {
            'mage': {
                'primary_stat': 'intelligence',
                'mana_multiplier': 2.0,
                'spell_schools': [SpellSchool.EVOCATION, SpellSchool.TRANSMUTATION, SpellSchool.CONJURATION],
                'max_spell_level': 9,
                'spells_per_level': [4, 3, 3, 2, 2, 1, 1, 1, 1, 1]  # Spells known by level
            },
            'druid': {
                'primary_stat': 'wisdom',
                'mana_multiplier': 1.5,
                'spell_schools': [SpellSchool.CONJURATION, SpellSchool.TRANSMUTATION, SpellSchool.DIVINATION],
                'max_spell_level': 7,
                'spells_per_level': [3, 2, 2, 2, 1, 1, 1, 1]
            },
            'necromancer': {
                'primary_stat': 'intelligence',
                'mana_multiplier': 1.8,
                'spell_schools': [SpellSchool.NECROMANCY, SpellSchool.EVOCATION, SpellSchool.ENCHANTMENT],
                'max_spell_level': 8,
                'spells_per_level': [3, 3, 2, 2, 2, 1, 1, 1, 1]
            },
            'warlock': {
                'primary_stat': 'intelligence',
                'mana_multiplier': 1.3,
                'spell_schools': [SpellSchool.EVOCATION, SpellSchool.ENCHANTMENT, SpellSchool.CONJURATION],
                'max_spell_level': 6,
                'spells_per_level': [3, 2, 2, 1, 1, 1, 1]
            },
            'paladin': {
                'primary_stat': 'wisdom',
                'mana_multiplier': 0.8,
                'spell_schools': [SpellSchool.ABJURATION, SpellSchool.EVOCATION],
                'max_spell_level': 4,
                'spells_per_level': [2, 1, 1, 1, 1]
            },
            'ranger': {
                'primary_stat': 'wisdom',
                'mana_multiplier': 0.6,
                'spell_schools': [SpellSchool.DIVINATION, SpellSchool.CONJURATION],
                'max_spell_level': 3,
                'spells_per_level': [1, 1, 1, 1]
            },
            'bard': {
                'primary_stat': 'charisma',
                'mana_multiplier': 1.0,
                'spell_schools': [SpellSchool.ENCHANTMENT, SpellSchool.ILLUSION],
                'max_spell_level': 6,
                'spells_per_level': [2, 2, 1, 1, 1, 1, 1]
            }
        }
        
        # Basic spell library
        self.spell_library = {
            # CANTRIPS (Level 0)
            'light': {
                'level': SpellLevel.CANTRIP,
                'school': SpellSchool.EVOCATION,
                'mana_cost': 1,
                'cast_time': 1,
                'target_type': TargetType.NONE,
                'description': 'Creates a bright light',
                'effect': self._spell_light
            },
            'detect magic': {
                'level': SpellLevel.CANTRIP,
                'school': SpellSchool.DIVINATION,
                'mana_cost': 1,
                'cast_time': 1,
                'target_type': TargetType.NONE,
                'description': 'Reveals magical auras',
                'effect': self._spell_detect_magic
            },
            
            # FIRST LEVEL
            'magic missile': {
                'level': SpellLevel.FIRST,
                'school': SpellSchool.EVOCATION,
                'mana_cost': 2,
                'cast_time': 1,
                'target_type': TargetType.SINGLE_ENEMY,
                'description': 'Launches unerring magical darts',
                'effect': self._spell_magic_missile
            },
            'heal': {
                'level': SpellLevel.FIRST,
                'school': SpellSchool.CONJURATION,
                'mana_cost': 3,
                'cast_time': 1,
                'target_type': TargetType.SINGLE_ALLY,
                'description': 'Restores hit points',
                'effect': self._spell_heal
            },
            'shield': {
                'level': SpellLevel.FIRST,
                'school': SpellSchool.ABJURATION,
                'mana_cost': 2,
                'cast_time': 1,
                'target_type': TargetType.SELF,
                'description': 'Provides magical protection',
                'effect': self._spell_shield
            },
            
            # SECOND LEVEL
            'fireball': {
                'level': SpellLevel.SECOND,
                'school': SpellSchool.EVOCATION,
                'mana_cost': 5,
                'cast_time': 2,
                'target_type': TargetType.SINGLE_ENEMY,
                'description': 'Launches a fiery explosion',
                'effect': self._spell_fireball
            },
            'invisibility': {
                'level': SpellLevel.SECOND,
                'school': SpellSchool.ILLUSION,
                'mana_cost': 4,
                'cast_time': 2,
                'target_type': TargetType.SINGLE_ALLY,
                'description': 'Makes target invisible',
                'effect': self._spell_invisibility
            }
        }
        
        # Character mana tracking
        self.character_mana: Dict[str, Dict[str, Any]] = {}
        
        # Spell effects tracking
        self.active_spell_effects: Dict[str, List[Dict]] = {}
    
    def can_cast_spells(self, character) -> bool:
        """Check if character can cast spells."""
        if not hasattr(character, 'character_class'):
            return False
        return character.character_class.lower() in self.spellcasting_classes
    
    def can_meditate(self, character) -> bool:
        """Check if character can meditate to recover mana/ki."""
        if not hasattr(character, 'character_class'):
            return False
        char_class = character.character_class.lower()
        return char_class in ['mystic', 'ninja'] or self.can_cast_spells(character)
    
    def get_character_mana(self, character) -> Tuple[int, int]:
        """Get character's current and maximum mana."""
        char_id = self._get_character_id(character)
        
        if char_id not in self.character_mana:
            self._initialize_character_mana(character)
        
        mana_data = self.character_mana[char_id]
        return mana_data['current'], mana_data['maximum']
    
    def _initialize_character_mana(self, character) -> None:
        """Initialize character's mana pool."""
        char_id = self._get_character_id(character)
        
        if not self.can_cast_spells(character) and not self.can_meditate(character):
            self.character_mana[char_id] = {'current': 0, 'maximum': 0}
            return
        
        char_class = character.character_class.lower()
        
        # Calculate maximum mana
        if char_class in ['mystic', 'ninja']:
            # Ki-based classes
            base_mana = 10
            level_multiplier = 2
            stat_name = 'wisdom'
        else:
            # Spellcasting classes
            class_info = self.spellcasting_classes[char_class]
            base_mana = 5
            level_multiplier = class_info['mana_multiplier']
            stat_name = class_info['primary_stat']
        
        # Calculate mana from level and primary stat
        level = getattr(character, 'level', 1)
        stat_bonus = character.get_stat_modifier(stat_name) if hasattr(character, 'get_stat_modifier') else 0
        
        max_mana = int(base_mana + (level * level_multiplier) + (stat_bonus * 3))
        
        self.character_mana[char_id] = {
            'current': max_mana,
            'maximum': max_mana
        }
    
    def attempt_cast_spell(self, character, spell_name: str, target_name: str = None) -> bool:
        """
        Attempt to cast a spell.
        
        Returns:
            True if spell was cast successfully
        """
        if not self.can_cast_spells(character):
            self.ui_manager.log_error("You don't know how to cast spells.")
            return False
        
        # Find spell
        spell_name_lower = spell_name.lower()
        if spell_name_lower not in self.spell_library:
            self.ui_manager.log_error(f"You don't know the spell '{spell_name}'.")
            return False
        
        spell = self.spell_library[spell_name_lower]
        
        # Check if character can cast this spell level/school
        if not self._can_cast_spell(character, spell):
            self.ui_manager.log_error(f"You cannot cast {spell_name} - insufficient knowledge or level.")
            return False
        
        # Check mana cost
        current_mana, max_mana = self.get_character_mana(character)
        if current_mana < spell['mana_cost']:
            self.ui_manager.log_error(f"You don't have enough mana to cast {spell_name}. (Need {spell['mana_cost']}, have {current_mana})")
            return False
        
        # Validate target
        target = self._resolve_spell_target(character, spell, target_name)
        if spell['target_type'] != TargetType.NONE and target is None:
            return False
        
        # Begin casting
        self.ui_manager.log_info(f"You begin casting {spell_name}...")
        
        # Check for spell failure (armor interference, etc.)
        if self._check_spell_failure(character):
            self.ui_manager.log_error("Your spell fails!")
            return False
        
        # Deduct mana cost
        self._consume_mana(character, spell['mana_cost'])
        
        # Cast time simulation (for now, instant)
        if spell['cast_time'] > 1:
            self.ui_manager.log_system(f"[Casting time: {spell['cast_time']} rounds]")
        
        # Execute spell effect
        try:
            success = spell['effect'](character, target, spell)
            if success:
                self.ui_manager.log_success(f"You successfully cast {spell_name}!")
            return success
        except Exception as e:
            self.ui_manager.log_error(f"Spell casting failed: {e}")
            return False
    
    def attempt_meditation(self, character) -> bool:
        """
        Attempt to meditate and recover mana/ki.
        
        Returns:
            True if meditation was successful
        """
        if not self.can_meditate(character):
            self.ui_manager.log_error("You don't know how to meditate.")
            return False
        
        current_mana, max_mana = self.get_character_mana(character)
        
        if current_mana >= max_mana:
            self.ui_manager.log_info("You are already at full mana/ki.")
            return True
        
        self.ui_manager.log_info("You sit quietly and begin to meditate...")
        
        # Calculate mana recovery
        char_class = character.character_class.lower()
        if char_class in ['mystic', 'ninja']:
            # Ki recovery
            base_recovery = 3
            wisdom_bonus = character.get_stat_modifier('wisdom') if hasattr(character, 'get_stat_modifier') else 0
        else:
            # Mana recovery for spellcasters
            class_info = self.spellcasting_classes[char_class]
            stat_name = class_info['primary_stat']
            base_recovery = 2
            wisdom_bonus = character.get_stat_modifier(stat_name) if hasattr(character, 'get_stat_modifier') else 0
        
        recovery_amount = base_recovery + max(0, wisdom_bonus)
        
        # Roll for meditation success
        meditation_roll = random.randint(1, 20) + wisdom_bonus
        if meditation_roll >= 10:  # DC 10 meditation check
            recovered = min(recovery_amount, max_mana - current_mana)
            self._restore_mana(character, recovered)
            
            energy_type = "ki" if char_class in ['mystic', 'ninja'] else "mana"
            self.ui_manager.log_success(f"You recover {recovered} {energy_type} through meditation.")
            return True
        else:
            self.ui_manager.log_error("You cannot focus your mind properly.")
            return False
    
    def _can_cast_spell(self, character, spell) -> bool:
        """Check if character can cast a specific spell."""
        char_class = character.character_class.lower()
        if char_class not in self.spellcasting_classes:
            return False
        
        class_info = self.spellcasting_classes[char_class]
        
        # Check spell level
        spell_level = spell['level'].value
        if spell_level > class_info['max_spell_level']:
            return False
        
        # Check if character level is high enough (need to be level spell_level*2 minimum)
        min_level = max(1, spell_level * 2 - 1)
        if getattr(character, 'level', 1) < min_level:
            return False
        
        # Check spell school
        if spell['school'] not in class_info['spell_schools']:
            return False
        
        return True
    
    def _resolve_spell_target(self, caster, spell, target_name: str) -> Optional[Any]:
        """Resolve spell target based on target type and name."""
        target_type = spell['target_type']
        
        if target_type == TargetType.NONE or target_type == TargetType.SELF:
            return caster
        
        if target_name is None:
            if target_type == TargetType.SELF:
                return caster
            else:
                self.ui_manager.log_error(f"You must specify a target for {spell['description'].lower()}.")
                return None
        
        # For now, simplified target resolution
        # In a full implementation, this would search current area for enemies/allies
        if target_type in [TargetType.SINGLE_ENEMY, TargetType.ALL_ENEMIES]:
            # Mock enemy targeting
            return {"name": target_name, "type": "enemy"}
        elif target_type in [TargetType.SINGLE_ALLY, TargetType.ALL_ALLIES]:
            if target_name.lower() in ['self', 'me', caster.name.lower()]:
                return caster
            # Mock ally targeting
            return {"name": target_name, "type": "ally"}
        
        return None
    
    def _check_spell_failure(self, character) -> bool:
        """Check for spell failure due to armor or other factors."""
        failure_chance = 0
        
        # Heavy armor spell failure
        if hasattr(character, 'equipment_system') and character.equipment_system:
            armor = character.equipment_system.get_equipped_armor()
            if armor and hasattr(armor, 'armor_type'):
                armor_type = armor.armor_type.lower()
                if 'heavy' in armor_type or 'plate' in armor_type:
                    failure_chance += 40
                elif 'medium' in armor_type or 'chain' in armor_type:
                    failure_chance += 20
        
        # Roll for failure
        if failure_chance > 0:
            roll = random.randint(1, 100)
            return roll <= failure_chance
        
        return False
    
    def _consume_mana(self, character, amount: int) -> None:
        """Consume mana from character."""
        char_id = self._get_character_id(character)
        if char_id in self.character_mana:
            self.character_mana[char_id]['current'] = max(0, self.character_mana[char_id]['current'] - amount)
    
    def _restore_mana(self, character, amount: int) -> None:
        """Restore mana to character."""
        char_id = self._get_character_id(character)
        if char_id in self.character_mana:
            current = self.character_mana[char_id]['current']
            maximum = self.character_mana[char_id]['maximum']
            self.character_mana[char_id]['current'] = min(maximum, current + amount)
    
    def _get_character_id(self, character) -> str:
        """Get unique identifier for character."""
        if hasattr(character, 'name'):
            return character.name
        return str(id(character))
    
    # Spell Effect Functions
    def _spell_light(self, caster, target, spell) -> bool:
        """Create light spell effect."""
        self.ui_manager.log_success("A bright light illuminates the area around you.")
        return True
    
    def _spell_detect_magic(self, caster, target, spell) -> bool:
        """Detect magic spell effect."""
        self.ui_manager.log_info("You sense magical auras in the area...")
        # In full implementation, would detect magical items/effects
        return True
    
    def _spell_magic_missile(self, caster, target, spell) -> bool:
        """Magic missile spell effect."""
        if not target or target.get('type') != 'enemy':
            self.ui_manager.log_error("You must target an enemy.")
            return False
        
        # Calculate damage (1d4+1 per missile, number based on level)
        caster_level = getattr(caster, 'level', 1)
        num_missiles = min(5, 1 + (caster_level - 1) // 2)  # 1 at level 1, up to 5 at level 9
        
        total_damage = 0
        for i in range(num_missiles):
            damage = self.dice_system.roll("1d4+1")
            total_damage += damage
        
        target_name = target['name']
        self.ui_manager.log_success(f"You launch {num_missiles} glowing dart{'s' if num_missiles > 1 else ''} at {target_name}!")
        self.ui_manager.log_success(f"The magic missile{'s' if num_missiles > 1 else ''} hit{'s' if num_missiles == 1 else ''} {target_name} for {total_damage} damage!")
        
        return True
    
    def _spell_heal(self, caster, target, spell) -> bool:
        """Healing spell effect."""
        if target == caster:
            target_name = "yourself"
        elif hasattr(target, 'name'):
            target_name = target.name
        else:
            target_name = "the target"
        
        # Calculate healing (1d8 + caster level)
        caster_level = getattr(caster, 'level', 1)
        healing = self.dice_system.roll(f"1d8+{caster_level}")
        
        self.ui_manager.log_success(f"Warm healing energy flows into {target_name}.")
        self.ui_manager.log_success(f"{target_name.title()} recover{'s' if target != caster else ''} {healing} hit points.")
        
        # In full implementation, would actually restore HP to target
        return True
    
    def _spell_shield(self, caster, target, spell) -> bool:
        """Shield spell effect."""
        self.ui_manager.log_success("A shimmering magical barrier surrounds you.")
        self.ui_manager.log_system("[+4 AC bonus for the next 10 minutes]")
        
        # In full implementation, would add temporary AC bonus
        return True
    
    def _spell_fireball(self, caster, target, spell) -> bool:
        """Fireball spell effect."""
        if not target or target.get('type') != 'enemy':
            self.ui_manager.log_error("You must target an enemy.")
            return False
        
        # Calculate damage (6d6)
        damage = self.dice_system.roll("6d6")
        target_name = target['name']
        
        self.ui_manager.log_success(f"You hurl a blazing sphere of fire at {target_name}!")
        self.ui_manager.log_success(f"The fireball explodes around {target_name} for {damage} fire damage!")
        
        return True
    
    def _spell_invisibility(self, caster, target, spell) -> bool:
        """Invisibility spell effect."""
        if target == caster:
            target_name = "You"
            self.ui_manager.log_success("You fade from view, becoming invisible.")
        else:
            target_name = target.get('name', 'The target')
            self.ui_manager.log_success(f"{target_name} fades from view, becoming invisible.")
        
        self.ui_manager.log_system("[Invisibility will last until you attack or cast a spell]")
        return True


# Test function
def _test_magic_system():
    """Test magic command system functionality."""
    from .dice_system import DiceSystem
    
    class MockUIManager:
        def log_success(self, msg): print(f"SUCCESS: {msg}")
        def log_error(self, msg): print(f"ERROR: {msg}")
        def log_info(self, msg): print(f"INFO: {msg}")
        def log_system(self, msg): print(f"SYSTEM: {msg}")
    
    class MockCharacter:
        def __init__(self, char_class="mage", level=3):
            self.name = "TestMage"
            self.character_class = char_class
            self.level = level
            self.intelligence = 16
            self.wisdom = 14
            
        def get_stat_modifier(self, stat):
            if stat == 'intelligence':
                return 3
            elif stat == 'wisdom':
                return 2
            return 0
    
    # Create test instances
    dice_system = DiceSystem(show_rolls=False)
    ui_manager = MockUIManager()
    magic_system = MagicCommandSystem(dice_system, ui_manager)
    
    mage = MockCharacter("mage", 3)
    warrior = MockCharacter("warrior", 3)
    
    # Test magic abilities
    assert magic_system.can_cast_spells(mage)
    assert not magic_system.can_cast_spells(warrior)
    
    # Test mana system
    current, maximum = magic_system.get_character_mana(mage)
    assert maximum > 0
    assert current == maximum
    
    # Test spell casting
    assert magic_system.attempt_cast_spell(mage, "magic missile", "goblin")
    
    print("Magic system tests passed!")


if __name__ == "__main__":
    _test_magic_system()