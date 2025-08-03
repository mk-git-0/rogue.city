"""
Base Character Class for Rogue City
Abstract base class providing core character functionality.
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import time


class BaseCharacter(ABC):
    """Base class for all character types with core functionality"""
    
    def __init__(self, name: str, character_class: str, race_id: str = "human"):
        """Initialize base character with name, class, and race"""
        self.name = name
        self.character_class = character_class
        self.race_id = race_id
        self.race = None
        self.level = 1  # Start at level 1
        self.experience = 0
        
        # Initialize race
        self._initialize_race()
        
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
        
        # Apply class modifiers during initialization
        self._apply_initial_class_modifiers()
        
        # Derived stats calculated from base stats
        self.max_hp = 0
        self.current_hp = 0
        self.armor_class = 10  # Base AC is 10
        self.base_attack_bonus = 0
        
        # Calculate initial derived stats after class modifiers are applied
        self.calculate_derived_stats()
        
        # Game state
        self.current_area = None
        self.current_room = None
        
        # Item systems - initialized after character creation
        self.inventory_system = None
        self.equipment_system = None
        
        # Character creation tracking
        self.unallocated_stats = 10  # Points to spend during creation
        self.creation_complete = False
        
    def _initialize_race(self):
        """Initialize the character's race"""
        try:
            from characters.races import get_race_class
            race_class = get_race_class(self.race_id)
            if race_class:
                self.race = race_class()
            else:
                # Default to human if race not found
                from characters.races.race_human import Human
                self.race = Human()
                self.race_id = "human"
        except ImportError:
            # If races module not available, create a basic race object
            self.race = None
        
    def _apply_initial_class_modifiers(self):
        """Apply class modifiers during character initialization"""
        try:
            from core.save_manager import SaveManager
            save_manager = SaveManager()
            class_definitions = save_manager.load_class_definitions()
            if self.character_class in class_definitions:
                class_data = class_definitions[self.character_class]
                self.apply_class_modifiers(class_data)
        except (ImportError, Exception):
            pass
        
    def apply_class_modifiers(self, class_data: Dict[str, Any]):
        """Apply class-specific stat modifiers to base stats"""
        # Start with base stats
        self.stats = self.base_stats.copy()
        
        # Apply racial modifiers first
        if self.race:
            self.stats = self.race.apply_stat_modifiers(self.stats)
        
        # Then apply class modifiers
        class_modifiers = class_data.get('stat_modifiers', {})
        for stat, modifier in class_modifiers.items():
            if stat in self.stats:
                self.stats[stat] += modifier
                
    def calculate_derived_stats(self):
        """Calculate HP, AC, attack bonus from base stats"""
        # HP calculation: hit die + CON modifier
        con_modifier = (self.stats['constitution'] - 10) // 2
        hit_die_value = self.get_hit_die_value()
        self.max_hp = max(1, hit_die_value + con_modifier)
        
        # Set current HP to max if this is first calculation
        if self.current_hp == 0:
            self.current_hp = self.max_hp
            
        # AC calculation: 10 + DEX modifier + racial bonuses + armor bonuses
        dex_modifier = (self.stats['dexterity'] - 10) // 2
        base_ac = 10 + dex_modifier
        
        # Add racial AC bonuses
        racial_ac_bonus = 0
        if self.race:
            for ability_name, ability_data in self.race.special_abilities.items():
                if isinstance(ability_data, dict) and 'ac_bonus' in ability_data:
                    racial_ac_bonus += ability_data['ac_bonus']
        
        # Add equipment bonuses if available
        if hasattr(self, 'equipment_system') and self.equipment_system:
            armor_bonus = self.equipment_system.get_armor_class_bonus()
            max_dex = self.equipment_system.get_max_dex_bonus()
            if max_dex is not None:
                dex_modifier = min(dex_modifier, max_dex)
            self.armor_class = base_ac + racial_ac_bonus + armor_bonus
        else:
            self.armor_class = base_ac + racial_ac_bonus
        
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
        """Return attack speed in seconds (considering equipped weapon)"""
        if hasattr(self, 'equipment_system') and self.equipment_system:
            return self.equipment_system.get_attack_speed_modifier()
        return self.get_base_attack_speed()
    
    @abstractmethod
    def get_base_attack_speed(self) -> float:
        """Return base attack speed in seconds for this class (unarmed)"""
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
        """Calculate XP needed for next level with racial modifiers"""
        if self.level >= 100:
            return float('inf')  # Max level reached
            
        base_exp = 100
        multiplier = 1.5
        base_requirement = int(base_exp * (multiplier ** self.level))
        
        # Apply racial experience modifier
        if self.race:
            return self.race.calculate_experience_requirement(base_requirement)
        
        return base_requirement
        
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
    
    def initialize_item_systems(self):
        """Initialize inventory and equipment systems"""
        from core.inventory_system import InventorySystem
        from core.equipment_system import EquipmentSystem
        from core.item_factory import ItemFactory
        
        # Initialize systems
        self.inventory_system = InventorySystem(self)
        self.equipment_system = EquipmentSystem(self, self.inventory_system)
        
        # Give starting equipment for this class
        item_factory = ItemFactory()
        starting_equipment = item_factory.get_starting_equipment(self.character_class)
        
        for slot, item in starting_equipment.items():
            self.inventory_system.add_item(item)
            if slot in ['weapon', 'armor']:
                self.equipment_system.equip_item(item.item_id)
    
    def restore_mana(self, amount: int) -> int:
        """Restore mana (for mage classes). Override in mage subclass."""
        return 0  # Base classes don't have mana
        
    def get_special_abilities(self) -> Dict[str, Any]:
        """Get class-specific special abilities (override in subclasses)"""
        return {}
    
    def get_racial_abilities(self) -> Dict[str, Any]:
        """Get racial special abilities"""
        if self.race:
            return self.race.special_abilities
        return {}
    
    def has_racial_ability(self, ability_name: str) -> bool:
        """Check if character has a specific racial ability"""
        if self.race:
            return self.race.has_ability(ability_name)
        return False
    
    def get_racial_ability_value(self, ability_name: str, default=None):
        """Get the value of a racial ability"""
        if self.race:
            return self.race.get_ability_value(ability_name, default)
        return default
    
    def get_race_info(self) -> str:
        """Get formatted race information"""
        if self.race:
            return self.race.get_display_info()
        return "Unknown Race"
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize character for saving to JSON"""
        save_data = {
            'character_name': self.name,
            'character_class': self.character_class,
            'race_id': self.race_id,
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
            'unallocated_stats': self.unallocated_stats,
            'creation_complete': self.creation_complete,
            'save_timestamp': time.time()
        }
        
        # Add inventory and equipment data if systems are initialized
        if self.inventory_system:
            save_data['inventory'] = self.inventory_system.to_dict()
        else:
            save_data['inventory'] = {'items': {}, 'max_weight': 50.0}
            
        if self.equipment_system:
            save_data['equipment'] = self.equipment_system.to_dict()
        else:
            save_data['equipment'] = {'equipped_items': {}, 'applied_bonuses': {}}
        
        return save_data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseCharacter':
        """Deserialize character from save data (implement in subclasses)"""
        raise NotImplementedError("from_dict must be implemented in character subclasses")
        
    def __str__(self) -> str:
        """String representation of character"""
        hp_status = f"{self.current_hp}/{self.max_hp}"
        race_name = self.race.name if self.race else "Unknown"
        return f"{self.name} the {race_name} {self.character_class.title()} (Level {self.level}, HP: {hp_status})"
        
    def __repr__(self) -> str:
        """Debug representation of character"""
        return f"<{self.__class__.__name__}: {self.name}, Level {self.level}, HP: {self.current_hp}/{self.max_hp}>"