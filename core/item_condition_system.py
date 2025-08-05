"""
Item Condition System for Rogue City
Handles equipment durability, condition tracking, and repair mechanics.
"""

from enum import Enum
from typing import Dict, Tuple, Optional
import random


class ItemCondition(Enum):
    """Item condition levels"""
    PERFECT = "perfect"      # 100% condition
    EXCELLENT = "excellent"  # 90-99% condition
    GOOD = "good"           # 70-89% condition
    FAIR = "fair"           # 50-69% condition
    POOR = "poor"           # 25-49% condition
    DAMAGED = "damaged"     # 10-24% condition
    BROKEN = "broken"       # 0-9% condition


class ItemConditionSystem:
    """Manages item condition, durability, and repair mechanics"""
    
    def __init__(self):
        # Condition thresholds (percentage)
        self.condition_thresholds = {
            ItemCondition.PERFECT: (100, 100),
            ItemCondition.EXCELLENT: (90, 99),
            ItemCondition.GOOD: (70, 89),
            ItemCondition.FAIR: (50, 69),
            ItemCondition.POOR: (25, 49),
            ItemCondition.DAMAGED: (10, 24),
            ItemCondition.BROKEN: (0, 9)
        }
        
        # How much condition affects item value when selling
        self.condition_value_modifiers = {
            ItemCondition.PERFECT: 1.0,
            ItemCondition.EXCELLENT: 0.95,
            ItemCondition.GOOD: 0.80,
            ItemCondition.FAIR: 0.60,
            ItemCondition.POOR: 0.40,
            ItemCondition.DAMAGED: 0.20,
            ItemCondition.BROKEN: 0.10
        }
        
        # How much condition affects item effectiveness
        self.condition_effectiveness_modifiers = {
            ItemCondition.PERFECT: 1.0,
            ItemCondition.EXCELLENT: 0.98,
            ItemCondition.GOOD: 0.90,
            ItemCondition.FAIR: 0.75,
            ItemCondition.POOR: 0.50,
            ItemCondition.DAMAGED: 0.25,
            ItemCondition.BROKEN: 0.0  # Broken items provide no benefit
        }
    
    def get_condition_from_percentage(self, percentage: float) -> ItemCondition:
        """Get condition enum from percentage value"""
        percentage = max(0, min(100, percentage))
        
        for condition, (min_val, max_val) in self.condition_thresholds.items():
            if min_val <= percentage <= max_val:
                return condition
        
        return ItemCondition.BROKEN
    
    def get_condition_percentage_range(self, condition: ItemCondition) -> Tuple[int, int]:
        """Get the percentage range for a condition"""
        return self.condition_thresholds[condition]
    
    def get_condition_display_name(self, condition: ItemCondition) -> str:
        """Get display name for condition"""
        display_names = {
            ItemCondition.PERFECT: "Perfect",
            ItemCondition.EXCELLENT: "Excellent",
            ItemCondition.GOOD: "Good",
            ItemCondition.FAIR: "Fair",
            ItemCondition.POOR: "Poor",
            ItemCondition.DAMAGED: "Damaged",
            ItemCondition.BROKEN: "Broken"
        }
        return display_names[condition]
    
    def get_condition_color_code(self, condition: ItemCondition) -> str:
        """Get color code for condition display"""
        color_codes = {
            ItemCondition.PERFECT: "cyan",
            ItemCondition.EXCELLENT: "green",
            ItemCondition.GOOD: "yellow",
            ItemCondition.FAIR: "white",
            ItemCondition.POOR: "magenta",
            ItemCondition.DAMAGED: "red",
            ItemCondition.BROKEN: "dark_red"
        }
        return color_codes[condition]
    
    def calculate_damage_to_item(self, item_type: str, damage_source: str = "combat") -> float:
        """
        Calculate how much condition damage an item takes.
        Returns percentage points lost (0.0 to 5.0 typically)
        """
        base_damage = {
            "weapon": 0.5,    # Weapons take damage from combat use
            "armor": 1.0,     # Armor takes more damage from being hit
            "accessory": 0.1  # Accessories rarely take damage
        }
        
        source_modifiers = {
            "combat": 1.0,
            "critical_hit": 2.0,  # Extra damage on critical hits
            "fire": 3.0,          # Fire damage is harsh on equipment
            "acid": 4.0,          # Acid is very damaging
            "environmental": 0.2   # Gradual wear from environment
        }
        
        base = base_damage.get(item_type.lower(), 0.5)
        modifier = source_modifiers.get(damage_source.lower(), 1.0)
        
        # Add some randomness (50% to 150% of base)
        variation = random.uniform(0.5, 1.5)
        
        return base * modifier * variation
    
    def apply_condition_damage(self, current_percentage: float, damage_amount: float) -> float:
        """Apply damage to item condition, returns new percentage"""
        new_percentage = current_percentage - damage_amount
        return max(0.0, new_percentage)
    
    def calculate_repair_cost(self, item_base_value: int, current_percentage: float, 
                            target_percentage: float = 100.0) -> int:
        """
        Calculate cost to repair item from current to target condition.
        Cost is proportional to item value and condition improvement needed.
        """
        if current_percentage >= target_percentage:
            return 0
        
        condition_improvement = target_percentage - current_percentage
        
        # Base repair cost: 10% of item value per 10% condition improvement
        repair_cost_per_10_percent = item_base_value * 0.1
        cost_multiplier = condition_improvement / 10.0
        
        total_cost = int(repair_cost_per_10_percent * cost_multiplier)
        
        # Minimum cost of 1 gold for any repair
        return max(1, total_cost)
    
    def can_item_be_used(self, condition: ItemCondition) -> bool:
        """Check if item can be used/equipped in its current condition"""
        return condition != ItemCondition.BROKEN
    
    def get_effectiveness_modifier(self, condition: ItemCondition) -> float:
        """Get how effective the item is based on condition"""
        return self.condition_effectiveness_modifiers[condition]
    
    def get_value_modifier(self, condition: ItemCondition) -> float:
        """Get how much the condition affects item selling value"""
        return self.condition_value_modifiers[condition]
    
    def generate_random_condition(self, item_rarity: str = "common") -> float:
        """Generate random condition for found/looted items"""
        # Better rarity items are found in better condition
        rarity_modifiers = {
            "common": (20, 80),      # 20-80% condition
            "uncommon": (40, 90),    # 40-90% condition
            "rare": (60, 95),        # 60-95% condition
            "epic": (80, 100),       # 80-100% condition
            "legendary": (90, 100)   # 90-100% condition
        }
        
        min_condition, max_condition = rarity_modifiers.get(item_rarity.lower(), (20, 80))
        return random.uniform(min_condition, max_condition)
    
    def format_condition_display(self, percentage: float, show_percentage: bool = True) -> str:
        """Format condition for display in UI"""
        condition = self.get_condition_from_percentage(percentage)
        display_name = self.get_condition_display_name(condition)
        
        if show_percentage:
            return f"{display_name} ({percentage:.0f}%)"
        else:
            return display_name
    
    def get_repair_materials_needed(self, item_type: str, condition_improvement: float) -> Dict[str, int]:
        """
        Get materials needed for repair (for future crafting system).
        Returns dict of material_name: quantity
        """
        materials = {}
        
        if item_type.lower() == "weapon":
            if condition_improvement > 20:
                materials["iron_ingot"] = 1
            if condition_improvement > 50:
                materials["steel_ingot"] = 1
        elif item_type.lower() == "armor":
            if condition_improvement > 20:
                materials["leather_strips"] = 2
            if condition_improvement > 50:
                materials["metal_plates"] = 1
        
        # Always need basic repair supplies
        materials["repair_kit"] = 1
        
        return materials
    
    def get_condition_description(self, condition: ItemCondition) -> str:
        """Get descriptive text for item condition"""
        descriptions = {
            ItemCondition.PERFECT: "This item is in perfect condition, unmarked and pristine.",
            ItemCondition.EXCELLENT: "This item shows barely any wear and is in excellent shape.",
            ItemCondition.GOOD: "This item has some minor wear but is still in good condition.",
            ItemCondition.FAIR: "This item shows moderate wear but remains functional.",
            ItemCondition.POOR: "This item is heavily worn and showing signs of age.",
            ItemCondition.DAMAGED: "This item is badly damaged and barely functional.",
            ItemCondition.BROKEN: "This item is completely broken and cannot be used."
        }
        return descriptions[condition]