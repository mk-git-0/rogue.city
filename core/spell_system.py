"""
Spell System for Rogue City
Manages spell casting, effects, and integration with combat system.
"""

from typing import Dict, List, Optional, Any, Tuple
import json
import os


class SpellSystem:
    """
    Manages all spell casting mechanics and effects
    """
    
    def __init__(self, dice_system=None, ui_manager=None):
        """Initialize spell system"""
        self.dice_system = dice_system
        self.ui_manager = ui_manager
        self.spell_registry = {}
        self.active_spell_effects = {}  # Track ongoing spell effects
        
        # Initialize spell registry
        self._initialize_spells()
        
    def _initialize_spells(self):
        """Initialize all available spells"""
        try:
            from spells.mage_spells import MAGE_SPELLS
            from spells.priest_spells import PRIEST_SPELLS
            from spells.druid_spells import DRUID_SPELLS
            
            # Register all spells
            for spell_class in MAGE_SPELLS:
                spell_instance = spell_class()
                self.spell_registry[spell_instance.name.lower().replace(' ', '_')] = spell_instance
                
            for spell_class in PRIEST_SPELLS:
                spell_instance = spell_class()
                self.spell_registry[spell_instance.name.lower().replace(' ', '_')] = spell_instance
                
            for spell_class in DRUID_SPELLS:
                spell_instance = spell_class()
                self.spell_registry[spell_instance.name.lower().replace(' ', '_')] = spell_instance
                
        except ImportError:
            # Spells not yet implemented, create empty registry
            pass
            
    def get_spell(self, spell_name: str):
        """Get spell instance by name"""
        spell_key = spell_name.lower().replace(' ', '_')
        return self.spell_registry.get(spell_key)
        
    def get_spell_data(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """Get spell data dictionary"""
        spell = self.get_spell(spell_name)
        if spell:
            return spell.get_display_info()
        return None
        
    def can_cast_spell(self, caster, spell_name: str, target=None) -> Tuple[bool, str]:
        """Check if character can cast a specific spell"""
        # Check if character knows the spell
        if hasattr(caster, 'known_spells'):
            if spell_name not in caster.known_spells:
                return False, f"You don't know the spell '{spell_name}'"
        else:
            return False, "You don't know any spells"
            
        # Get spell instance
        spell = self.get_spell(spell_name)
        if not spell:
            return False, f"Spell '{spell_name}' not found"
            
        # Check if spell can be cast
        return spell.can_cast(caster, target)
        
    def cast_spell(self, caster, spell_name: str, target=None, combat_system=None) -> Tuple[bool, str, Dict[str, Any]]:
        """Cast a spell"""
        # Check if spell can be cast
        can_cast, reason = self.can_cast_spell(caster, spell_name, target)
        if not can_cast:
            return False, reason, {}
            
        # Get spell instance
        spell = self.get_spell(spell_name)
        if not spell:
            return False, f"Spell '{spell_name}' not found", {}
            
        # Consume mana
        mana_cost = spell.get_mana_cost(caster)
        if hasattr(caster, 'current_mana'):
            caster.current_mana -= mana_cost
            
        # Cast the spell
        success, message, effects_data = spell.cast(caster, target, combat_system, self.ui_manager)
        
        if success and self.ui_manager:
            self.ui_manager.log_success(f"You cast {spell.name}!")
            if message:
                self.ui_manager.log_info(message)
        elif not success and self.ui_manager:
            self.ui_manager.log_error(f"Failed to cast {spell.name}: {message}")
            
        return success, message, effects_data
        
    def get_available_spells(self, character_class: str, level: int) -> List[str]:
        """Get spells available to a class at a given level"""
        available_spells = []
        
        try:
            from core.magic_system import MagicSystem, SpellSchool
            magic_system = MagicSystem()
            
            spell_schools = magic_system.get_spell_schools(character_class)
            
            for spell_name, spell in self.spell_registry.items():
                # Check if spell school matches
                school_match = False
                for school in spell_schools:
                    if school.value == spell.school:
                        school_match = True
                        break
                        
                if not school_match:
                    continue
                    
                # Check level requirement
                min_level = spell.level * 2 - 1 if spell.level > 0 else 1
                if level >= min_level:
                    available_spells.append(spell_name)
                    
        except ImportError:
            pass
            
        return available_spells
        
    def learn_spell_on_levelup(self, character) -> List[str]:
        """Automatically learn spells when character levels up"""
        if not hasattr(character, 'character_class') or not hasattr(character, 'level'):
            return []
            
        # Only learn spells at odd levels (3, 5, 7, etc.)
        if character.level % 2 == 0 or character.level < 3:
            return []
            
        try:
            from core.magic_system import MagicSystem
            magic_system = MagicSystem()
            
            if not magic_system.is_spellcaster(character.character_class):
                return []
                
            available_spells = self.get_available_spells(character.character_class, character.level)
            new_spells = []
            
            # Learn 1-2 new spells depending on class and level
            spells_to_learn = 1
            if character.character_class.lower() == 'mage' and character.level >= 5:
                spells_to_learn = 2  # Mages learn more spells
                
            learned_count = 0
            for spell_name in available_spells:
                if spell_name not in character.known_spells and learned_count < spells_to_learn:
                    character.known_spells.append(spell_name)
                    new_spells.append(spell_name)
                    learned_count += 1
                    
            return new_spells
            
        except ImportError:
            return []
            
    def get_spell_list_display(self, character) -> List[str]:
        """Get formatted spell list for character display"""
        if not hasattr(character, 'known_spells'):
            return ["No spells known"]
            
        spell_lines = []
        for spell_name in character.known_spells:
            spell = self.get_spell(spell_name)
            if spell:
                mana_cost = spell.get_mana_cost(character)
                school_name = spell.school.title()
                spell_lines.append(f"{spell.name} (Level {spell.level} {school_name}, {mana_cost} mana)")
            else:
                spell_lines.append(f"{spell_name} (Unknown spell)")
                
        return spell_lines if spell_lines else ["No spells known"]
        
    def process_spell_effects(self, character) -> List[str]:
        """Process ongoing spell effects for a character"""
        char_id = character.name if hasattr(character, 'name') else str(id(character))
        
        if char_id not in self.active_spell_effects:
            return []
            
        effects = self.active_spell_effects[char_id]
        expired_effects = []
        messages = []
        
        for i, effect in enumerate(effects):
            effect['duration'] -= 1
            
            if effect['duration'] <= 0:
                expired_effects.append(i)
                messages.append(f"{effect['name']} effect wears off")
            elif effect['duration'] <= 3:
                messages.append(f"{effect['name']} effect is fading")
                
        # Remove expired effects (in reverse order to maintain indices)
        for i in reversed(expired_effects):
            effects.pop(i)
            
        if not effects:
            del self.active_spell_effects[char_id]
            
        return messages
        
    def add_spell_effect(self, character, effect_name: str, duration: int, effect_data: Dict[str, Any]):
        """Add a temporary spell effect to character"""
        char_id = character.name if hasattr(character, 'name') else str(id(character))
        
        if char_id not in self.active_spell_effects:
            self.active_spell_effects[char_id] = []
            
        effect = {
            'name': effect_name,
            'duration': duration,
            'data': effect_data
        }
        
        self.active_spell_effects[char_id].append(effect)
        
    def get_active_effects(self, character) -> List[Dict[str, Any]]:
        """Get list of active spell effects on character"""
        char_id = character.name if hasattr(character, 'name') else str(id(character))
        return self.active_spell_effects.get(char_id, [])
        
    def has_spell_effect(self, character, effect_name: str) -> bool:
        """Check if character has a specific spell effect active"""
        effects = self.get_active_effects(character)
        return any(effect['name'] == effect_name for effect in effects)