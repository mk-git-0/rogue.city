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
    
    def __init__(self, timer_system: TimerSystem, dice_system: DiceSystem, ui_manager, game_engine=None):
        """
        Initialize the combat system.
        
        Args:
            timer_system: Game timer system for action scheduling
            dice_system: Dice system for combat calculations
            ui_manager: UI manager for displaying combat messages
            game_engine: Reference to game engine for state management
        """
        self.timer_system = timer_system
        self.dice_system = dice_system
        self.ui_manager = ui_manager
        self.game_engine = game_engine
        
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
            
        # Turn-based combat - no initial scheduling needed
        
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
        
        # Notify game engine to reset game state
        if self.game_engine:
            self.game_engine.end_combat(victory)
        
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
        else:
            self.ui_manager.log_system("Auto-combat disabled")
            
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
            # Look for enemy by name (allow partial matches)
            for enemy_id, enemy in self.enemies.items():
                if enemy.is_alive():
                    enemy_name = enemy.name.lower()
                    target_lower = target_name.lower()
                    # Check for exact match first, then partial matches
                    if enemy_name == target_lower or target_lower in enemy_name or enemy_name in target_lower:
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
            
        # Turn-based combat - no delays needed
            
        # Turn-based combat: Execute player turn immediately
        self._execute_player_turn(target_name)
        
        # Then execute enemy turn if combat is still active
        if self.is_active():
            self._execute_enemy_turn()
            
        # Auto-combat will be handled by the command parser asking for another attack
            
        return True
        
    def _execute_player_turn(self, target_name: str = None) -> None:
        """Execute the player's turn with multiple attacks if applicable."""
        if not self.is_active() or not self.current_character.is_alive():
            return
            
        # Get number of attacks per turn (to be implemented)
        num_attacks = self._get_player_attacks_per_turn()
        
        for attack_num in range(num_attacks):
            if not self.is_active():  # Combat might end mid-turn
                break
                
            # Find target for this attack
            target_enemy = None
            target_id = None
            
            if target_name:
                # Look for enemy by name (allow partial matches)
                for enemy_id, enemy in self.enemies.items():
                    if enemy.is_alive():
                        enemy_name = enemy.name.lower()
                        target_lower = target_name.lower()
                        if enemy_name == target_lower or target_lower in enemy_name or enemy_name in target_lower:
                            target_enemy = enemy
                            target_id = enemy_id
                            break
            
            if not target_enemy:
                # Attack first living enemy
                for enemy_id, enemy in self.enemies.items():
                    if enemy.is_alive():
                        target_enemy = enemy
                        target_id = enemy_id
                        break
                        
            if not target_enemy:
                break  # No enemies left
                
            # Show attack number if multiple attacks
            if num_attacks > 1:
                self.ui_manager.log_info(f"Attack {attack_num + 1} of {num_attacks}:")
                
            # Execute the attack
            self._execute_single_player_attack(target_enemy)
            
    def _execute_enemy_turn(self) -> None:
        """Execute all enemies' turns."""
        if not self.is_active():
            return
            
        # Create a list copy to avoid "dictionary changed size during iteration" error
        enemies_list = list(self.enemies.items())
        for enemy_id, enemy in enemies_list:
            if enemy.is_alive() and self.current_character.is_alive() and self.is_active():
                self._execute_single_enemy_attack(enemy)
                
    def _get_player_attacks_per_turn(self) -> int:
        """Get number of attacks player gets per turn based on weapon and class."""
        if not (hasattr(self.current_character, 'equipment_system') and 
                self.current_character.equipment_system):
            return 1
            
        equipment = self.current_character.equipment_system
        
        # For dual-wielding classes (rogues), sum attacks from both weapons
        if (hasattr(self.current_character, 'character_class') and 
            self.current_character.character_class == 'rogue' and
            hasattr(equipment, 'get_all_weapons')):
            
            weapons = equipment.get_all_weapons()
            total_attacks = 0
            for weapon in weapons:
                if hasattr(weapon, 'attacks_per_turn'):
                    total_attacks += weapon.attacks_per_turn
                else:
                    total_attacks += 1  # Default if no attacks_per_turn
            return max(1, total_attacks)  # At least 1 attack
        
        # For non-dual-wielding classes, use main weapon only
        weapon = equipment.get_equipped_weapon()
        if weapon and hasattr(weapon, 'attacks_per_turn'):
            return weapon.attacks_per_turn
        
        # Default to 1 attack for unarmed or weapons without this property
        return 1
        
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
        
    def cast_spell_in_combat(self, spell_name: str, target_name: str = None) -> bool:
        """
        Cast a spell during combat.
        
        Args:
            spell_name: Name of spell to cast
            target_name: Name of target (for targeted spells)
            
        Returns:
            True if spell was cast successfully
        """
        if not self.is_active() or not self.current_character.is_alive():
            return False
            
        # Check if character can cast spells
        if not self.current_character.is_spellcaster():
            self.ui_manager.log_error("You don't know how to cast spells.")
            return False
            
        # Initialize spell system if needed
        if not hasattr(self, 'spell_system'):
            from core.spell_system import SpellSystem
            self.spell_system = SpellSystem(self.dice_system, self.ui_manager)
            
        # Resolve target for combat
        target = None
        if target_name:
            if target_name.lower() in ['self', 'me']:
                target = self.current_character
            else:
                # Find enemy target
                for enemy_id, enemy in self.enemies.items():
                    if enemy.is_alive():
                        enemy_name = enemy.name.lower()
                        target_lower = target_name.lower()
                        if enemy_name == target_lower or target_lower in enemy_name:
                            target = enemy
                            break
                            
                if not target:
                    self.ui_manager.log_error(f"Enemy '{target_name}' not found.")
                    return False
                    
        # Cast the spell
        success, message, effects_data = self.spell_system.cast_spell(
            self.current_character, spell_name, target, self
        )
        
        if success:
            # Apply spell effects
            self._apply_spell_effects(effects_data)
            
        return success
        
    def _apply_spell_effects(self, effects_data: Dict[str, Any]):
        """Apply spell effects during combat"""
        effect_type = effects_data.get('type')
        
        if effect_type == 'damage':
            # Apply damage to target
            damage = effects_data.get('damage', 0)
            target = effects_data.get('target')
            damage_type = effects_data.get('damage_type', 'magical')
            
            if hasattr(target, 'current_hp'):  # Enemy target
                actual_damage = target.take_damage(damage)
                self.ui_manager.log_success(f"{target.name} takes {actual_damage} {damage_type} damage!")
                
                # Check if enemy died
                if not target.is_alive():
                    self.ui_manager.log_success(f"{target.name} has been slain!")
                    self._check_combat_end()
                    
        elif effect_type == 'healing':
            # Apply healing to target
            healing = effects_data.get('healing')
            target = effects_data.get('target')
            
            if healing == 'full':
                # Full heal
                if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
                    old_hp = target.current_hp
                    target.current_hp = target.max_hp
                    actual_healing = target.current_hp - old_hp
                    self.ui_manager.log_success(f"{target.name if hasattr(target, 'name') else 'You'} fully healed for {actual_healing} HP!")
            else:
                # Normal healing
                if hasattr(target, 'heal'):
                    actual_healing = target.heal(healing)
                    target_name = target.name if hasattr(target, 'name') else 'You'
                    self.ui_manager.log_success(f"{target_name} healed for {actual_healing} HP!")
                    
        elif effect_type == 'buff':
            # Apply temporary buff
            effect_name = effects_data.get('effect')
            duration = effects_data.get('duration', 1)
            target = effects_data.get('target')
            
            self.ui_manager.log_info(f"Spell effect '{effect_name}' applied for {duration} rounds.")
            # TODO: Implement buff tracking system
            
        elif effect_type == 'turn_undead':
            # Turn undead effect
            turning_dc = effects_data.get('turning_dc', 10)
            undead_affected = 0
            
            for enemy_id, enemy in self.enemies.items():
                if enemy.is_alive() and hasattr(enemy, 'creature_type') and enemy.creature_type == 'undead':
                    # Roll save vs turning
                    save_roll = self.dice_system.roll("1d20")
                    if save_roll < turning_dc:
                        enemy.current_hp = 0  # Destroy weak undead
                        self.ui_manager.log_success(f"{enemy.name} is destroyed by divine power!")
                        undead_affected += 1
                    else:
                        self.ui_manager.log_info(f"{enemy.name} resists the turning attempt.")
                        
            if undead_affected > 0:
                self._check_combat_end()
            else:
                self.ui_manager.log_info("No undead creatures were affected.")
        
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
        
                
    def _execute_player_action(self, timed_action) -> None:
        """Execute a player combat action."""
        action_data = timed_action.action_data
        action = action_data.get("action")
        
        if not action or not self.is_active():
            return
            
        if action.action_type == "attack":
            self._execute_player_attack(action)
            
    def _execute_single_player_attack(self, target_enemy) -> None:
        """Execute a single player attack."""
        if not target_enemy or not target_enemy.is_alive():
            return
            
        # Calculate attack roll with equipment bonuses
        attack_bonus = self.current_character.base_attack_bonus
        crit_range = self.current_character.get_critical_range()
        
        # Add equipment attack bonus
        if (hasattr(self.current_character, 'equipment_system') and 
            self.current_character.equipment_system and 
            self.current_character.equipment_system.get_equipped_weapon()):
            weapon = self.current_character.equipment_system.get_equipped_weapon()
            if hasattr(weapon, 'attack_bonus'):
                attack_bonus += weapon.attack_bonus
            if hasattr(weapon, 'crit_range'):
                crit_range = weapon.crit_range
        
        # Display attack attempt  
        enemy_colored = self.ui_manager.colorize_enemy(target_enemy.name)
        self.ui_manager.log_info(f"You swing at the {enemy_colored}!")
        
        attack_roll, is_critical = self.dice_system.attack_roll(
            f"1d20+{attack_bonus}", 
            critical_threshold=crit_range
        )
        
        # Check if attack hits
        if attack_roll >= target_enemy.armor_class:
            # Attack hits - calculate damage using equipped weapon
            if (hasattr(self.current_character, 'equipment_system') and 
                self.current_character.equipment_system and 
                self.current_character.equipment_system.get_equipped_weapon()):
                # Use equipped weapon damage
                weapon = self.current_character.equipment_system.get_equipped_weapon()
                if hasattr(weapon, 'damage_dice'):
                    base_damage = weapon.damage_dice
                else:
                    base_damage = "1d4"
                if hasattr(weapon, 'damage_bonus'):
                    weapon_bonus = weapon.damage_bonus
                else:
                    weapon_bonus = 0
            else:
                # Use unarmed damage 1d4 with -2 penalty (handled later)
                base_damage = "1d4"  # Unarmed damage
                weapon_bonus = -2
            
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
                
            damage = self.dice_system.roll_with_context(damage_notation, "You", "damage")
            
            # Ensure minimum damage of 1
            damage = max(1, damage)
            
            # Apply critical hit multiplier
            if is_critical:
                damage *= 2
                self.ui_manager.log_critical(f"*** CRITICAL HIT! *** You strike the {enemy_colored} for {damage} damage!")
            else:
                self.ui_manager.log_success(f"You hit the {enemy_colored} for {damage} damage!")
                
            # Apply damage
            actual_damage = target_enemy.take_damage(damage)
            
            # Show enemy health after damage
            enemy_hp_percent = int((target_enemy.current_hp / target_enemy.max_hp) * 100) if target_enemy.max_hp > 0 else 0
            if target_enemy.is_alive():
                self.ui_manager.log_info(f"The {enemy_colored} has {target_enemy.current_hp}/{target_enemy.max_hp} HP ({enemy_hp_percent}%)")
            
            # Check if enemy dies
            if not target_enemy.is_alive():
                self.ui_manager.log_success(f"*** The {enemy_colored} dies! ***")
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
            self.ui_manager.log_info(f"You miss the {enemy_colored}!")
            
    def _execute_single_enemy_attack(self, enemy) -> None:
        """Execute a single enemy attack."""
        if not enemy or not enemy.is_alive() or not self.is_active():
            return
            
        # Enemy attacks player
        # Display enemy attack attempt
        enemy_colored = self.ui_manager.colorize_enemy(enemy.name)
        self.ui_manager.log_info(f"The {enemy_colored} attacks you!")
        
        attack_roll, is_critical = self.dice_system.attack_roll(
            f"1d20+{enemy.attack_bonus}",
            critical_threshold=20
        )
        
        if attack_roll >= self.current_character.armor_class:
            # Attack hits
            damage = self.dice_system.roll_with_context(enemy.damage_dice, f"The {enemy.name}", "damage")
            
            if is_critical:
                damage *= 2
                self.ui_manager.log_critical(f"*** CRITICAL HIT! *** The {enemy_colored} strikes you for {damage} damage!")
            else:
                self.ui_manager.log_error(f"The {enemy_colored} hits you for {damage} damage!")
                
            actual_damage = self.current_character.take_damage(damage)
            
            # Show player health after damage  
            player_hp_percent = int((self.current_character.current_hp / self.current_character.max_hp) * 100) if self.current_character.max_hp > 0 else 0
            if self.current_character.is_alive():
                self.ui_manager.log_info(f"You have {self.current_character.current_hp}/{self.current_character.max_hp} HP ({player_hp_percent}%)")
            
            # Check if player dies
            if not self.current_character.is_alive():
                self.ui_manager.log_critical("*** YOU HAVE BEEN DEFEATED! ***")
                self.end_combat(victory=False)
                return
        else:
            self.ui_manager.log_info(f"The {enemy_colored} misses you!")
            
        # Turn-based combat - no scheduling needed
            
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
                
    def toggle_dual_wield(self, character) -> bool:
        """
        Toggle dual-wield mode for applicable classes.
        
        Returns:
            True if dual-wield mode was toggled successfully
        """
        if not hasattr(character, 'character_class'):
            return False
        
        char_class = character.character_class.lower()
        dual_wield_classes = ['ranger', 'rogue', 'ninja', 'bard']
        
        if char_class not in dual_wield_classes:
            self.ui_manager.log_error("You don't know how to fight with two weapons.")
            return False
        
        # Check if character has two weapons
        if not (hasattr(character, 'equipment_system') and character.equipment_system):
            self.ui_manager.log_error("You need weapons equipped to dual-wield.")
            return False
        
        # Toggle dual-wield state
        if not hasattr(character, 'dual_wield_mode'):
            character.dual_wield_mode = False
        
        character.dual_wield_mode = not character.dual_wield_mode
        
        if character.dual_wield_mode:
            self.ui_manager.log_success("You prepare to fight with both hands.")
            self.ui_manager.log_system("[Dual-wield mode activated - extra attacks with penalties]")
        else:
            self.ui_manager.log_success("You return to single-weapon fighting.")
            self.ui_manager.log_system("[Dual-wield mode deactivated]")
        
        return True
    
    def enter_defensive_stance(self, character) -> bool:
        """
        Enter defensive stance for increased AC at cost of attack.
        
        Returns:
            True if defensive stance was entered
        """
        if not hasattr(character, 'character_class'):
            return False
        
        char_class = character.character_class.lower()
        defensive_classes = ['knight', 'warrior', 'paladin', 'barbarian']
        
        if char_class not in defensive_classes:
            self.ui_manager.log_error("You don't know how to fight defensively.")
            return False
        
        # Set defensive stance
        if not hasattr(character, 'defensive_stance'):
            character.defensive_stance = False
        
        character.defensive_stance = not character.defensive_stance
        
        if character.defensive_stance:
            self.ui_manager.log_success("You adopt a defensive fighting stance.")
            self.ui_manager.log_system("[Defensive stance: +2 AC, -2 attack penalties]")
        else:
            self.ui_manager.log_success("You return to normal fighting stance.")
            self.ui_manager.log_system("[Normal combat stance resumed]")
        
        return True
    
    def attempt_block(self, character) -> bool:
        """
        Attempt to actively block with shield.
        
        Returns:
            True if block attempt was set up
        """
        # Check for shield
        if not (hasattr(character, 'equipment_system') and character.equipment_system):
            self.ui_manager.log_error("You need a shield to block.")
            return False
        
        # For now, simplified - would check for actual shield in equipment
        shield = None  # character.equipment_system.get_equipped_shield()
        if not shield:
            self.ui_manager.log_error("You don't have a shield equipped.")
            return False
        
        # Set blocking stance
        if not hasattr(character, 'blocking_stance'):
            character.blocking_stance = False
        
        character.blocking_stance = not character.blocking_stance
        
        if character.blocking_stance:
            self.ui_manager.log_success("You raise your shield to block incoming attacks.")
            self.ui_manager.log_system("[Blocking stance: +2 AC vs attacks, -1 to your attacks]")
        else:
            self.ui_manager.log_success("You lower your shield.")
            self.ui_manager.log_system("[Normal stance resumed]")
        
        return True
    
    def attempt_parry(self, character) -> bool:
        """
        Attempt to parry with weapon.
        
        Returns:
            True if parry stance was set up
        """
        # Check for weapon
        if not (hasattr(character, 'equipment_system') and character.equipment_system):
            self.ui_manager.log_error("You need a weapon to parry.")
            return False
        
        weapon = character.equipment_system.get_equipped_weapon()
        if not weapon:
            self.ui_manager.log_error("You don't have a weapon equipped.")
            return False
        
        # Set parrying stance
        if not hasattr(character, 'parrying_stance'):
            character.parrying_stance = False
        
        character.parrying_stance = not character.parrying_stance
        
        if character.parrying_stance:
            self.ui_manager.log_success("You prepare to parry incoming attacks with your weapon.")
            self.ui_manager.log_system("[Parrying stance: chance to negate attacks, -1 to your attacks]")
        else:
            self.ui_manager.log_success("You return to normal weapon stance.")
            self.ui_manager.log_system("[Normal combat stance resumed]")
        
        return True
    
    def attempt_charge_attack(self, character, target_name: str = None) -> bool:
        """
        Attempt a charging attack for extra damage.
        
        Returns:
            True if charge attack was executed
        """
        if not self.is_active():
            self.ui_manager.log_error("You can only charge in combat.")
            return False
        
        char_class = getattr(character, 'character_class', '').lower()
        charge_classes = ['warrior', 'knight', 'barbarian', 'ranger']
        
        if char_class not in charge_classes:
            self.ui_manager.log_error("You don't know how to execute charging attacks.")
            return False
        
        # Find target
        target_enemy = None
        if target_name:
            for enemy_id, enemy in self.enemies.items():
                if enemy.is_alive() and target_name.lower() in enemy.name.lower():
                    target_enemy = enemy
                    break
        else:
            # Charge first available enemy
            for enemy_id, enemy in self.enemies.items():
                if enemy.is_alive():
                    target_enemy = enemy
                    break
        
        if not target_enemy:
            self.ui_manager.log_error("There is no enemy to charge.")
            return False
        
        self.ui_manager.log_info(f"You charge at the {target_enemy.name}!")
        
        # Execute charge attack (enhanced normal attack)
        # Set a temporary charge flag for damage calculation
        character._charging = True
        self._execute_single_player_attack(target_enemy)
        character._charging = False
        
        return True
    
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
    
    # Process timer to execute the attack
    import time
    time.sleep(0.2)  # Wait for attack to be ready
    ready_actions = timer_system.process_ready_actions()
    print(f"Processed {len(ready_actions)} actions")
    
    print("Combat system tests passed!")


if __name__ == "__main__":
    _test_combat_system()