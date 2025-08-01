"""
Combat System for Rogue City
Timer-based combat with class-specific speeds, auto-combat, and multi-enemy support.
"""

import time
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

from .timer_system import TimerSystem
from .dice_system import DiceSystem


class CombatState(Enum):
    """Combat state enumeration."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass
class CombatAction:
    """Represents a combat action."""
    actor_id: str
    action_type: str  # 'attack', 'defend', 'flee', etc.
    target_id: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None


class CombatSystem:
    """
    Manages timer-based combat encounters with class-specific attack speeds,
    auto-combat functionality, and multi-enemy support.
    """
    
    def __init__(self, timer_system: TimerSystem, dice_system: DiceSystem, ui_manager):
        """
        Initialize the combat system.
        
        Args:
            timer_system: Game timer system for action scheduling
            dice_system: Dice system for combat calculations
            ui_manager: UI manager for displaying combat messages
        """
        self.timer_system = timer_system
        self.dice_system = dice_system
        self.ui_manager = ui_manager
        
        # Combat state
        self.state = CombatState.INACTIVE
        self.current_character = None
        self.enemies: Dict[str, Any] = {}  # enemy_id -> enemy object
        self.enemy_counter = 0
        
        # Auto-combat settings
        self.auto_combat_enabled = False
        self.last_combat_action = None
        
        # Combat tracking
        self.combat_round = 0
        self.experience_gained = 0
        self.loot_gained = []
        
    def start_combat(self, character, enemies: List[Any]) -> bool:
        """
        Start a combat encounter.
        
        Args:
            character: Player character
            enemies: List of enemy objects
            
        Returns:
            True if combat started successfully
        """
        if self.state != CombatState.INACTIVE:
            return False
            
        self.current_character = character
        self.enemies.clear()
        self.enemy_counter = 0
        
        # Add enemies with unique IDs
        for enemy in enemies:
            enemy_id = f"enemy_{self.enemy_counter}"
            self.enemies[enemy_id] = enemy
            enemy.combat_id = enemy_id  # Store ID on enemy for reference
            self.enemy_counter += 1
            
        self.state = CombatState.ACTIVE
        self.combat_round = 1
        self.experience_gained = 0
        self.loot_gained.clear()
        
        # Display combat start message
        if len(enemies) == 1:
            self.ui_manager.log_combat(f"A {enemies[0].name} appears!")
        else:
            enemy_names = [enemy.name for enemy in enemies]
            self.ui_manager.log_combat(f"Enemies appear: {', '.join(enemy_names)}!")
            
        # Schedule initial enemy actions
        self._schedule_enemy_actions()
        
        return True
        
    def end_combat(self, victory: bool = True) -> Dict[str, Any]:
        """
        End the current combat encounter.
        
        Args:
            victory: True if player won, False if defeated
            
        Returns:
            Combat results dictionary
        """
        if self.state == CombatState.INACTIVE:
            return {}
            
        # Cancel all pending combat actions
        self.timer_system.cancel_actor_actions(self.current_character.name)
        for enemy_id in self.enemies:
            self.timer_system.cancel_actor_actions(enemy_id)
            
        # Calculate results
        results = {
            'victory': victory,
            'rounds': self.combat_round,
            'experience_gained': self.experience_gained,
            'loot_gained': self.loot_gained.copy(),
            'enemies_defeated': len([e for e in self.enemies.values() if not e.is_alive()])
        }
        
        # Award experience if victorious
        if victory and self.experience_gained > 0:
            self.current_character.gain_experience(self.experience_gained)
            self.ui_manager.log_success(f"You gain {self.experience_gained} experience points!")
            
        # Display loot if any
        if self.loot_gained:
            loot_names = [item['name'] for item in self.loot_gained]
            self.ui_manager.log_success(f"You find: {', '.join(loot_names)}")
            
        # Reset combat state
        self.state = CombatState.INACTIVE
        self.current_character = None
        self.enemies.clear()
        self.auto_combat_enabled = False
        self.last_combat_action = None
        
        return results
        
    def is_active(self) -> bool:
        """Check if combat is currently active."""
        return self.state != CombatState.INACTIVE
        
    def toggle_auto_combat(self) -> bool:
        """
        Toggle auto-combat mode.
        
        Returns:
            New auto-combat state
        """
        if not self.is_active():
            return False
            
        self.auto_combat_enabled = not self.auto_combat_enabled
        
        if self.auto_combat_enabled:
            self.ui_manager.log_system("Auto-combat enabled - attacking automatically")
            # If we have a last action and character is ready, schedule it
            if (self.last_combat_action and 
                self.timer_system.is_actor_ready(self.current_character.name)):
                self._execute_auto_combat()
        else:
            self.ui_manager.log_system("Auto-combat disabled")
            # Cancel any pending auto-combat actions
            self.timer_system.cancel_actor_actions(self.current_character.name)
            
        return self.auto_combat_enabled
        
    def attack_enemy(self, target_name: Optional[str] = None) -> bool:
        """
        Attack an enemy.
        
        Args:
            target_name: Name of enemy to attack, or None for first available
            
        Returns:
            True if attack was queued successfully
        """
        if not self.is_active() or not self.current_character.is_alive():
            return False
            
        # Find target enemy
        target_enemy = None
        target_id = None
        
        if target_name:
            # Look for enemy by name
            for enemy_id, enemy in self.enemies.items():
                if enemy.is_alive() and enemy.name.lower() == target_name.lower():
                    target_enemy = enemy
                    target_id = enemy_id
                    break
        else:
            # Attack first living enemy
            for enemy_id, enemy in self.enemies.items():
                if enemy.is_alive():
                    target_enemy = enemy
                    target_id = enemy_id
                    break
                    
        if not target_enemy:
            if target_name:
                self.ui_manager.log_error(f"There is no {target_name} to attack.")
            else:
                self.ui_manager.log_error("There are no enemies to attack.")
            return False
            
        # Check if character can act
        if not self.timer_system.is_actor_ready(self.current_character.name):
            delay = self.timer_system.get_actor_action_delay(self.current_character.name)
            if delay is not None:
                self.ui_manager.log_error(f"You must wait {delay:.1f} seconds before attacking again.")
            else:
                self.ui_manager.log_error("You cannot attack yet.")
            return False
            
        # Create attack action
        action = CombatAction(
            actor_id=self.current_character.name,
            action_type="attack",
            target_id=target_id,
            action_data={"target_enemy": target_enemy}
        )
        
        # Schedule the attack
        attack_speed = self.current_character.get_attack_speed()
        self.timer_system.schedule_action(
            actor_id=self.current_character.name,
            action_type="attack",
            delay=0.1,  # Small delay for immediate execution
            action_data={"action": action},
            callback=self._execute_player_action
        )
        
        # Store as last action for auto-combat
        self.last_combat_action = action
        
        # Schedule next auto-attack if enabled
        if self.auto_combat_enabled:
            self.timer_system.schedule_action(
                actor_id=self.current_character.name,
                action_type="auto_attack",
                delay=attack_speed,
                action_data={"action": action},
                callback=self._execute_auto_combat_callback
            )
            
        return True
        
    def flee_combat(self) -> bool:
        """
        Attempt to flee from combat.
        
        Returns:
            True if flee attempt was successful
        """
        if not self.is_active():
            return False
            
        # For tutorial, fleeing always fails
        self.ui_manager.log_error("You cannot flee from this battle!")
        return False
        
    def get_combat_status(self) -> Dict[str, Any]:
        """
        Get current combat status.
        
        Returns:
            Combat status information
        """
        if not self.is_active():
            return {"active": False}
            
        living_enemies = [e for e in self.enemies.values() if e.is_alive()]
        
        return {
            "active": True,
            "state": self.state.value,
            "round": self.combat_round,
            "auto_combat": self.auto_combat_enabled,
            "player_hp": f"{self.current_character.current_hp}/{self.current_character.max_hp}",
            "enemies": [
                {
                    "name": enemy.name,
                    "hp": f"{enemy.current_hp}/{enemy.max_hp}",
                    "alive": enemy.is_alive()
                }
                for enemy in self.enemies.values()
            ],
            "living_enemies": len(living_enemies)
        }
        
    def _schedule_enemy_actions(self) -> None:
        """Schedule actions for all living enemies."""
        for enemy_id, enemy in self.enemies.items():
            if enemy.is_alive():
                # Schedule enemy attack with their attack speed
                attack_delay = enemy.get_attack_speed()
                self.timer_system.schedule_action(
                    actor_id=enemy_id,
                    action_type="attack",
                    delay=attack_delay,
                    action_data={"enemy": enemy},
                    callback=self._execute_enemy_action
                )
                
    def _execute_player_action(self, timed_action) -> None:
        """Execute a player combat action."""
        action_data = timed_action.action_data
        action = action_data.get("action")
        
        if not action or not self.is_active():
            return
            
        if action.action_type == "attack":
            self._execute_player_attack(action)
            
    def _execute_player_attack(self, action: CombatAction) -> None:
        """Execute a player attack action."""
        target_enemy = action.action_data.get("target_enemy")
        if not target_enemy or not target_enemy.is_alive():
            return
            
        # Calculate attack roll with equipment bonuses
        attack_bonus = self.current_character.base_attack_bonus
        crit_range = self.current_character.get_critical_range()
        
        # Add equipment attack bonus
        if (self.current_character.equipment_system and 
            self.current_character.equipment_system.get_equipped_weapon()):
            weapon = self.current_character.equipment_system.get_equipped_weapon()
            attack_bonus += weapon.attack_bonus
            crit_range = weapon.crit_range
        
        attack_roll, is_critical = self.dice_system.attack_roll(
            f"1d20+{attack_bonus}", 
            critical_threshold=crit_range
        )
        
        # Check if attack hits
        if attack_roll >= target_enemy.armor_class:
            # Attack hits - calculate damage using equipped weapon
            if (self.current_character.equipment_system and 
                self.current_character.equipment_system.get_equipped_weapon()):
                # Use equipped weapon damage
                weapon = self.current_character.equipment_system.get_equipped_weapon()
                base_damage = weapon.damage_dice
                weapon_bonus = weapon.damage_bonus
            else:
                # Use unarmed damage
                base_damage = "1d2"  # Unarmed damage
                weapon_bonus = 0
            
            # Add strength modifier (or dex for finesse weapons like rogues)
            stat_modifier = self.current_character.get_stat_modifier('strength')
            if hasattr(self.current_character, 'character_class') and self.current_character.character_class == 'rogue':
                # Rogues use DEX for damage with finesse weapons
                stat_modifier = self.current_character.get_stat_modifier('dexterity')
            
            total_bonus = stat_modifier + weapon_bonus
            
            if total_bonus > 0:
                damage_notation = f"{base_damage}+{total_bonus}"
            elif total_bonus < 0:
                damage_notation = f"{base_damage}{total_bonus}"
            else:
                damage_notation = base_damage
                
            damage = self.dice_system.roll(damage_notation)
            
            # Apply critical hit multiplier
            if is_critical:
                damage *= 2
                self.ui_manager.log_combat(f"Critical hit! You attack the {target_enemy.name} for {damage} damage!")
            else:
                self.ui_manager.log_combat(f"You attack the {target_enemy.name} for {damage} damage!")
                
            # Apply damage
            actual_damage = target_enemy.take_damage(damage)
            
            # Check if enemy dies
            if not target_enemy.is_alive():
                self.ui_manager.log_combat(f"The {target_enemy.name} dies!")
                self.experience_gained += target_enemy.experience_value
                
                # Add loot if any
                loot = target_enemy.get_loot()
                if loot:
                    self.loot_gained.extend(loot)
                    
                # Check for combat end
                if not any(enemy.is_alive() for enemy in self.enemies.values()):
                    self.end_combat(victory=True)
                    return
        else:
            self.ui_manager.log_combat(f"You miss the {target_enemy.name}!")
            
    def _execute_enemy_action(self, timed_action) -> None:
        """Execute an enemy combat action."""
        enemy = timed_action.action_data.get("enemy")
        if not enemy or not enemy.is_alive() or not self.is_active():
            return
            
        # Enemy attacks player
        attack_roll, is_critical = self.dice_system.attack_roll(
            f"1d20+{enemy.attack_bonus}",
            critical_threshold=20
        )
        
        if attack_roll >= self.current_character.armor_class:
            # Attack hits
            damage = self.dice_system.roll(enemy.damage_dice)
            
            if is_critical:
                damage *= 2
                self.ui_manager.log_combat(f"Critical hit! The {enemy.name} attacks you for {damage} damage!")
            else:
                self.ui_manager.log_combat(f"The {enemy.name} attacks you for {damage} damage!")
                
            actual_damage = self.current_character.take_damage(damage)
            
            # Check if player dies
            if not self.current_character.is_alive():
                self.ui_manager.log_combat("You have been defeated!")
                self.end_combat(victory=False)
                return
        else:
            self.ui_manager.log_combat(f"The {enemy.name} misses you!")
            
        # Schedule next enemy action if combat is still active
        if self.is_active() and enemy.is_alive():
            attack_delay = enemy.get_attack_speed()
            self.timer_system.schedule_action(
                actor_id=enemy.combat_id,
                action_type="attack",
                delay=attack_delay,
                action_data={"enemy": enemy},
                callback=self._execute_enemy_action
            )
            
    def _execute_auto_combat(self) -> None:
        """Execute auto-combat action."""
        if (not self.auto_combat_enabled or 
            not self.last_combat_action or 
            not self.is_active()):
            return
            
        # Find a valid target (in case original target died)
        living_enemies = [(eid, e) for eid, e in self.enemies.items() if e.is_alive()]
        if not living_enemies:
            return
            
        # Use first living enemy as target
        target_id, target_enemy = living_enemies[0]
        
        # Update the action with new target
        action = CombatAction(
            actor_id=self.current_character.name,
            action_type="attack",
            target_id=target_id,
            action_data={"target_enemy": target_enemy}
        )
        
        self._execute_player_attack(action)
        
    def _execute_auto_combat_callback(self, timed_action) -> None:
        """Callback for auto-combat timer."""
        if self.auto_combat_enabled and self.is_active():
            self._execute_auto_combat()
            
            # Schedule next auto-attack
            if self.auto_combat_enabled and self.is_active():
                attack_speed = self.current_character.get_attack_speed()
                action = timed_action.action_data.get("action")
                self.timer_system.schedule_action(
                    actor_id=self.current_character.name,
                    action_type="auto_attack",
                    delay=attack_speed,
                    action_data={"action": action},
                    callback=self._execute_auto_combat_callback
                )
                
    def process_combat_update(self) -> None:
        """Process combat system updates (called by game engine)."""
        if not self.is_active():
            return
            
        # Check for combat end conditions
        if not self.current_character.is_alive():
            self.end_combat(victory=False)
        elif not any(enemy.is_alive() for enemy in self.enemies.values()):
            self.end_combat(victory=True)


# Test function for combat system
def _test_combat_system():
    """Test combat system functionality."""
    from .timer_system import TimerSystem
    from .dice_system import DiceSystem
    
    class MockUIManager:
        def log_combat(self, msg): print(f"COMBAT: {msg}")
        def log_system(self, msg): print(f"SYSTEM: {msg}")
        def log_success(self, msg): print(f"SUCCESS: {msg}")
        def log_error(self, msg): print(f"ERROR: {msg}")
    
    class MockCharacter:
        def __init__(self):
            self.name = "TestHero"
            self.current_hp = 20
            self.max_hp = 20
            self.armor_class = 15
            self.base_attack_bonus = 3
            
        def get_attack_speed(self): return 2.0
        def get_critical_range(self): return 20
        def get_stat_modifier(self, stat): return 1
        def is_alive(self): return self.current_hp > 0
        def take_damage(self, amount): 
            self.current_hp = max(0, self.current_hp - amount)
            return amount
        def gain_experience(self, amount): pass
    
    class MockEnemy:
        def __init__(self):
            self.name = "TestGoblin"
            self.current_hp = 8
            self.max_hp = 8
            self.armor_class = 12
            self.attack_bonus = 2
            self.damage_dice = "1d4+1"
            self.experience_value = 50
            self.combat_id = None
            
        def get_attack_speed(self): return 3.0
        def is_alive(self): return self.current_hp > 0
        def take_damage(self, amount):
            self.current_hp = max(0, self.current_hp - amount)
            return amount
        def get_loot(self): return []
    
    # Create test instances
    timer_system = TimerSystem()
    dice_system = DiceSystem(show_rolls=False)
    ui_manager = MockUIManager()
    combat_system = CombatSystem(timer_system, dice_system, ui_manager)
    
    character = MockCharacter()
    enemy = MockEnemy()
    
    # Test combat start
    assert combat_system.start_combat(character, [enemy])
    assert combat_system.is_active()
    
    # Test attack
    assert combat_system.attack_enemy("testgoblin")
    
    print("Combat system tests passed!")


if __name__ == "__main__":
    _test_combat_system()