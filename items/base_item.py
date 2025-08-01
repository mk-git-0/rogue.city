from enum import Enum
from typing import Dict, Any, Optional, List
import json

class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    ACCESSORY = "accessory"

class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class BaseItem:
    def __init__(self, item_id: str, name: str, description: str, item_type: ItemType, 
                 weight: float = 0.0, value: int = 0, rarity: ItemRarity = ItemRarity.COMMON):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.item_type = item_type
        self.weight = weight
        self.value = value
        self.rarity = rarity
        
        # Class restrictions (empty list means no restrictions)
        self.class_restrictions: List[str] = []
        
        # Level requirements
        self.level_requirement: int = 1
        
        # Stat bonuses provided by this item when equipped
        self.stat_bonuses: Dict[str, int] = {
            'strength': 0,
            'dexterity': 0,
            'constitution': 0,
            'intelligence': 0,
            'wisdom': 0,
            'charisma': 0
        }
    
    def can_be_used_by_class(self, character_class: str) -> bool:
        """Check if this item can be used by the given character class."""
        if not self.class_restrictions:
            return True
        return character_class.lower() in [cls.lower() for cls in self.class_restrictions]
    
    def can_be_used_by_level(self, character_level: int) -> bool:
        """Check if this item can be used by the given character level."""
        return character_level >= self.level_requirement
    
    def get_tooltip_text(self) -> str:
        """Generate tooltip text showing item details."""
        lines = []
        lines.append(f"=== {self.name.upper()} ===")
        lines.append(f"Type: {self.item_type.value.title()}")
        lines.append(f"Weight: {self.weight} lbs")
        lines.append(f"Value: {self.value} gold")
        lines.append(f"Rarity: {self.rarity.value.title()}")
        
        if self.level_requirement > 1:
            lines.append(f"Level Required: {self.level_requirement}")
        
        if self.class_restrictions:
            lines.append(f"Classes: {', '.join(self.class_restrictions)}")
        
        # Show stat bonuses if any
        bonuses = [f"{stat.title()}: +{bonus}" for stat, bonus in self.stat_bonuses.items() if bonus > 0]
        if bonuses:
            lines.append("Stat Bonuses:")
            for bonus in bonuses:
                lines.append(f"  {bonus}")
        
        lines.append("")
        lines.append(self.description)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for serialization."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type.value,
            'weight': self.weight,
            'value': self.value,
            'rarity': self.rarity.value,
            'class_restrictions': self.class_restrictions,
            'level_requirement': self.level_requirement,
            'stat_bonuses': self.stat_bonuses
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseItem':
        """Create item from dictionary data."""
        item = cls(
            item_id=data['item_id'],
            name=data['name'],
            description=data['description'],
            item_type=ItemType(data['item_type']),
            weight=data.get('weight', 0.0),
            value=data.get('value', 0),
            rarity=ItemRarity(data.get('rarity', 'common'))
        )
        
        item.class_restrictions = data.get('class_restrictions', [])
        item.level_requirement = data.get('level_requirement', 1)
        item.stat_bonuses = data.get('stat_bonuses', {
            'strength': 0, 'dexterity': 0, 'constitution': 0,
            'intelligence': 0, 'wisdom': 0, 'charisma': 0
        })
        
        return item

class InventoryItem:
    """Wrapper for items in inventory with quantity and equipped status."""
    
    def __init__(self, item: BaseItem, quantity: int = 1, equipped: bool = False):
        self.item = item
        self.quantity = quantity
        self.equipped = equipped
    
    def get_total_weight(self) -> float:
        """Get total weight of all items of this type."""
        return self.item.weight * self.quantity
    
    def get_display_name(self) -> str:
        """Get display name with quantity if > 1."""
        if self.quantity > 1:
            return f"{self.item.name} x{self.quantity}"
        return self.item.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'item': self.item.to_dict(),
            'quantity': self.quantity,
            'equipped': self.equipped
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryItem':
        """Create from dictionary data."""
        item = BaseItem.from_dict(data['item'])
        return cls(
            item=item,
            quantity=data.get('quantity', 1),
            equipped=data.get('equipped', False)
        )