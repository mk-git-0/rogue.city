"""
Spell Factory for Rogue City
Centralized spell creation and management.
"""

from typing import Dict, List, Optional, Type
from .base_spell import BaseSpell


class SpellFactory:
    """
    Factory for creating and managing spell instances
    """
    
    def __init__(self):
        """Initialize spell factory"""
        self.spell_classes = {}
        self.spell_instances = {}
        self._register_spells()
        
    def _register_spells(self):
        """Register all available spell classes"""
        try:
            from .mage_spells import MAGE_SPELLS
            from .priest_spells import PRIEST_SPELLS
            from .druid_spells import DRUID_SPELLS
            
            # Register mage spells
            for spell_class in MAGE_SPELLS:
                spell_instance = spell_class()
                spell_key = spell_instance.name.lower().replace(' ', '_')
                self.spell_classes[spell_key] = spell_class
                self.spell_instances[spell_key] = spell_instance
                
            # Register priest spells
            for spell_class in PRIEST_SPELLS:
                spell_instance = spell_class()
                spell_key = spell_instance.name.lower().replace(' ', '_')
                self.spell_classes[spell_key] = spell_class
                self.spell_instances[spell_key] = spell_instance
                
            # Register druid spells
            for spell_class in DRUID_SPELLS:
                spell_instance = spell_class()
                spell_key = spell_instance.name.lower().replace(' ', '_')
                self.spell_classes[spell_key] = spell_class
                self.spell_instances[spell_key] = spell_instance
                
        except ImportError:
            # Spell modules not yet implemented
            pass
            
    def create_spell(self, spell_name: str) -> Optional[BaseSpell]:
        """Create a new instance of a spell"""
        spell_key = spell_name.lower().replace(' ', '_')
        spell_class = self.spell_classes.get(spell_key)
        
        if spell_class:
            return spell_class()
        return None
        
    def get_spell(self, spell_name: str) -> Optional[BaseSpell]:
        """Get existing spell instance"""
        spell_key = spell_name.lower().replace(' ', '_')
        return self.spell_instances.get(spell_key)
        
    def get_spells_by_school(self, school: str) -> List[BaseSpell]:
        """Get all spells from a specific school"""
        spells = []
        for spell in self.spell_instances.values():
            if spell.school == school:
                spells.append(spell)
        return spells
        
    def get_spells_by_level(self, level: int, school: str = None) -> List[BaseSpell]:
        """Get all spells of a specific level, optionally filtered by school"""
        spells = []
        for spell in self.spell_instances.values():
            if spell.level == level:
                if school is None or spell.school == school:
                    spells.append(spell)
        return spells
        
    def get_all_spells(self) -> Dict[str, BaseSpell]:
        """Get all registered spells"""
        return self.spell_instances.copy()
        
    def get_spell_names(self) -> List[str]:
        """Get list of all spell names"""
        return [spell.name for spell in self.spell_instances.values()]
        
    def register_spell(self, spell_class: Type[BaseSpell]):
        """Register a new spell class"""
        spell_instance = spell_class()
        spell_key = spell_instance.name.lower().replace(' ', '_')
        self.spell_classes[spell_key] = spell_class
        self.spell_instances[spell_key] = spell_instance