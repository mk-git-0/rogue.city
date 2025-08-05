"""
Currency System for Rogue City
Handles gold, silver, copper conversion and currency operations.
"""

from typing import Dict, Tuple, Union
import random


class Currency:
    """
    Represents currency amounts in gold pieces, silver pieces, and copper pieces.
    Standard MajorMUD conversion: 1 GP = 10 SP = 100 CP
    """
    
    def __init__(self, gold: int = 0, silver: int = 0, copper: int = 0):
        """Initialize currency with gold, silver, and copper pieces"""
        self.gold = max(0, gold)
        self.silver = max(0, silver)
        self.copper = max(0, copper)
        self._normalize()
    
    def _normalize(self):
        """Convert excess copper/silver to higher denominations"""
        # Convert excess copper to silver
        if self.copper >= 10:
            extra_silver = self.copper // 10
            self.silver += extra_silver
            self.copper = self.copper % 10
        
        # Convert excess silver to gold
        if self.silver >= 10:
            extra_gold = self.silver // 10
            self.gold += extra_gold
            self.silver = self.silver % 10
    
    def total_copper(self) -> int:
        """Get total value in copper pieces"""
        return (self.gold * 100) + (self.silver * 10) + self.copper
    
    def total_silver(self) -> int:
        """Get total value in silver pieces"""
        return (self.gold * 10) + self.silver + (self.copper // 10)
    
    def total_gold(self) -> int:
        """Get total value in gold pieces (rounded down)"""
        return self.gold + (self.silver // 10) + (self.copper // 100)
    
    def add(self, other: 'Currency') -> 'Currency':
        """Add another currency amount to this one"""
        self.gold += other.gold
        self.silver += other.silver
        self.copper += other.copper
        self._normalize()
        return self
    
    def subtract(self, other: 'Currency') -> bool:
        """
        Subtract another currency amount from this one.
        Returns True if successful, False if insufficient funds.
        """
        if not self.can_afford(other):
            return False
        
        # Convert to total copper for easier calculation
        total_copper = self.total_copper()
        subtract_copper = other.total_copper()
        
        remaining_copper = total_copper - subtract_copper
        
        # Convert back to gold/silver/copper
        self.gold = remaining_copper // 100
        remaining_copper = remaining_copper % 100
        
        self.silver = remaining_copper // 10
        self.copper = remaining_copper % 10
        
        return True
    
    def can_afford(self, cost: 'Currency') -> bool:
        """Check if we have enough money for the given cost"""
        return self.total_copper() >= cost.total_copper()
    
    def can_afford_gold(self, gold_cost: int) -> bool:
        """Check if we can afford a cost in gold pieces"""
        return self.total_copper() >= (gold_cost * 100)
    
    def subtract_gold(self, gold_amount: int) -> bool:
        """Subtract gold amount, returns True if successful"""
        if not self.can_afford_gold(gold_amount):
            return False
        
        cost = Currency(gold=gold_amount)
        return self.subtract(cost)
    
    def add_gold(self, gold_amount: int):
        """Add gold to currency"""
        self.gold += max(0, gold_amount)
        self._normalize()
    
    def __str__(self) -> str:
        """String representation for display"""
        parts = []
        if self.gold > 0:
            parts.append(f"{self.gold} GP")
        if self.silver > 0:
            parts.append(f"{self.silver} SP")
        if self.copper > 0:
            parts.append(f"{self.copper} CP")
        
        if not parts:
            return "0 GP"
        
        return ", ".join(parts)
    
    def display_total_gold(self) -> str:
        """Display total value in gold with fractions"""
        total_copper = self.total_copper()
        gold_value = total_copper / 100.0
        
        if gold_value == int(gold_value):
            return f"{int(gold_value)} GP"
        else:
            return f"{gold_value:.2f} GP"
    
    def copy(self) -> 'Currency':
        """Create a copy of this currency"""
        return Currency(self.gold, self.silver, self.copper)
    
    @classmethod
    def from_gold(cls, gold_amount: Union[int, float]) -> 'Currency':
        """Create currency from a gold amount (can include fractions)"""
        total_copper = int(gold_amount * 100)
        
        gold = total_copper // 100
        remaining = total_copper % 100
        
        silver = remaining // 10
        copper = remaining % 10
        
        return cls(gold, silver, copper)
    
    @classmethod
    def from_copper(cls, copper_amount: int) -> 'Currency':
        """Create currency from total copper amount"""
        gold = copper_amount // 100
        remaining = copper_amount % 100
        
        silver = remaining // 10
        copper = remaining % 10
        
        return cls(gold, silver, copper)


class CurrencySystem:
    """Manages currency operations and conversions for the game"""
    
    def __init__(self):
        pass
    
    def calculate_starting_gold(self, character_class: str, character_level: int = 1) -> Currency:
        """
        Calculate starting gold for new characters based on class.
        Base: 50 + (2d6 * 10) GP
        """
        base_gold = 50
        
        # Roll 2d6 for extra gold
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        extra_gold = (roll1 + roll2) * 10
        
        # Class modifiers
        class_modifiers = {
            'knight': 20,      # Knights start with more gold (noble background)
            'warrior': 10,     # Warriors have some extra equipment funds
            'paladin': 15,     # Paladins have church support
            'ranger': 5,       # Rangers are self-sufficient
            'thief': -10,      # Thieves start poor
            'rogue': -5,       # Rogues are street smart but poor
            'barbarian': -15,  # Barbarians don't care about money
            'mage': 0,         # Mages are average
            'priest': 10,      # Priests have church support
            'mystic': -5,      # Mystics live simply
            'ninja': -10,      # Ninjas start with minimal possessions
            'necromancer': 0,  # Necromancers are average
            'warlock': 5,      # Warlocks have some resources
            'spellsword': 10,  # Spellswords need equipment funds
            'witchhunter': 15  # Witchhunters have organization backing
        }
        
        class_bonus = class_modifiers.get(character_class.lower(), 0)
        total_gold = base_gold + extra_gold + class_bonus
        
        # Ensure minimum of 25 gold
        total_gold = max(25, total_gold)
        
        return Currency(gold=total_gold)
    
    def generate_loot_gold(self, enemy_level: int, enemy_type: str = "normal") -> Currency:
        """Generate random gold loot from defeated enemies"""
        base_amount = enemy_level * 5  # 5 copper per level minimum
        
        # Enemy type modifiers
        type_modifiers = {
            'normal': 1.0,
            'elite': 2.0,
            'boss': 5.0,
            'humanoid': 1.5,  # Humanoids carry more money
            'undead': 0.5,    # Undead carry less
            'beast': 0.3,     # Beasts carry very little
            'construct': 0.1  # Constructs rarely have money
        }
        
        modifier = type_modifiers.get(enemy_type.lower(), 1.0)
        
        # Random variation (50% to 150% of base)
        variation = random.uniform(0.5, 1.5)
        
        total_copper = int(base_amount * modifier * variation)
        
        # Minimum of 1 copper for any enemy
        total_copper = max(1, total_copper)
        
        return Currency.from_copper(total_copper)
    
    def format_price(self, currency: Currency) -> str:
        """Format currency for price displays"""
        if currency.total_copper() == 0:
            return "Free"
        
        # For large amounts, show in gold
        if currency.total_copper() >= 100:
            return currency.display_total_gold()
        
        # For smaller amounts, show exact denominations
        return str(currency)
    
    def parse_currency_input(self, input_str: str) -> Currency:
        """
        Parse user input like '10g 5s 3c' or '15 gold' into Currency.
        Returns Currency(0,0,0) if parsing fails.
        """
        try:
            input_str = input_str.lower().strip()
            gold = silver = copper = 0
            
            # Handle simple number (assume gold)
            if input_str.isdigit():
                return Currency(gold=int(input_str))
            
            # Parse complex format
            parts = input_str.split()
            i = 0
            while i < len(parts):
                if i + 1 < len(parts):
                    amount = int(parts[i])
                    unit = parts[i + 1]
                    
                    if unit.startswith('g') or 'gold' in unit:
                        gold = amount
                    elif unit.startswith('s') or 'silver' in unit:
                        silver = amount
                    elif unit.startswith('c') or 'copper' in unit:
                        copper = amount
                    
                    i += 2
                else:
                    i += 1
            
            return Currency(gold, silver, copper)
            
        except (ValueError, IndexError):
            return Currency(0, 0, 0)
    
    def convert_item_value_to_currency(self, item_value: int) -> Currency:
        """Convert an item's base value (in gold) to Currency object"""
        return Currency(gold=item_value)