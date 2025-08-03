from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseRace(ABC):
    """
    Abstract base class for all character races in the MajorMUD-style race system.
    Defines the interface for racial stat modifiers, special abilities, and experience costs.
    """
    
    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.stat_modifiers = self.get_stat_modifiers()
        self.special_abilities = self.get_special_abilities()
        self.experience_modifier = self.get_experience_modifier()
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the display name of this race"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return the descriptive text for this race"""
        pass
    
    @abstractmethod
    def get_stat_modifiers(self) -> Dict[str, int]:
        """
        Return stat modifiers for this race.
        Keys: 'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'
        Values: Integer modifiers (positive or negative)
        """
        pass
    
    @abstractmethod
    def get_special_abilities(self) -> Dict[str, Any]:
        """
        Return special racial abilities.
        Each ability should have a name as key and configuration as value.
        """
        pass
    
    @abstractmethod
    def get_experience_modifier(self) -> int:
        """
        Return experience cost modifier as percentage.
        0 = baseline, positive values increase XP requirements, negative values decrease them.
        """
        pass
    
    def apply_stat_modifiers(self, base_stats: Dict[str, int]) -> Dict[str, int]:
        """
        Apply racial stat modifiers to base character stats.
        
        Args:
            base_stats: Dictionary of base stats to modify
            
        Returns:
            Dictionary of modified stats
        """
        modified_stats = base_stats.copy()
        
        for stat_name, modifier in self.stat_modifiers.items():
            if stat_name in modified_stats:
                modified_stats[stat_name] += modifier
                # Ensure stats don't go below 1
                modified_stats[stat_name] = max(1, modified_stats[stat_name])
        
        return modified_stats
    
    def has_ability(self, ability_name: str) -> bool:
        """Check if this race has a specific special ability"""
        return ability_name in self.special_abilities
    
    def get_ability_value(self, ability_name: str, default=None):
        """Get the configuration value for a special ability"""
        return self.special_abilities.get(ability_name, default)
    
    def calculate_experience_requirement(self, base_xp: int) -> int:
        """
        Calculate the modified experience requirement for this race.
        
        Args:
            base_xp: Base experience requirement
            
        Returns:
            Modified experience requirement
        """
        modifier = 1.0 + (self.experience_modifier / 100.0)
        return int(base_xp * modifier)
    
    def get_stat_summary(self) -> str:
        """Get a formatted string showing stat modifiers"""
        modifiers = []
        for stat, mod in self.stat_modifiers.items():
            if mod != 0:
                stat_abbrev = stat[:3].upper()
                sign = "+" if mod > 0 else ""
                modifiers.append(f"{sign}{mod} {stat_abbrev}")
        
        return ", ".join(modifiers) if modifiers else "No stat modifiers"
    
    def get_abilities_summary(self) -> str:
        """Get a formatted string showing special abilities"""
        abilities = list(self.special_abilities.keys())
        if not abilities:
            return "No special abilities"
        
        return ", ".join(abilities)
    
    def get_display_info(self) -> str:
        """Get formatted display information for race selection"""
        exp_text = f"+{self.experience_modifier}%" if self.experience_modifier >= 0 else f"{self.experience_modifier}%"
        
        return (f"{self.name}\n"
                f"  {self.description}\n"
                f"  Stat Modifiers: {self.get_stat_summary()}\n"
                f"  Special Abilities: {self.get_abilities_summary()}\n"
                f"  Experience Cost: {exp_text}")