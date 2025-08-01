"""
Base Enemy Class for Rogue City
Abstract base class providing core enemy functionality and combat integration.
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import random


class BaseEnemy(ABC):
    """Base class for all enemy types with core combat functionality"""
    
    def __init__(self, name: str, enemy_type: str):
        """Initialize base enemy with name and type"""
        self.name = name
        self.enemy_type = enemy_type
        self.combat_id = None  # Set by combat system
        
        # Core stats
        self.level = 1
        self.max_hp = 10
        self.current_hp = 10
        self.armor_class = 10
        self.attack_bonus = 0
        self.damage_dice = "1d4"
        
        # Combat properties
        self.attack_speed = 3.0  # Default 3 second attack speed
        self.experience_value = 10
        self.difficulty_rating = 1
        
        # Loot and rewards
        self.loot_table = []
        self.gold_min = 0
        self.gold_max = 5
        
        # Status effects and conditions
        self.status_effects = []
        self.is_hostile = True
        self.is_fleeing = False
        
        # AI behavior flags
        self.ai_aggressive = True
        self.ai_intelligent = False
        self.ai_pack_hunter = False
        
    @abstractmethod
    def get_attack_speed(self) -> float:
        """Return attack speed in seconds for this enemy type"""
        pass
        
    @abstractmethod
    def get_special_abilities(self) -> List[str]:
        """Return list of special abilities this enemy can use"""
        pass
        
    def is_alive(self) -> bool:
        """Check if enemy is alive"""
        return self.current_hp > 0
        
    def take_damage(self, amount: int) -> int:
        """
        Take damage and return actual amount taken.
        
        Args:
            amount: Damage amount to apply
            
        Returns:
            Actual damage taken after any reductions
        """
        if amount <= 0:
            return 0
            
        # Apply any damage resistances or special effects here
        actual_damage = self._apply_damage_modifiers(amount)
        
        old_hp = self.current_hp
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        return old_hp - self.current_hp
        
    def heal(self, amount: int) -> int:
        """
        Heal enemy and return actual amount healed.
        
        Args:
            amount: Healing amount to apply
            
        Returns:
            Actual amount healed
        """
        if amount <= 0:
            return 0
            
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        
        return self.current_hp - old_hp
        
    def get_hp_percentage(self) -> float:
        """Get HP as percentage (0.0 to 1.0)"""
        if self.max_hp <= 0:
            return 0.0
        return self.current_hp / self.max_hp
        
    def get_loot(self) -> List[Dict[str, Any]]:
        """
        Generate loot when enemy dies.
        
        Returns:
            List of loot items
        """
        loot = []
        
        # Roll for each item in loot table
        for loot_entry in self.loot_table:
            if self._roll_loot_chance(loot_entry.get('chance', 100)):
                loot.append({
                    'name': loot_entry['name'],
                    'type': loot_entry.get('type', 'misc'),
                    'quantity': loot_entry.get('quantity', 1)
                })
                
        # Roll for gold
        if self.gold_max > 0:
            gold_amount = random.randint(self.gold_min, self.gold_max)
            if gold_amount > 0:
                loot.append({
                    'name': 'Gold',
                    'type': 'currency',
                    'quantity': gold_amount
                })
                
        return loot
        
    def get_combat_actions(self) -> List[str]:
        """
        Get available combat actions for this enemy.
        
        Returns:
            List of action names
        """
        actions = ['attack']
        actions.extend(self.get_special_abilities())
        return actions
        
    def choose_combat_action(self, target, allies: List['BaseEnemy'] = None) -> str:
        """
        AI chooses what action to take in combat.
        
        Args:
            target: The target (usually player character)
            allies: Other enemies in the same combat
            
        Returns:
            Action name to perform
        """
        # Simple AI - always attack for now
        # More complex AI can be implemented in subclasses
        return 'attack'
        
    def get_attack_target(self, possible_targets: List[Any]) -> Optional[Any]:
        """
        AI chooses attack target.
        
        Args:
            possible_targets: List of possible targets
            
        Returns:
            Chosen target or None
        """
        if not possible_targets:
            return None
            
        # Simple AI - attack first available target
        # More intelligent AI can prioritize targets differently
        return possible_targets[0]
        
    def apply_status_effect(self, effect_name: str, duration: int = 1) -> bool:
        """
        Apply a status effect to this enemy.
        
        Args:
            effect_name: Name of the status effect
            duration: Duration in rounds
            
        Returns:
            True if effect was applied successfully
        """
        # Remove existing effect of same type
        self.status_effects = [e for e in self.status_effects if e['name'] != effect_name]
        
        # Add new effect
        self.status_effects.append({
            'name': effect_name,
            'duration': duration,
            'applied_round': 0  # Will be set by combat system
        })
        
        return True
        
    def remove_status_effect(self, effect_name: str) -> bool:
        """
        Remove a status effect from this enemy.
        
        Args:
            effect_name: Name of effect to remove
            
        Returns:
            True if effect was found and removed
        """
        original_count = len(self.status_effects)
        self.status_effects = [e for e in self.status_effects if e['name'] != effect_name]
        return len(self.status_effects) < original_count
        
    def has_status_effect(self, effect_name: str) -> bool:
        """Check if enemy has a specific status effect"""
        return any(e['name'] == effect_name for e in self.status_effects)
        
    def process_status_effects(self, current_round: int) -> List[str]:
        """
        Process status effects and remove expired ones.
        
        Args:
            current_round: Current combat round
            
        Returns:
            List of effect messages
        """
        messages = []
        active_effects = []
        
        for effect in self.status_effects:
            effect['duration'] -= 1
            
            if effect['duration'] > 0:
                active_effects.append(effect)
                # Apply effect
                effect_msg = self._apply_status_effect(effect, current_round)
                if effect_msg:
                    messages.append(effect_msg)
            else:
                messages.append(f"The {effect['name']} effect on {self.name} wears off.")
                
        self.status_effects = active_effects
        return messages
        
    def get_display_name(self) -> str:
        """Get display name with any status indicators"""
        name = self.name
        
        # Add status indicators
        if self.has_status_effect('poisoned'):
            name += " (poisoned)"
        if self.has_status_effect('stunned'):
            name += " (stunned)"
        if self.is_fleeing:
            name += " (fleeing)"
            
        return name
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize enemy for saving/loading"""
        return {
            'name': self.name,
            'enemy_type': self.enemy_type,
            'level': self.level,
            'max_hp': self.max_hp,
            'current_hp': self.current_hp,
            'armor_class': self.armor_class,
            'attack_bonus': self.attack_bonus,
            'damage_dice': self.damage_dice,
            'attack_speed': self.attack_speed,
            'experience_value': self.experience_value,
            'difficulty_rating': self.difficulty_rating,
            'loot_table': self.loot_table.copy(),
            'gold_min': self.gold_min,
            'gold_max': self.gold_max,
            'status_effects': self.status_effects.copy(),
            'is_hostile': self.is_hostile,
            'is_fleeing': self.is_fleeing,
            'ai_flags': {
                'aggressive': self.ai_aggressive,
                'intelligent': self.ai_intelligent,
                'pack_hunter': self.ai_pack_hunter
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEnemy':
        """Deserialize enemy from save data (implement in subclasses)"""
        raise NotImplementedError("from_dict must be implemented in enemy subclasses")
        
    def _apply_damage_modifiers(self, damage: int) -> int:
        """
        Apply damage modifiers (resistances, vulnerabilities, etc.)
        Override in subclasses for special damage handling.
        
        Args:
            damage: Base damage amount
            
        Returns:
            Modified damage amount
        """
        return damage
        
    def _roll_loot_chance(self, chance: int) -> bool:
        """
        Roll for loot drop chance.
        
        Args:
            chance: Percentage chance (0-100)
            
        Returns:
            True if loot should drop
        """
        return random.randint(1, 100) <= chance
        
    def _apply_status_effect(self, effect: Dict[str, Any], current_round: int) -> Optional[str]:
        """
        Apply the ongoing effect of a status effect.
        
        Args:
            effect: Status effect data
            current_round: Current combat round
            
        Returns:
            Effect message or None
        """
        effect_name = effect['name']
        
        if effect_name == 'poisoned':
            # Take 1 poison damage per round
            damage = self.take_damage(1)
            if damage > 0:
                return f"{self.name} takes {damage} poison damage!"
        elif effect_name == 'regenerating':
            # Heal 2 HP per round
            healed = self.heal(2)
            if healed > 0:
                return f"{self.name} regenerates {healed} health!"
                
        return None
        
    def __str__(self) -> str:
        """String representation of enemy"""
        hp_status = f"{self.current_hp}/{self.max_hp}"
        status = "alive" if self.is_alive() else "dead"
        return f"{self.name} ({self.enemy_type}, Level {self.level}, HP: {hp_status}, {status})"
        
    def __repr__(self) -> str:
        """Debug representation of enemy"""
        return f"<{self.__class__.__name__}: {self.name}, Level {self.level}, HP: {self.current_hp}/{self.max_hp}>"


# Tutorial-specific enemy implementations
class TutorialEnemy(BaseEnemy):
    """Base class for tutorial enemies with simplified mechanics"""
    
    def __init__(self, name: str, enemy_type: str = "tutorial"):
        super().__init__(name, enemy_type)
        self.ai_intelligent = False  # Simple AI for tutorial
        
    def get_special_abilities(self) -> List[str]:
        """Tutorial enemies have no special abilities"""
        return []
        
    def choose_combat_action(self, target, allies: List['BaseEnemy'] = None) -> str:
        """Simple AI - always attack"""
        return 'attack'


# Test function for enemy system
def _test_enemy_system():
    """Test enemy system functionality."""
    class TestEnemy(TutorialEnemy):
        def __init__(self):
            super().__init__("Test Enemy", "test")
            self.max_hp = 20
            self.current_hp = 20
            self.armor_class = 12
            self.attack_bonus = 3
            self.damage_dice = "1d6+1"
            self.attack_speed = 2.5
            self.experience_value = 25
            
        def get_attack_speed(self):
            return self.attack_speed
    
    # Create test enemy
    enemy = TestEnemy()
    
    # Test basic properties
    assert enemy.is_alive()
    assert enemy.current_hp == 20
    assert enemy.get_hp_percentage() == 1.0
    
    # Test damage
    damage_taken = enemy.take_damage(5)
    assert damage_taken == 5
    assert enemy.current_hp == 15
    assert enemy.get_hp_percentage() == 0.75
    
    # Test healing
    healed = enemy.heal(3)
    assert healed == 3
    assert enemy.current_hp == 18
    
    # Test death
    enemy.take_damage(25)
    assert not enemy.is_alive()
    assert enemy.current_hp == 0
    
    # Test status effects
    enemy2 = TestEnemy()
    assert enemy2.apply_status_effect("poisoned", 3)
    assert enemy2.has_status_effect("poisoned")
    assert not enemy2.has_status_effect("stunned")
    
    print("Enemy system tests passed!")


if __name__ == "__main__":
    _test_enemy_system()