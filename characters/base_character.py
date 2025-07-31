"""
Base Character Class for Rogue City
Abstract base class providing core character functionality.
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import time


class BaseCharacter(ABC):
    """Base class for all character types with core functionality"""
    
    def __init__(self, name: str, character_class: str):
        """Initialize base character with name and class"""
        self.name = name
        self.character_class = character_class
        self.level = 0
        self.experience = 0
        
        # Base stats (3-18 range, 10 is average human)
        self.base_stats = {
            'strength': 10,
            'dexterity': 10,
            'constitution': 10,
            'intelligence': 10,
            'wisdom': 10,
            'charisma': 10
        }
        
        # Final stats (after all modifiers)
        self.stats = self.base_stats.copy()
        
        # Derived stats calculated from base stats
        self.max_hp = 0
        self.current_hp = 0
        self.armor_class = 10  # Base AC is 10
        self.base_attack_bonus = 0
        
        # Game state
        self.current_area = None
        self.current_room = None
        self.inventory = []
        self.equipped_items = {}
        
        # Character creation tracking
        self.unallocated_stats = 10  # Points to spend during creation
        self.creation_complete = False
        
    def apply_class_modifiers(self, class_data: Dict[str, Any]):
        """Apply class-specific stat modifiers to base stats"""
        modifiers = class_data.get('stat_modifiers', {})
        for stat, modifier in modifiers.items():
            if stat in self.stats:
                self.stats[stat] = self.base_stats[stat] + modifier
                
    def calculate_derived_stats(self):
        """Calculate HP, AC, attack bonus from base stats"""
        # HP calculation: hit die + CON modifier
        con_modifier = (self.stats['constitution'] - 10) // 2
        hit_die_value = self.get_hit_die_value()
        self.max_hp = max(1, hit_die_value + con_modifier)
        
        # Set current HP to max if this is first calculation
        if self.current_hp == 0:
            self.current_hp = self.max_hp
            
        # AC calculation: 10 + DEX modifier + armor bonuses
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        self.armor_class = 10 + dex_modifier  # + equipped armor bonuses
        
        # Attack bonus: level + primary stat modifier
        str_modifier = (self.stats['strength'] - 10) // 2
        self.base_attack_bonus = self.level + str_modifier
        
    @abstractmethod
    def get_hit_die_value(self) -> int:
        """Return hit die value for this class (4, 6, 8, 10, 12)"""
        pass
        
    @abstractmethod
    def get_hit_die_type(self) -> str:
        """Return hit die type as string (1d4, 1d6, 1d8, 1d10, 1d12)"""
        pass
        
    @abstractmethod
    def get_attack_speed(self) -> float:
        """Return base attack speed in seconds for this class"""
        pass
        
    @abstractmethod
    def get_critical_range(self) -> int:
        """Return critical hit range (20 = only natural 20, 19 = 19-20)"""
        pass
        
    def allocate_stat_point(self, stat_name: str) -> bool:
        """Allocate one stat point during character creation"""
        if self.unallocated_stats <= 0:
            return False
            
        if stat_name not in self.base_stats:
            return False
            
        # Increase base stat and recalculate
        self.base_stats[stat_name] += 1
        self.unallocated_stats -= 1
        self.recalculate_stats()
        return True
        
    def recalculate_stats(self):
        """Recalculate all derived stats after changes"""
        # Reapply class modifiers to updated base stats
        try:
            from core.save_manager import SaveManager
            save_manager = SaveManager()
            class_definitions = save_manager.load_class_definitions()
            if self.character_class in class_definitions:
                class_data = class_definitions[self.character_class]
                self.apply_class_modifiers(class_data)
        except ImportError:
            # If save manager not available, just apply stats as-is
            pass
            
        self.calculate_derived_stats()
        
    def gain_experience(self, amount: int):
        """Add experience and check for level up"""
        self.experience += amount
        required_exp = self.calculate_required_experience()
        
        while self.experience >= required_exp and self.level < 100:
            self.level_up()
            required_exp = self.calculate_required_experience()
            
    def calculate_required_experience(self) -> int:
        """Calculate XP needed for next level"""
        if self.level >= 100:
            return float('inf')  # Max level reached
            
        base_exp = 100
        multiplier = 1.5
        return int(base_exp * (multiplier ** self.level))
        
    def level_up(self):
        """Handle character level increase"""
        old_level = self.level
        self.level += 1
        self.unallocated_stats += 1  # Gain 1 stat point per level
        old_max_hp = self.max_hp
        
        # Roll for HP increase using dice system
        try:
            from core.dice_system import DiceSystem
            dice = DiceSystem(show_rolls=False)
            hit_die = self.get_hit_die_type()
            hp_roll = dice.roll(hit_die)
            
            con_modifier = (self.stats['constitution'] - 10) // 2
            hp_gain = max(1, hp_roll + con_modifier)  # Always gain at least 1 HP
            
            self.max_hp += hp_gain
            self.current_hp += hp_gain  # Heal to full on level up
            
        except ImportError:
            # Fallback if dice system not available
            con_modifier = (self.stats['constitution'] - 10) // 2
            avg_roll = (self.get_hit_die_value() + 1) // 2
            hp_gain = max(1, avg_roll + con_modifier)
            self.max_hp += hp_gain
            self.current_hp += hp_gain
            
        # Recalculate derived stats for new level
        self.calculate_derived_stats()
        
        return {
            'old_level': old_level,
            'new_level': self.level,
            'hp_gained': self.max_hp - old_max_hp,
            'stat_points_gained': 1
        }
        
    def get_stat_modifier(self, stat_name: str) -> int:
        """Get D&D style stat modifier for a given stat"""
        if stat_name not in self.stats:
            return 0
        return (self.stats[stat_name] - 10) // 2
        
    def heal(self, amount: int) -> int:
        """Heal character, return actual amount healed"""
        if self.current_hp >= self.max_hp:
            return 0
            
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
        
    def take_damage(self, amount: int) -> int:
        """Take damage, return actual damage taken"""
        if amount <= 0:
            return 0
            
        old_hp = self.current_hp
        self.current_hp = max(0, self.current_hp - amount)
        return old_hp - self.current_hp
        
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.current_hp > 0
        
    def get_hp_percentage(self) -> float:
        """Get HP as percentage (0.0 to 1.0)"""
        if self.max_hp <= 0:
            return 0.0
        return self.current_hp / self.max_hp
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Get class-specific special abilities (override in subclasses)"""
        return {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize character for saving to JSON"""
        return {
            'character_name': self.name,
            'character_class': self.character_class,
            'level': self.level,
            'experience': self.experience,
            'base_stats': self.base_stats.copy(),
            'stats': self.stats.copy(),
            'derived_stats': {
                'max_hp': self.max_hp,
                'current_hp': self.current_hp,
                'armor_class': self.armor_class,
                'base_attack_bonus': self.base_attack_bonus
            },
            'current_location': {
                'area_id': self.current_area,
                'room_id': self.current_room
            },
            'inventory': self.inventory.copy(),
            'equipped_items': self.equipped_items.copy(),
            'unallocated_stats': self.unallocated_stats,
            'creation_complete': self.creation_complete,
            'save_timestamp': time.time()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseCharacter':
        """Deserialize character from save data (implement in subclasses)"""
        raise NotImplementedError("from_dict must be implemented in character subclasses")
        
    def __str__(self) -> str:
        """String representation of character"""
        hp_status = f"{self.current_hp}/{self.max_hp}"
        return f"{self.name} the {self.character_class.title()} (Level {self.level}, HP: {hp_status})"
        
    def __repr__(self) -> str:
        """Debug representation of character"""
        return f"<{self.__class__.__name__}: {self.name}, Level {self.level}, HP: {self.current_hp}/{self.max_hp}>"