"""
Dice System for Rogue City
Handles D&D-style dice rolling with support for various dice types and modifiers.
"""

import random
import re
from typing import Tuple, Optional


class DiceSystem:
    """
    Manages dice rolling operations for the game.
    Supports standard D&D dice notation like '1d20+5', '3d6+2', '2d8-1'.
    """
    
    def __init__(self, show_rolls: bool = True):
        """
        Initialize the dice system.
        
        Args:
            show_rolls: Whether to show individual roll results to the player
        """
        self.show_rolls = show_rolls
        self.valid_dice = [3, 4, 6, 8, 10, 12, 20, 100]
        
    def set_visibility(self, show_rolls: bool) -> None:
        """Toggle visibility of dice roll results."""
        self.show_rolls = show_rolls
        
    def roll_single_die(self, sides: int) -> int:
        """
        Roll a single die with the specified number of sides.
        
        Args:
            sides: Number of sides on the die
            
        Returns:
            Random number between 1 and sides (inclusive)
            
        Raises:
            ValueError: If sides is not a valid die type
        """
        if sides not in self.valid_dice:
            raise ValueError(f"Invalid die type: d{sides}. Valid types: {self.valid_dice}")
            
        return random.randint(1, sides)
        
    def parse_dice_notation(self, notation: str) -> Tuple[int, int, int]:
        """
        Parse dice notation like '3d6+2' or '1d20-1'.
        
        Args:
            notation: Dice notation string
            
        Returns:
            Tuple of (number_of_dice, die_sides, modifier)
            
        Raises:
            ValueError: If notation is invalid
        """
        # Remove spaces and convert to lowercase
        notation = notation.replace(' ', '').lower()
        
        # Pattern: optional number, 'd', die sides, optional +/- modifier
        pattern = r'^(\d+)?d(\d+)([+-]\d+)?$'
        match = re.match(pattern, notation)
        
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")
            
        num_dice = int(match.group(1)) if match.group(1) else 1
        die_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        if num_dice < 1 or num_dice > 100:
            raise ValueError(f"Number of dice must be between 1 and 100, got {num_dice}")
            
        if die_sides not in self.valid_dice:
            raise ValueError(f"Invalid die type: d{die_sides}. Valid types: {self.valid_dice}")
            
        return num_dice, die_sides, modifier
        
    def roll(self, notation: str) -> int:
        """
        Roll dice using standard notation.
        
        Args:
            notation: Dice notation like '1d20+5' or '3d6'
            
        Returns:
            Total result of all dice rolls plus modifier
        """
        num_dice, die_sides, modifier = self.parse_dice_notation(notation)
        
        rolls = []
        for _ in range(num_dice):
            roll_result = self.roll_single_die(die_sides)
            rolls.append(roll_result)
            
        total = sum(rolls) + modifier
        
        if self.show_rolls and len(rolls) > 1:
            rolls_str = '+'.join(map(str, rolls))
            modifier_str = f"{modifier:+d}" if modifier != 0 else ""
            print(f"Rolled {notation}: [{rolls_str}]{modifier_str} = {total}")
        elif self.show_rolls:
            modifier_str = f"{modifier:+d}" if modifier != 0 else ""
            print(f"Rolled {notation}: {rolls[0]}{modifier_str} = {total}")
            
        return total
        
    def attack_roll(self, notation: str, critical_threshold: int = 20) -> Tuple[int, bool]:
        """
        Roll for an attack, checking for critical hits.
        
        Args:
            notation: Dice notation for the attack roll
            critical_threshold: Minimum roll for a critical hit (default 20)
            
        Returns:
            Tuple of (total_result, is_critical)
        """
        num_dice, die_sides, modifier = self.parse_dice_notation(notation)
        
        # For attack rolls, we typically only care about the first die for criticals
        if num_dice != 1:
            raise ValueError("Attack rolls should use single dice (e.g., '1d20+5')")
            
        roll_result = self.roll_single_die(die_sides)
        total = roll_result + modifier
        is_critical = roll_result >= critical_threshold
        
        if self.show_rolls:
            crit_indicator = " (CRITICAL!)" if is_critical else ""
            modifier_str = f"{modifier:+d}" if modifier != 0 else ""
            print(f"Attack roll {notation}: {roll_result}{modifier_str} = {total}{crit_indicator}")
            
        return total, is_critical
        
    def advantage_roll(self, notation: str) -> int:
        """
        Roll with advantage (roll twice, take higher).
        
        Args:
            notation: Dice notation for the roll
            
        Returns:
            Higher of the two rolls
        """
        roll1 = self.roll(notation)
        roll2 = self.roll(notation)
        result = max(roll1, roll2)
        
        if self.show_rolls:
            print(f"Advantage roll: {roll1} vs {roll2}, taking {result}")
            
        return result
        
    def disadvantage_roll(self, notation: str) -> int:
        """
        Roll with disadvantage (roll twice, take lower).
        
        Args:
            notation: Dice notation for the roll
            
        Returns:
            Lower of the two rolls
        """
        roll1 = self.roll(notation)
        roll2 = self.roll(notation)
        result = min(roll1, roll2)
        
        if self.show_rolls:
            print(f"Disadvantage roll: {roll1} vs {roll2}, taking {result}")
            
        return result


# Quick test function for validation
def _test_dice_system():
    """Test the dice system functionality."""
    dice = DiceSystem(show_rolls=False)
    
    # Test basic rolling
    result = dice.roll('1d20')
    assert 1 <= result <= 20, f"1d20 roll out of range: {result}"
    
    # Test with modifier
    result = dice.roll('1d6+3')
    assert 4 <= result <= 9, f"1d6+3 roll out of range: {result}"
    
    # Test multiple dice
    result = dice.roll('3d6')
    assert 3 <= result <= 18, f"3d6 roll out of range: {result}"
    
    # Test attack roll
    total, is_crit = dice.attack_roll('1d20+5')
    assert 6 <= total <= 25, f"Attack roll out of range: {total}"
    assert isinstance(is_crit, bool), f"Critical flag should be boolean: {is_crit}"
    
    print("All dice system tests passed!")


if __name__ == "__main__":
    _test_dice_system()