"""
Base Character Class for Rogue City
Abstract base class providing core character functionality.
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import time
from core.alignment_system import Alignment
from characters.alignment_manager import AlignmentManager
from core.reputation_manager import ReputationManager


class BaseCharacter(ABC):
    """Base class for all character types with core functionality"""
    
    def __init__(self, name: str, character_class: str, race_id: str = "human", alignment: Alignment = Alignment.NEUTRAL):
        """Initialize base character with name, class, race, and alignment"""
        self.name = name
        self.character_class = character_class
        self.race_id = race_id
        self.race = None
        self.level = 1  # Start at level 1
        self.experience = 0
        
        # Initialize alignment system
        self.alignment_manager = AlignmentManager(alignment)
        self.alignment_manager.character_name = name  # For reputation tracking
        
        # Initialize reputation manager
        self.reputation_manager = ReputationManager(name)
        
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
        
        # Magic system integration
        self.max_mana = 0
        self.current_mana = 0
        self.known_spells = []
        
        # Currency system integration
        self.currency = None  # Will be initialized when currency system is available
        
        # Initialize magic system for spellcasting classes
        self._initialize_magic_system()
        
        # Initialize currency system
        self._initialize_currency_system()
        
        # Calculate initial derived stats after class modifiers are applied
        self.calculate_derived_stats()
        
        # Game state
        self.current_area = None
        self.current_room = None
        
        # Item systems - initialized after character creation
        self.inventory_system = None
        self.equipment_system = None
        
        # Skill tracking for practice-based improvement
        self.skill_experience = {}  # Dict[skill_name, usage_count]
        
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
            
    def _initialize_magic_system(self):
        """Initialize magic system for spellcasting classes"""
        try:
            from core.magic_system import MagicSystem
            magic_system = MagicSystem()
            
            if magic_system.is_spellcaster(self.character_class):
                # Get starting spells for this class
                self.known_spells = magic_system.get_starting_spells(self.character_class).copy()
            else:
                self.known_spells = []
        except ImportError:
            self.known_spells = []
    
    def _initialize_currency_system(self):
        """Initialize currency system for new characters"""
        try:
            from core.currency_system import Currency, CurrencySystem
            currency_system = CurrencySystem()
            
            # For new characters, generate starting gold
            if self.currency is None:
                self.currency = currency_system.calculate_starting_gold(self.character_class, self.level)
        except ImportError:
            # Fallback if currency system not available
            from core.currency_system import Currency
            self.currency = Currency(gold=50)  # Default starting gold
        
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
            # Include shield base AC if present
            shield_bonus = 0
            if hasattr(self.equipment_system, 'get_shield_ac_bonus'):
                shield_bonus = self.equipment_system.get_shield_ac_bonus()
            max_dex = self.equipment_system.get_max_dex_bonus()
            if max_dex is not None:
                dex_modifier = min(dex_modifier, max_dex)
            self.armor_class = base_ac + racial_ac_bonus + armor_bonus + shield_bonus
        else:
            self.armor_class = base_ac + racial_ac_bonus
        
        # Attack bonus: level + primary stat modifier
        str_modifier = (self.stats['strength'] - 10) // 2
        self.base_attack_bonus = self.level + str_modifier
        
        # Mana calculation for spellcasting classes
        self._calculate_mana()
        
    def _calculate_mana(self):
        """Calculate mana pool for spellcasting classes"""
        try:
            from core.magic_system import MagicSystem
            magic_system = MagicSystem()
            
            if magic_system.is_spellcaster(self.character_class):
                self.max_mana = magic_system.calculate_max_mana(self)
                # Set current mana to max if this is first calculation
                if self.current_mana == 0:
                    self.current_mana = self.max_mana
            else:
                self.max_mana = 0
                self.current_mana = 0
        except ImportError:
            self.max_mana = 0
            self.current_mana = 0
        
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
        
    @abstractmethod
    def get_experience_penalty(self) -> int:
        """Return experience penalty percentage for this class (0-100)"""
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
        """Calculate XP needed for next level with racial and class modifiers"""
        if self.level >= 100:
            return float('inf')  # Max level reached
            
        base_exp = 100
        multiplier = 1.5
        base_requirement = int(base_exp * (multiplier ** self.level))
        
        # Apply class experience penalty first
        class_penalty = self.get_experience_penalty()
        class_modified_exp = int(base_requirement * (1.0 + class_penalty / 100.0))
        
        # Apply racial experience modifier to class-modified amount
        if self.race:
            return self.race.calculate_experience_requirement(class_modified_exp)
        
        return class_modified_exp
        
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
        
        # Learn new spells for spellcasting classes
        new_spells = self._learn_spells_on_levelup()
        
        return {
            'old_level': old_level,
            'new_level': self.level,
            'hp_gained': self.max_hp - old_max_hp,
            'stat_points_gained': 1,
            'new_spells': new_spells
        }
        
    def _learn_spells_on_levelup(self) -> List[str]:
        """Learn new spells when leveling up"""
        try:
            from core.spell_system import SpellSystem
            spell_system = SpellSystem()
            return spell_system.learn_spell_on_levelup(self)
        except ImportError:
            return []
        
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
            if slot in ['weapon', 'armor', 'shield']:
                self.equipment_system.equip_item(item.item_id)
    
    def restore_mana(self, amount: int) -> int:
        """Restore mana for spellcasting classes"""
        if self.max_mana <= 0:
            return 0  # Non-spellcasting classes
            
        if self.current_mana >= self.max_mana:
            return 0  # Already at full mana
            
        old_mana = self.current_mana
        self.current_mana = min(self.max_mana, self.current_mana + amount)
        return self.current_mana - old_mana
        
    def spend_mana(self, amount: int) -> bool:
        """Spend mana for spell casting"""
        if self.current_mana < amount:
            return False
        self.current_mana -= amount
        return True
        
    def get_mana_percentage(self) -> float:
        """Get mana as percentage (0.0 to 1.0)"""
        if self.max_mana <= 0:
            return 0.0
        return self.current_mana / self.max_mana
        
    def is_spellcaster(self) -> bool:
        """Check if this character can cast spells"""
        return self.max_mana > 0
        
    def knows_spell(self, spell_name: str) -> bool:
        """Check if character knows a specific spell"""
        return spell_name.lower() in [spell.lower() for spell in self.known_spells]
        
    def learn_spell(self, spell_name: str) -> bool:
        """Learn a new spell"""
        if not self.knows_spell(spell_name):
            self.known_spells.append(spell_name)
            return True
        return False
    
    def track_skill_usage(self, skill_name: str) -> None:
        """Track skill usage for practice-based improvement"""
        if skill_name not in self.skill_experience:
            self.skill_experience[skill_name] = 0
        self.skill_experience[skill_name] += 1
    
    def get_skill_experience(self, skill_name: str) -> int:
        """Get the experience (usage count) for a specific skill"""
        return self.skill_experience.get(skill_name, 0)
        
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
    
    def get_alignment(self) -> Alignment:
        """Get character's current alignment"""
        return self.alignment_manager.get_alignment()
    
    def set_alignment(self, new_alignment: Alignment) -> bool:
        """Set character alignment (usually for character creation)"""
        return self.alignment_manager.set_alignment(new_alignment)
    
    def get_alignment_display(self) -> str:
        """Get formatted alignment information"""
        return self.alignment_manager.get_alignment_display()
    
    def get_reputation(self, faction: str) -> int:
        """Get reputation with a specific faction"""
        return self.alignment_manager.get_reputation(faction)
    
    def modify_reputation(self, faction: str, change: int) -> int:
        """Modify reputation with a faction"""
        return self.alignment_manager.modify_reputation(faction, change)
    
    def can_use_item_alignment(self, item_alignment: Optional[str]) -> tuple[bool, str]:
        """Check if character can use an item based on alignment"""
        return self.alignment_manager.can_use_item(item_alignment)
    
    def get_npc_reaction_modifier(self, npc_alignment: Alignment) -> int:
        """Get reaction modifier when interacting with an NPC"""
        return self.alignment_manager.get_npc_reaction_modifier(npc_alignment)
    
    def add_alignment_drift(self, action_type: str) -> bool:
        """Add alignment drift based on character actions"""
        return self.alignment_manager.add_alignment_drift(action_type)
    
    def get_alignment_bonuses(self) -> Dict[str, int]:
        """Get stat bonuses from current alignment"""
        return self.alignment_manager.get_alignment_bonuses()
    
    def load_alignment_data(self, alignment_data: Dict):
        """Load alignment data from save file"""
        if alignment_data:
            self.alignment_manager = AlignmentManager.load_from_dict(alignment_data)
            self.alignment_manager.character_name = self.name
        else:
            # Default to neutral alignment for legacy characters
            self.alignment_manager = AlignmentManager(Alignment.NEUTRAL)
            self.alignment_manager.character_name = self.name
    
    def load_currency_data(self, currency_data: Dict):
        """Load currency data from save file"""
        try:
            from core.currency_system import Currency
            if currency_data:
                self.currency = Currency(
                    currency_data.get('gold', 0),
                    currency_data.get('silver', 0),
                    currency_data.get('copper', 0)
                )
            else:
                # Default currency for legacy characters
                self.currency = Currency(gold=50)
        except ImportError:
            from core.currency_system import Currency
            self.currency = Currency(gold=50)
    
    def load_reputation_data(self, reputation_data: Dict):
        """Load reputation data from save file"""
        if reputation_data:
            self.reputation_manager.load_from_dict(reputation_data)
        else:
            # Initialize with default reputation for legacy characters
            self.reputation_manager = ReputationManager(self.name)
    
    def get_character_display(self) -> str:
        """Get detailed character information for display"""
        lines = []
        
        # Header
        race_name = self.race.name if self.race else "Unknown"
        alignment_display = self.alignment_manager.get_alignment_display()
        lines.append(f"=== {self.name.upper()} THE {race_name.upper()} {self.character_class.upper()} ===")
        lines.append(f"Race: {race_name}      Alignment: {alignment_display.split(' - ')[0]}")
        exp_penalty = self.get_experience_penalty()
        exp_display = f" (+{exp_penalty}% exp)" if exp_penalty > 0 else ""
        lines.append(f"Level: {self.level}           Experience: {self.experience}/{self.calculate_required_experience()}{exp_display}")
        lines.append(f"HP: {self.current_hp}/{self.max_hp}          AC: {self.armor_class}")
        if self.currency:
            lines.append(f"Wealth: {self.currency}")
        lines.append("")
        
        # Reputation section
        lines.append("Reputation:")
        reputation_lines = self.alignment_manager.get_reputation_display()
        lines.extend(reputation_lines)
        lines.append("")
        
        # Stats
        lines.append("STR: {0:2d}  DEX: {1:2d}  CON: {2:2d}  INT: {3:2d}  WIS: {4:2d}  CHA: {5:2d}".format(
            self.stats['strength'], self.stats['dexterity'], self.stats['constitution'],
            self.stats['intelligence'], self.stats['wisdom'], self.stats['charisma']
        ))
        
        # Alignment bonuses
        alignment_bonuses = self.get_alignment_bonuses()
        if alignment_bonuses:
            bonus_descriptions = []
            for bonus_type, value in alignment_bonuses.items():
                if value > 0:
                    bonus_descriptions.append(f"+{value} {bonus_type.replace('_', ' ')}")
            if bonus_descriptions:
                lines.append(f"Alignment Bonuses: {', '.join(bonus_descriptions)}")
        
        return "\n".join(lines)
        
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
            'alignment_data': self.alignment_manager.save_to_dict(),
            'reputation_data': self.reputation_manager.save_to_dict(),
            'magic_data': {
                'max_mana': self.max_mana,
                'current_mana': self.current_mana,
                'known_spells': self.known_spells.copy()
            },
            'currency_data': {
                'gold': self.currency.gold if self.currency else 0,
                'silver': self.currency.silver if self.currency else 0,
                'copper': self.currency.copper if self.currency else 0
            },
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